from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from components.itinerary.backend.models.business_directory import BusinessDirectory
from components.itinerary.backend.models.saved_reference import SavedReference
from components.itinerary.backend.models.tourist_guide import TouristGuide
from components.itinerary.backend.models.travel_agency import TravelAgency
from components.itinerary.backend.utils.trip_helpers import get_current_user_id, get_user_trip

saved_refs_bp = Blueprint("saved_references", __name__)

VALID_REF_TYPES = ("business_directory", "travel_agency", "tourist_guide")


@saved_refs_bp.route("/saved-references", methods=["POST"])
@jwt_required()
def save_reference():
    data = request.get_json() or {}
    trip_id = data.get("trip_id")
    ref_type = data.get("ref_type")
    ref_id = data.get("ref_id")

    if not trip_id or not ref_type or ref_id is None:
        return jsonify({"error": "trip_id, ref_type, and ref_id are required"}), 400
    if ref_type not in VALID_REF_TYPES:
        return jsonify(
            {
                "error": "ref_type must be business_directory, travel_agency, or tourist_guide",
            }
        ), 400

    try:
        ref_id = int(ref_id)
    except (TypeError, ValueError):
        return jsonify({"error": "ref_id must be an integer"}), 400

    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    if ref_type == "business_directory":
        if db.session.get(BusinessDirectory, ref_id) is None:
            return jsonify({"error": "Business not found"}), 404
    elif ref_type == "travel_agency":
        if db.session.get(TravelAgency, ref_id) is None:
            return jsonify({"error": "Travel agency not found"}), 404
    elif db.session.get(TouristGuide, ref_id) is None:
        return jsonify({"error": "Tourist guide not found"}), 404

    existing = SavedReference.query.filter_by(
        trip_id=trip.trip_id, ref_type=ref_type, ref_id=ref_id
    ).first()
    if existing:
        return jsonify({"saved_reference": existing.to_dict()}), 200

    saved = SavedReference(
        trip_id=trip.trip_id,
        user_id=get_current_user_id(),
        ref_type=ref_type,
        ref_id=ref_id,
    )
    try:
        db.session.add(saved)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": f"Failed to save reference: {exc}"}), 500

    return jsonify({"saved_reference": saved.to_dict()}), 201


@saved_refs_bp.route("/saved-references", methods=["GET"])
@jwt_required()
def list_saved_references():
    trip_id = request.args.get("trip_id")
    if not trip_id:
        return jsonify({"error": "trip_id is required"}), 400

    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    refs = SavedReference.query.filter_by(trip_id=trip.trip_id).all()
    return jsonify({"saved_references": [r.to_dict() for r in refs], "count": len(refs)})
