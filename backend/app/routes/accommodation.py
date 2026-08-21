from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.budget_service import accommodation_budget_per_night
from app.services.room_type_service import (
    enrich_accommodation,
    normalize_room_type,
    room_type_label,
    room_types_for_api,
)
from app.services.trip_plan_service import (
    get_day_plan,
    hotels_for_destination,
    ordered_attractions,
    trip_destinations,
)
from app.utils.trip_helpers import get_user_trip

accommodation_bp = Blueprint("accommodation", __name__)


@accommodation_bp.route("/accommodation", methods=["GET"])
@jwt_required()
def list_accommodation():
    trip_id = request.args.get("trip_id")
    if not trip_id:
        return jsonify({"error": "trip_id query parameter is required"}), 400

    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    if not trip.budget_split:
        return jsonify({"error": "Budget split required before accommodation search"}), 400

    room_type = normalize_room_type(request.args.get("room_type") or trip.room_type)

    lkr_rate = current_app.config.get("LKR_TO_USD_RATE", 300)
    accommodation_budget_usd = float(trip.budget_split.accommodation)
    per_night_usd = accommodation_budget_per_night(accommodation_budget_usd, trip.days)
    per_night_lkr = per_night_usd * lkr_rate

    day_plan = get_day_plan(trip)
    if len(day_plan) != trip.days:
        return jsonify(
            {
                "error": f"Select at least {trip.days} places for your {trip.days}-day trip",
                "days": trip.days,
                "places_in_plan": len(day_plan),
            }
        ), 400

    dests = trip_destinations(trip)
    stops_by_destination = []

    for dest in dests:
        sample_attr = next(a for a in ordered_attractions(trip) if a.destination == dest)
        hotels = hotels_for_destination(
            dest,
            sample_attr.normalized_destination,
            per_night_lkr,
            room_type=room_type,
        )
        days_at_dest = [e["day"] for e in day_plan if e["destination"] == dest]
        attractions = [
            {
                "attraction_id": a.id,
                "attraction_name": a.attraction_name,
            }
            for a in ordered_attractions(trip)
            if a.destination == dest
        ]
        stops_by_destination.append(
            {
                "destination": dest,
                "days": days_at_dest,
                "attractions": attractions,
                "hotels": [enrich_accommodation(h, room_type) for h in hotels],
                "hotel_count": len(hotels),
            }
        )

    return jsonify(
        {
            "day_plan": day_plan,
            "stops_by_destination": stops_by_destination,
            "count": sum(s["hotel_count"] for s in stops_by_destination),
            "rules": {
                "min_places": trip.days,
                "max_hotels": len(dests),
                "required_hotels": len(dests),
                "message": (
                    f"Choose 1 hotel per destination (max {len(dests)} hotels "
                    f"for {len(dests)} place(s) across {trip.days} day(s))"
                ),
            },
            "filters": {
                "accommodation_budget_usd": accommodation_budget_usd,
                "per_night_usd": round(per_night_usd, 2),
                "per_night_lkr": round(per_night_lkr, 2),
                "destinations": dests,
                "room_type": room_type,
                "room_type_label": room_type_label(room_type),
                "room_types": room_types_for_api(),
                "pricing_rule": "Single=A, Double=(A+B)/2, Family=B (from hotel price range)",
            },
        }
    )
