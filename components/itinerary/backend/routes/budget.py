from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from components.itinerary.backend.models.budget_split import BudgetSplit
from components.itinerary.backend.services.budget_service import (
    calculate_amounts,
    percentages_for_request,
    validate_percentages,
)
from components.itinerary.backend.utils.trip_helpers import get_user_trip

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/split", methods=["POST"])
@jwt_required()
def create_budget_split():
    data = request.get_json() or {}
    trip_id = data.get("trip_id")
    total_budget = data.get("budget")
    use_custom = data.get("customize", False)

    if not trip_id:
        return jsonify({"error": "trip_id is required"}), 400
    if total_budget is None or float(total_budget) <= 0:
        return jsonify({"error": "budget must be a positive number"}), 400

    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    total_budget = float(total_budget)
    trip.budget = total_budget

    include_guide = bool(data.get("include_guide"))
    percentages = percentages_for_request(data, use_custom)

    valid, err = validate_percentages(percentages)
    if not valid:
        return jsonify({"error": err}), 400

    amounts = calculate_amounts(total_budget, percentages)

    split = trip.budget_split
    if not split:
        split = BudgetSplit(trip_id=trip.trip_id)
        db.session.add(split)

    split.food = amounts["food"]
    split.accommodation = amounts["accommodation"]
    split.shopping = amounts["shopping"]
    split.transport = amounts["transport"]
    split.guide = amounts["guide"]
    split.food_pct = percentages["food_pct"]
    split.accommodation_pct = percentages["accommodation_pct"]
    split.shopping_pct = percentages["shopping_pct"]
    split.transport_pct = percentages["transport_pct"]
    split.guide_pct = percentages["guide_pct"]
    split.include_guide = include_guide

    db.session.commit()

    return jsonify(
        {
            "trip_id": str(trip.trip_id),
            "budget": total_budget,
            "split": split.to_dict(),
            "daily_estimate": round(total_budget / trip.days, 2),
        }
    )


@budget_bp.route("/split/<trip_id>", methods=["GET"])
@jwt_required()
def get_budget_split(trip_id):
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    if not trip.budget_split:
        return jsonify({"error": "Budget split not found"}), 404
    return jsonify({"split": trip.budget_split.to_dict(), "budget": float(trip.budget or 0)})
