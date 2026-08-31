"""
trip_plan_service.py — helps split the trip into days and match hotels.

Simple job:
  - figure out which city/place goes on which day
  - put all selected attractions onto those days
  - find / check hotels for each city
  - tell ai_service which hotel is for which day

Does NOT make clock times (ai_service does that).
Does NOT use OpenAI.
"""

from __future__ import annotations

import re

from sqlalchemy import or_

from components.itinerary.backend.models.accommodation import Accommodation
from components.itinerary.backend.models.attraction import Attraction
from components.itinerary.backend.models.user_trip_input import UserTripInput


def ordered_attractions(trip: UserTripInput) -> list[Attraction]:
    """
    What it does: loads the places the user picked, in the same order they picked them.
    Returns: list of Attraction objects (database rows).
    """
    attraction_ids = trip.finalized_attractions or []
    if not attraction_ids:
        return []
    rows = Attraction.query.filter(Attraction.id.in_(attraction_ids)).all()
    by_id = {a.id: a for a in rows}  # dict: id → Attraction
    return [by_id[aid] for aid in attraction_ids if aid in by_id]


def unique_destinations_from_attractions(attractions: list[Attraction]) -> list[str]:
    """
    What it does: makes a list of city/area names with no duplicates.
    Example: [Kandy, Kandy, Galle] → [Kandy, Galle]
    """
    seen = []
    for a in attractions:
        dest = a.destination
        if dest and dest not in seen:
            seen.append(dest)
    return seen


def trip_destinations(trip: UserTripInput) -> list[str]:
    """
    What it does: all unique cities in this trip.
    Why: each city needs its own hotel on the Stay page.
    """
    return unique_destinations_from_attractions(ordered_attractions(trip))


def _day_plan_entry(day_num: int, attraction: Attraction) -> dict:
    """
    What it does: makes one small dict for one day (the "lead" place that day).
    This dict is not the full schedule yet — just the day skeleton.
    """
    return {
        "day": day_num,
        "attraction_id": attraction.id,
        "attraction_name": attraction.attraction_name,
        "destination": attraction.destination,
        "normalized_destination": attraction.normalized_destination,
        "mood_tag": attraction.mood_tag,
        "category": attraction.category,
    }


def get_day_plan(trip: UserTripInput) -> list[dict]:
    """
    What it does: builds one entry per trip day (length = trip.days).

    How days are split:
      1) Group consecutive days per destination — stay in one city before moving on.
      2) Split total days as evenly as possible across cities (extra days go to later stops).
      3) Never bounce back to a city once the trip has moved on.

    Example (7 days, Colombo → Batticaloa → Hambantota):
      Days 1–2 Colombo, 3–4 Batticaloa, 5–7 Hambantota — not alternating every day.
    Returns: list of day dicts.
    """
    attractions = ordered_attractions(trip)
    if not attractions:
        return []

    days = trip.days
    plan: list[dict] = []

    # by_dest = dict: city name → list of Attraction in that city
    by_dest: dict[str, list[Attraction]] = {}
    dest_order: list[str] = []
    for attraction in attractions:
        dest = attraction.destination
        if not dest:
            continue
        if dest not in by_dest:
            by_dest[dest] = []
            dest_order.append(dest)
        by_dest[dest].append(attraction)

    if not dest_order:
        return []

    num_dests = len(dest_order)
    base_days = days // num_dests
    extra_days = days % num_dests

    day_num = 1
    for i, dest in enumerate(dest_order):
        # Later destinations receive any leftover days so the route moves forward only once.
        block_size = base_days + (1 if i >= num_dests - extra_days else 0)
        if block_size <= 0:
            continue
        lead = by_dest[dest][0]
        for _ in range(block_size):
            plan.append(_day_plan_entry(day_num, lead))
            day_num += 1

    return plan


def attractions_grouped_by_day(trip: UserTripInput) -> dict[int, list[Attraction]]:
    """
    What it does: puts EVERY selected place onto a day number.

    Rules:
      - city has 1 day → all its places go on that day
      - city has many days → share places across those days
    Returns: dict like {1: [placeA, placeB], 2: [placeC]}
    """
    day_plan = get_day_plan(trip)
    by_day: dict[int, list[Attraction]] = {entry["day"]: [] for entry in day_plan}

    for dest in trip_destinations(trip):
        dest_days = sorted(entry["day"] for entry in day_plan if entry["destination"] == dest)
        dest_attrs = [a for a in ordered_attractions(trip) if a.destination == dest]
        if not dest_days or not dest_attrs:
            continue
        if len(dest_days) == 1:
            by_day[dest_days[0]] = dest_attrs
        else:
            # Spread places across consecutive days at this destination (at most one slot per day).
            for index, attraction in enumerate(dest_attrs):
                if index < len(dest_days):
                    by_day[dest_days[index]].append(attraction)
                else:
                    # More attractions than days — pair extras on the last day of the block.
                    by_day[dest_days[-1]].append(attraction)

    return by_day


def unique_destinations(day_plan: list[dict]) -> list[str]:
    """What it does: city names in the order they appear in the day plan."""
    seen = []
    for entry in day_plan:
        dest = entry.get("destination")
        if dest and dest not in seen:
            seen.append(dest)
    return seen


def _strip_suffix(value: str) -> str:
    """
    What it does: cleans long place names.
    Example: "Kandy Municipal Council" → "Kandy"
    """
    return re.sub(
        r"\s+(Pradeshiya Sabha|Urban Council|Municipal Council|Muncipal Council)$",
        "",
        value.strip(),
        flags=re.IGNORECASE,
    )


def destination_tokens(destination: str, normalized: str | None = None) -> list[str]:
    """
    What it does: makes search words for matching hotels to a city.
    Returns: city/area names only — never street fragments from an address.
    """
    raw = [destination, normalized, _strip_suffix(destination or ""), _strip_suffix(normalized or "")]
    expanded: list[str] = []
    for val in raw:
        if not val:
            continue
        text = val.strip()
        expanded.append(text)
        expanded.extend(part.strip() for part in re.findall(r"\(([^)]+)\)", text))
        without_paren = re.sub(r"\s*\([^)]*\)\s*", " ", text).strip()
        if without_paren:
            expanded.append(without_paren)

    tokens: list[str] = []
    seen: set[str] = set()
    for val in expanded:
        key = val.strip().lower()
        if len(key) < 3 or key in seen:
            continue
        seen.add(key)
        tokens.append(val.strip())
    return tokens


def _contains_place_token(text: str | None, token: str) -> bool:
    """True when token is a whole place word in text (not 'Colombo' inside 'Colombo Road' on another city)."""
    if not text or not token:
        return False
    return (
        re.search(
            rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])",
            text,
            flags=re.IGNORECASE,
        )
        is not None
    )


def hotel_matches_destination(
    hotel: Accommodation, destination: str, normalized: str | None = None
) -> bool:
    """
    What it does: checks if this hotel belongs to that city.
    How: matches city words against local authority only — never the street address.
    """
    tokens = destination_tokens(destination, normalized)
    fields = [
        hotel.normalized_local_authority,
        hotel.local_authority,
        _strip_suffix(hotel.normalized_local_authority or ""),
        _strip_suffix(hotel.local_authority or ""),
    ]
    for field in fields:
        for token in tokens:
            if _contains_place_token(field, token):
                return True
    return False


def destination_filter_clause(destination: str, normalized: str | None = None):
    """
    What it does: builds a database filter so we only load hotels for that city.
    Matches local authority / city, not street addresses such as "Colombo Road".
    Returns: SQLAlchemy OR clause (used inside hotels_for_destination).
    """
    tokens = destination_tokens(destination, normalized)
    clauses = []
    for token in tokens:
        clauses.append(Accommodation.normalized_local_authority.ilike(f"%{token}%"))
        clauses.append(Accommodation.local_authority.ilike(f"%{token}%"))
    return or_(*clauses) if clauses else None


def hotels_for_destination(
    destination: str,
    normalized: str | None,
    per_night_lkr: float,
    limit: int = 50,
    room_type: str = "double",
    query: str | None = None,
) -> list[Accommodation]:
    """
    What it does: list hotels for one city that fit the stay budget.
    Room type picks the effective nightly rate from the hotel's A–B range.
    Optional query matches hotel name, address, or local authority.
    """
    from components.itinerary.backend.services.room_type_service import room_nightly_rate

    location_clause = destination_filter_clause(destination, normalized)
    if location_clause is None:
        return []

    filters = [
        Accommodation.price_min.isnot(None),
        Accommodation.price_max.isnot(None),
        location_clause,
    ]
    q = (query or "").strip()
    if q:
        like = f"%{q}%"
        filters.append(
            or_(
                Accommodation.name.ilike(like),
                Accommodation.address.ilike(like),
                Accommodation.local_authority.ilike(like),
                Accommodation.normalized_local_authority.ilike(like),
                Accommodation.category.ilike(like),
            )
        )

    candidates = (
        Accommodation.query.filter(*filters)
        .order_by(Accommodation.name)
        .limit(200 if q else max(limit * 4, 100))
        .all()
    )

    matched: list[Accommodation] = []
    for hotel in candidates:
        if not hotel_matches_destination(hotel, destination, normalized):
            continue
        nightly = room_nightly_rate(hotel.price_min, hotel.price_max, room_type)
        if nightly is not None and nightly <= per_night_lkr:
            matched.append(hotel)
        if len(matched) >= limit:
            break
    return matched


def hotels_matching_query(
    query: str,
    per_night_lkr: float | None = None,
    room_type: str = "double",
    limit: int = 40,
) -> list[Accommodation]:
    """Find hotels by name, address, or city when the user types a stay search."""
    from components.itinerary.backend.services.room_type_service import room_nightly_rate

    q = (query or "").strip()
    if not q:
        return []

    like = f"%{q}%"
    candidates = (
        Accommodation.query.filter(
            or_(
                Accommodation.name.ilike(like),
                Accommodation.address.ilike(like),
                Accommodation.local_authority.ilike(like),
                Accommodation.normalized_local_authority.ilike(like),
                Accommodation.category.ilike(like),
            ),
        )
        .order_by(Accommodation.name)
        .limit(max(limit * 3, 80))
        .all()
    )

    matched: list[Accommodation] = []
    for hotel in candidates:
        nightly = room_nightly_rate(hotel.price_min, hotel.price_max, room_type)
        if per_night_lkr is not None:
            if nightly is None or nightly > per_night_lkr:
                continue
        matched.append(hotel)
        if len(matched) >= limit:
            break
    return matched


def expand_destination_picks(
    day_plan: list[dict],
    picks_by_destination: dict[str, int],
    room_types_by_destination: dict[str, str] | None = None,
) -> list[dict]:
    """
    What it does: turns {city: hotel_id} into a list of hotel rows, one per day.
    picks_by_destination = dict like {"Kandy": 12, "Galle": 45}
    Returns: list of small dicts saved on the trip.
    """
    from components.itinerary.backend.services.room_type_service import normalize_room_type

    room_types_by_destination = room_types_by_destination or {}
    expanded = []
    for entry in day_plan:
        dest = entry["destination"]
        hotel_id = picks_by_destination.get(dest)
        if not hotel_id:
            continue
        hotel = Accommodation.query.get(hotel_id)
        dest_type = room_types_by_destination.get(dest)
        row = {
            "day": entry["day"],
            "attraction_id": entry["attraction_id"],
            "destination": dest,
            "accommodation_id": hotel_id,
            "name": hotel.name if hotel else None,
        }
        if dest_type:
            row["room_type"] = normalize_room_type(dest_type)
        expanded.append(row)
    return expanded


def validate_accommodation_picks(
    trip: UserTripInput,
    picks_by_destination: dict[str, int],
    room_types_by_destination: dict[str, str] | None = None,
) -> tuple[bool, str | None, list[dict]]:
    """
    What it does: checks hotel choices before saving (Stay page confirm).

    Checks:
      - every city has a hotel
      - hotel really belongs to that city
    Returns: (ok?, error_message_or_None, expanded_hotel_list)
    """
    day_plan = get_day_plan(trip)
    if len(day_plan) != trip.days:
        return False, "Day plan incomplete — select at least one place per day", []

    dests = trip_destinations(trip)
    if not picks_by_destination:
        return False, "Select at least one hotel", []

    if len(picks_by_destination) > len(dests):
        return (
            False,
            f"You can choose at most {len(dests)} hotel(s) for {len(dests)} destination(s)",
            [],
        )

    for dest in dests:
        if dest not in picks_by_destination or not picks_by_destination[dest]:
            return False, f"Select a hotel for {dest}", []

    for dest, hotel_id in picks_by_destination.items():
        if dest not in dests:
            return False, f"Hotel destination '{dest}' is not in your trip", []
        hotel = Accommodation.query.get(hotel_id)
        if not hotel:
            return False, f"Hotel not found (id={hotel_id})", []
        sample = next(
            (e for e in day_plan if e["destination"] == dest),
            None,
        )
        if sample is None:
            attraction = next(a for a in ordered_attractions(trip) if a.destination == dest)
            normalized = attraction.normalized_destination
        else:
            normalized = sample.get("normalized_destination")
        if not hotel_matches_destination(hotel, dest, normalized):
            return (
                False,
                f"{hotel.name} is not available for {dest}. Choose a hotel listed under {dest}.",
                [],
            )

    expanded = expand_destination_picks(day_plan, picks_by_destination, room_types_by_destination)
    if len(expanded) != trip.days:
        return False, "Could not assign hotels to all days", []

    return True, None, expanded


def accommodations_list(trip: UserTripInput) -> list[dict]:
    """
    What it does: returns the hotels already saved on this trip.
    Returns: list of dicts (day, destination, hotel name, …)
    """
    if trip.accommodations:
        return trip.accommodations
    if trip.accommodation:
        plan = get_day_plan(trip)
        if plan:
            return [
                {
                    "day": entry["day"],
                    "attraction_id": entry["attraction_id"],
                    "destination": entry["destination"],
                    "name": trip.accommodation,
                }
                for entry in plan
            ]
    return []


def hotel_for_day(trip: UserTripInput, day_num: int) -> str | None:
    """
    What it does: finds the hotel name for one day number.
    Used by ai_service when building that day's card.
    """
    for entry in accommodations_list(trip):
        if entry.get("day") == day_num:
            return entry.get("name")
    return None
