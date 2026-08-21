"""
ai_service.py — builds the day-by-day trip times.

IMPORTANT: This does NOT use OpenAI. OPENAI_API_KEY can stay empty.

Simple flow (who calls who):
  1. User opens Itinerary page (ItineraryPage.jsx)
  2. Browser calls API (client.js → itineraryApi)
  3. Server route runs (routes/itinerary.py)
  4. This file makes the times + day list
  5. trip_plan_service.py helps split places by day / find hotels
  6. Result is saved in generated_itinerary table

What we already have from earlier steps (saved on the trip):
  days, moods, attractions, hotels, budget
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from app.models.accommodation import Accommodation
from app.models.attraction import Attraction
from app.models.user_trip_input import UserTripInput
from app.services.trip_plan_service import (
    accommodations_list,
    attractions_grouped_by_day,
    get_day_plan,
    hotel_for_day,
    ordered_attractions,
)

# ---------------------------------------------------------------------------
# MOOD_START_HOURS = dict (lookup table)
# What it does: if user picks "Auto (by mood)", we use these start times.
# Key = mood name (same as frontend). Value = hour (6.5 means 6:30 AM).
# ---------------------------------------------------------------------------
MOOD_START_HOURS = {
    "Spiritual": 6.5,   # start early
    "Adventure": 7.5,
    "Explore": 8.0,
    "Excited": 8.0,
    "Curious": 8.5,
    "Happy": 9.0,
    "Authentic": 9.0,
    "Healing": 9.5,
    "Peaceful": 10.0,
    "Relaxed": 10.5,    # start late / easy morning
}

# ---------------------------------------------------------------------------
# CATEGORY_START_HOURS = dict
# What it does: nudges the FIRST activity time using the place category.
# These names match the Attractions page filters / database.
# ---------------------------------------------------------------------------
CATEGORY_START_HOURS = {
    "Wild": 6.5,       # parks / animals — early
    "Heritage": 7.0,   # temples / history — early
    "Thrills": 7.5,    # adventure
    "Scenic": 8.5,     # views
    "Essence": 9.0,    # local feel
    "Pristine": 9.5,   # beach / calm — later
}

# ---------------------------------------------------------------------------
# NAME_START_HINTS = dict
# What it does: if category did not match, look for words in the place NAME
# (example: name has "beach" → start later).
# ---------------------------------------------------------------------------
NAME_START_HINTS = {
    "safari": 6.0,
    "wildlife": 6.5,
    "temple": 6.5,
    "religious": 6.5,
    "hiking": 7.0,
    "waterfall": 8.0,
    "museum": 10.0,
    "market": 9.0,
    "beach": 9.5,
    "spa": 10.5,
}


def _mood_start_hour(moods: list | None) -> float:
    """
    What it does: looks at the user's moods and returns one start hour.
    How: averages the hours from MOOD_START_HOURS.
    Example: Spiritual (6.5) + Relaxed (10.5) → 8.5
    """
    hours = [MOOD_START_HOURS[m] for m in (moods or []) if m in MOOD_START_HOURS]
    if not hours:
        return 8.5  # default if no moods
    return sum(hours) / len(hours)


def _parse_day_start(value, moods: list | None = None) -> float:
    """
    What it does: decides the day's start hour.

    Rules:
      1) User chose a time on the page (like "08:30 AM") → use that.
      2) User left Auto / empty → use mood average (_mood_start_hour).
    Returns: a number like 8.5 (meaning 8:30).
    """
    if value is None or value == "":
        return _mood_start_hour(moods)

    # Already a number?
    if isinstance(value, (int, float)):
        hour = float(value)
        if 0 <= hour < 24:
            return hour

    # Text like "8:30 AM" → number
    text = str(value).strip().upper()
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?$", text)
    if not match:
        return _mood_start_hour(moods)

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3)
    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return _mood_start_hour(moods)
    return hour + minute / 60.0


def _format_clock(hour_float: float) -> str:
    """
    What it does: turns a number into a clock string for the UI.
    Example: 8.5 → "8:30 AM"
    """
    total_minutes = int(round(hour_float * 60)) % (24 * 60)
    dt = datetime(2000, 1, 1) + timedelta(minutes=total_minutes)
    return dt.strftime("%I:%M %p").lstrip("0")


def _category_bias(attraction) -> float | None:
    """
    What it does: suggests a start hour from the FIRST place of the day.

    Checks in order:
      1) place.category (Wild, Heritage, …)
      2) words inside place name (temple, beach, …)
    Returns: hour number, or None if no match.
    """
    if attraction is None:
        return None

    category = (getattr(attraction, "category", None) or "").strip()
    for label, hour in CATEGORY_START_HOURS.items():
        if category.lower() == label.lower():
            return hour

    name = (getattr(attraction, "attraction_name", None) or "").lower()
    for key, hour in NAME_START_HINTS.items():
        if key in name:
            return hour
    return None


def _build_day_times(count: int, day_start: float, day_attractions: list) -> list[str]:
    """
    What it does: makes a list of clock times for one day.

    Spacing:
      1 place  → only start time
      2 places → about 3 hours apart
      3 places → about 2.5 hours apart
      more     → about 2 hours apart
      if next time falls in lunch (12–1) → move to 1:00 PM
      do not plan after about 8:00 PM

    Example: start 8:00, 3 places → about 8:00, 10:30, 1:00 PM
    Returns: list of strings like ["8:00 AM", "10:30 AM", "1:00 PM"]
    """
    if count <= 0:
        return []

    # Category may push first time later (e.g. beach).
    # We do not start earlier than day_start (user pick or mood).
    first_bias = _category_bias(day_attractions[0]) if day_attractions else None
    start = max(day_start, first_bias) if first_bias is not None else day_start
    start = min(max(start, 5.0), 14.0)  # keep between 5 AM and 2 PM

    if count == 1:
        return [_format_clock(start)]

    # Gap depends on how many places that day
    gap_hours = 3.0 if count == 2 else 2.5 if count == 3 else 2.0
    times = []
    cursor = start
    for _ in range(count):
        times.append(_format_clock(cursor))
        cursor += gap_hours
        if 12.0 <= cursor < 13.0:
            cursor = 13.0  # lunch break
        if cursor >= 20.0:
            cursor = 19.5  # stop late evening slots
    return times


def build_itinerary_from_database(trip: UserTripInput, day_start=None) -> dict:
    """
    What it does: builds the full itinerary object (a big dict / JSON).

    Uses only database data + rules. No AI chat.

    Steps:
      1) get day plan (which city each day)
      2) get hotels
      3) pick start hour
      4) put places on each day with times
      5) return one dict the frontend can show
    """
    # day_plan = list of dicts, one per day (city + lead place)
    day_plan = get_day_plan(trip)
    if not day_plan:
        raise ValueError("Trip day plan is empty")

    # acc_list = list of hotel picks already saved on the trip
    acc_list = accommodations_list(trip)
    if not acc_list:
        raise ValueError("Hotels must be selected before generating itinerary")

    # start_hour = number for first activity (user time OR mood average)
    start_hour = _parse_day_start(day_start, trip.selected_moods)

    # grouped = { day_number: [Attraction, Attraction, ...] }
    grouped = attractions_grouped_by_day(trip)

    # all_attractions = list of Attraction objects user selected
    all_attractions = ordered_attractions(trip)
    attraction_ids = [a.id for a in all_attractions]

    # details_by_id = { attraction_id: description text }
    detail_rows = Attraction.query.filter(Attraction.id.in_(attraction_ids)).all()
    details_by_id = {row.id: row.details or "" for row in detail_rows}

    # hotels_by_name = { hotel_name: Accommodation object }
    hotel_names = {a.get("name") for a in acc_list if a.get("name")}
    hotel_rows = Accommodation.query.filter(Accommodation.name.in_(hotel_names)).all()
    hotels_by_name = {row.name: row for row in hotel_rows}

    # days_out = final list we send to the UI
    days_out = []
    for entry in day_plan:
        day_num = entry["day"]
        hotel_name = hotel_for_day(trip, day_num) or "Not selected"
        hotel_record = hotels_by_name.get(hotel_name)

        # places for this day
        day_attractions = grouped.get(day_num) or []

        # schedule = list of time strings for those places
        activities = []
        schedule = _build_day_times(len(day_attractions), start_hour, day_attractions)
        for index, attraction in enumerate(day_attractions):
            # each activity = one stop on the day (dict)
            activities.append(
                {
                    "time": schedule[index],
                    "title": attraction.attraction_name,
                    "mood_tag": attraction.mood_tag,
                    "category": attraction.category,
                    "description": details_by_id.get(attraction.id, ""),
                    "attraction_id": attraction.id,
                    "destination": attraction.destination,
                }
            )

        # Extra days at the same city with no further places → leisure day, not a repeat visit.
        if not activities:
            destination = entry["destination"]
            activities.append(
                {
                    "time": _format_clock(start_hour),
                    "title": f"Explore {destination}",
                    "mood_tag": entry.get("mood_tag"),
                    "category": "Leisure",
                    "description": (
                        f"Free time in {destination}. Relax, try local food, "
                        "or revisit nearby spots at your own pace."
                    ),
                    "attraction_id": entry["attraction_id"],
                    "destination": destination,
                }
            )

        # one day object for the UI
        days_out.append(
            {
                "day": day_num,
                "title": entry["destination"],
                "location": entry["destination"],
                "normalized_destination": entry.get("normalized_destination"),
                "accommodation": hotel_name,
                "accommodation_local_authority": (
                    hotel_record.local_authority if hotel_record else None
                ),
                "activities": activities,
            }
        )

    # route = text like "Kandy → Galle"
    route = " → ".join(dict.fromkeys(e["destination"] for e in day_plan if e.get("destination")))
    hotel_name_list = list(dict.fromkeys(a.get("name") for a in acc_list if a.get("name")))
    highlights = [a.attraction_name for a in all_attractions]

    summary_parts = [f"Visiting: {', '.join(highlights)}."]
    if hotel_name_list:
        summary_parts.append(f"Stays: {', '.join(hotel_name_list)}.")

    # final itinerary object (dict) — this is what gets saved + shown
    return {
        "title": f"{trip.days}-Day Sri Lanka Trip",
        "summary": " ".join(summary_parts),
        "route": route,
        "highlights": highlights,
        "days": days_out,
        "accommodations": acc_list,
        "tips": [],
        "source": "database",  # means: built from DB rules, not ChatGPT
        "day_start": _format_clock(start_hour),
        "data_sources": {
            "attractions": "attractions.xlsx",
            "accommodation": "accomadation.xlsx",
        },
    }


def generate_itinerary(trip: UserTripInput, day_start=None) -> dict:
    """
    What it does: main function the route calls.
    Just calls build_itinerary_from_database and returns that dict.
    """
    return build_itinerary_from_database(trip, day_start=day_start)
