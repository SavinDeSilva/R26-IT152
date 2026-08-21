from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models.attraction import Attraction
from app.models.accommodation import Accommodation
from app.models.user_trip_input import UserTripInput
from app.services.room_type_service import VALID_ROOM_TYPES, normalize_room_type
from app.services.trip_plan_service import (
    get_day_plan,
    ordered_attractions,
    trip_destinations,
    unique_destinations,
    unique_destinations_from_attractions,
    validate_accommodation_picks,
)
from app.utils.trip_helpers import get_current_user_id, get_user_trip

trip_input_bp = Blueprint("trip_input", __name__)


@trip_input_bp.route("/trip-input", methods=["GET"])
@jwt_required()
def list_trip_inputs():
    """Itinerary / trip history for the logged-in user."""
    user_id = get_current_user_id()
    trips = (
        UserTripInput.query.filter_by(user_id=user_id)
        .order_by(UserTripInput.updated_at.desc(), UserTripInput.created_at.desc())
        .all()
    )
    return jsonify({"trips": [t.to_dict() for t in trips]})


def _parse_destination_picks(data: dict) -> dict[str, int]:
    """Accept {destinations: {Gampaha: 12}} or {Gampaha: {id: 12, name: ...}}."""
    if "accommodations_by_destination" in data:
        raw = data["accommodations_by_destination"] or {}
        picks: dict[str, int] = {}
        for dest, value in raw.items():
            if isinstance(value, dict):
                hid = value.get("id") or value.get("accommodation_id")
            else:
                hid = value
            if hid is not None:
                picks[str(dest)] = int(hid)
        return picks

    if "accommodations" in data:
        picks: dict[str, int] = {}
        for entry in data["accommodations"] or []:
            dest = entry.get("destination")
            hid = entry.get("accommodation_id") or entry.get("id")
            if dest and hid is not None:
                picks[str(dest)] = int(hid)
        return picks

    if data.get("accommodation"):
        return {"__legacy_name__": str(data["accommodation"])}

    return {}


@trip_input_bp.route("/trip-input", methods=["POST"])
@jwt_required()
def create_trip_input():
    data = request.get_json() or {}
    user_id = get_current_user_id()

    raw_days = data.get("days")
    selected_moods = data.get("selected_moods") or []
    raw_attractions = data.get("finalized_attractions") or []

    try:
        days = int(raw_days)
    except (TypeError, ValueError):
        return jsonify({"error": "days must be a positive integer"}), 400
    if days <= 0:
        return jsonify({"error": "days must be a positive integer"}), 400

    if not isinstance(selected_moods, list) or not (1 <= len(selected_moods) <= 3):
        return jsonify({"error": "selected_moods must contain 1 to 3 mood values"}), 400
    if not isinstance(raw_attractions, list) or not raw_attractions:
        return jsonify({"error": "finalized_attractions must be a non-empty list"}), 400

    try:
        finalized_attractions = [int(aid) for aid in raw_attractions]
    except (TypeError, ValueError):
        return jsonify({"error": "finalized_attractions must be a list of attraction IDs"}), 400

    selected_rows = ordered_attractions(
        UserTripInput(finalized_attractions=finalized_attractions, days=days, user_id=0)
    )
    found_ids = {a.id for a in selected_rows}
    missing = [aid for aid in finalized_attractions if aid not in found_ids]
    if missing:
        return jsonify({"error": "Some attraction IDs were not found", "invalid_ids": missing}), 400

    # Prefer moods of chosen attractions, then fill with UI mood picks (max 3 stored)
    attraction_moods = [
        (a.mood_tag or "").strip()
        for a in selected_rows
        if (a.mood_tag or "").strip()
    ]
    ui_moods = [str(m).strip() for m in selected_moods if str(m).strip()]
    selected_moods = list(dict.fromkeys([*attraction_moods, *ui_moods]))[:3]
    if not selected_moods:
        return jsonify({"error": "selected_moods must contain 1 to 3 mood values"}), 400

    mood_attractions = Attraction.query.filter(Attraction.mood_tag.in_(selected_moods)).all()
    mood_ids = [a.id for a in mood_attractions]

    location_list = unique_destinations_from_attractions(selected_rows)
    location_count = len(location_list)

    if location_count < 1:
        return jsonify({"error": "Select at least one attraction"}), 400
    if location_count > days:
        return jsonify(
            {
                "error": (
                    f"A {days}-day trip allows at most {days} different location(s). "
                    f"You selected {location_count}: {', '.join(location_list)}"
                ),
                "days": days,
                "location_count": location_count,
                "locations": location_list,
                "rule": "unique_locations <= days",
            }
        ), 400

    trip = UserTripInput(
        user_id=user_id,
        selected_moods=selected_moods,
        days=days,
        attractions_by_mood=mood_ids,
        attractions_by_days=finalized_attractions,
        finalized_attractions=finalized_attractions,
        status="in_progress",
    )
    db.session.add(trip)
    db.session.commit()

    day_plan = get_day_plan(trip)
    return jsonify(
        {
            "trip": trip.to_dict(),
            "day_plan": day_plan,
            "rules": {
                "min_locations": 1,
                "max_locations": days,
                "location_count": location_count,
                "max_hotels": len(trip_destinations(trip)),
            },
        }
    ), 201


@trip_input_bp.route("/trip-input/<trip_id>", methods=["GET"])
@jwt_required()
def get_trip_input(trip_id):
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    day_plan = get_day_plan(trip)
    return jsonify(
        {
            "trip": trip.to_dict(),
            "day_plan": day_plan,
            "rules": {
                "min_locations": 1,
                "max_locations": trip.days,
                "max_hotels": len(trip_destinations(trip)),
            },
        }
    )


@trip_input_bp.route("/trip-input/<trip_id>", methods=["PATCH"])
@jwt_required()
def update_trip_input(trip_id):
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json() or {}
    day_plan = get_day_plan(trip)

    if "accommodations_by_destination" in data or "accommodations" in data or "accommodation" in data:
        picks = _parse_destination_picks(data)

        if "__legacy_name__" in picks:
            dests = unique_destinations(day_plan)
            if len(dests) != 1:
                return jsonify(
                    {
                        "error": "Multiple destinations require one hotel per destination",
                        "destinations": dests,
                    }
                ), 400
            legacy_name = picks["__legacy_name__"]
            hotel = Accommodation.query.filter_by(name=legacy_name).first()
            if not hotel:
                return jsonify({"error": f"Hotel not found: {legacy_name}"}), 404
            picks = {dests[0]: hotel.id}

        valid, err, expanded = validate_accommodation_picks(trip, picks)
        if not valid:
            return jsonify({"error": err}), 400

        trip.accommodations = expanded
        trip.accommodation = expanded[0]["name"] if expanded else None

    if "budget" in data and data["budget"] is not None:
        trip.budget = data["budget"]

    if "room_type" in data:
        room_type = normalize_room_type(data.get("room_type"))
        if room_type not in VALID_ROOM_TYPES:
            return jsonify({"error": "room_type must be single, double, or family"}), 400
        trip.room_type = room_type

    if "status" in data and data["status"] in ("draft", "in_progress", "completed"):
        trip.status = data["status"]

    db.session.commit()
    return jsonify({"trip": trip.to_dict(), "accommodations": trip.accommodations})
