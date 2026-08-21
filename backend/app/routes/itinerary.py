"""
itinerary.py — API URLs for the itinerary feature.

Simple job: receive browser requests, check the trip, call the builder, save/load results.

Who calls this:
  ItineraryPage.jsx → client.js (itineraryApi) → THIS FILE

What this file calls:
  trip_helpers.get_user_trip  → load the user's trip safely
  ai_service.generate_itinerary → make the day plan + times
  GeneratedItinerary model → save / load JSON in the database
  pdf_service → make PDF for Export page
"""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
from io import BytesIO

from app import db
from app.models.generated_itinerary import GeneratedItinerary
from app.services.ai_service import generate_itinerary
from app.services.trip_plan_service import accommodations_list
from app.services.pdf_service import render_itinerary_pdf
from app.utils.trip_helpers import get_user_trip

# itinerary_bp = Flask blueprint object (group of related URLs)
itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    """
    What it does: builds a new itinerary (or rebuilds after user changes day start).

    Incoming JSON body:
      trip_id   — which trip
      day_start — optional time like "08:30 AM", or empty = Auto by mood

    Needs already saved: attractions, hotels, budget.
    Saves result into generated_itinerary table.
    """
    data = request.get_json() or {}
    trip_id = data.get("trip_id")
    if not trip_id:
        return jsonify({"error": "trip_id is required"}), 400

    # trip = UserTripInput object for this logged-in user only
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    if not trip.finalized_attractions:
        return jsonify({"error": "No attractions selected"}), 400
    if not accommodations_list(trip):
        return jsonify({"error": "Select hotels for each destination before generating itinerary"}), 400
    if not trip.budget_split:
        return jsonify({"error": "Budget split required"}), 400

    # delete old itinerary rows for this trip (rebuild clean)
    existing = (
        GeneratedItinerary.query.filter_by(trip_id=trip.trip_id)
        .order_by(GeneratedItinerary.created_at.desc())
        .all()
    )
    for old in existing:
        db.session.delete(old)

    day_start = data.get("day_start") or data.get("preferred_day_start")

    try:
        # itinerary_data = big dict with days, times, hotels (from rules, not OpenAI)
        itinerary_data = generate_itinerary(trip, day_start=day_start)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

    # record = one database row holding that JSON
    record = GeneratedItinerary(trip_id=trip.trip_id, itinerary=itinerary_data)
    db.session.add(record)
    trip.status = "in_progress"
    db.session.commit()

    return jsonify({"itinerary": record.to_dict()}), 201


@itinerary_bp.route("/history", methods=["GET"])
@jwt_required()
def itinerary_history():
    """
    What it does: lists past itineraries for the logged-in user.
    Used by: History page.
    """
    from app.models.user_trip_input import UserTripInput
    from app.utils.trip_helpers import get_current_user_id

    user_id = get_current_user_id()
    trips = (
        UserTripInput.query.filter_by(user_id=user_id)
        .order_by(UserTripInput.updated_at.desc(), UserTripInput.created_at.desc())
        .all()
    )
    items = []
    for trip in trips:
        record = (
            GeneratedItinerary.query.filter_by(trip_id=trip.trip_id)
            .order_by(GeneratedItinerary.created_at.desc())
            .first()
        )
        if not record:
            continue
        payload = record.itinerary or {}  # the saved JSON dict
        items.append(
            {
                "id": record.id,
                "trip_id": str(trip.trip_id),
                "title": payload.get("title") or f"{trip.days}-Day Trip",
                "route": payload.get("route"),
                "summary": payload.get("summary"),
                "day_start": payload.get("day_start"),
                "days": trip.days,
                "selected_moods": trip.selected_moods or [],
                "status": trip.status,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "updated_at": trip.updated_at.isoformat() if trip.updated_at else None,
            }
        )

    return jsonify({"history": items, "count": len(items)})


@itinerary_bp.route("/<trip_id>", methods=["GET"])
@jwt_required()
def get_itinerary(trip_id):
    """
    What it does: loads the latest saved itinerary for one trip.
    Used by: Itinerary page when opening an existing plan.
    """
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    record = (
        GeneratedItinerary.query.filter_by(trip_id=trip.trip_id)
        .order_by(GeneratedItinerary.created_at.desc())
        .first()
    )
    if not record:
        return jsonify({"error": "Itinerary not generated yet"}), 404

    return jsonify({"itinerary": record.to_dict()})


@itinerary_bp.route("/<trip_id>/pdf", methods=["GET"])
@jwt_required()
def export_pdf(trip_id):
    """
    What it does: downloads the itinerary as a PDF file.
    Used by: Export page.
    """
    trip = get_user_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    record = (
        GeneratedItinerary.query.filter_by(trip_id=trip.trip_id)
        .order_by(GeneratedItinerary.created_at.desc())
        .first()
    )
    if not record:
        return jsonify({"error": "Itinerary not generated yet"}), 404

    try:
        pdf_bytes = render_itinerary_pdf(trip, record.itinerary)
    except Exception as exc:
        return jsonify({"error": f"PDF generation failed: {exc}"}), 500

    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    filename = f"itinerary-{trip_id[:8]}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
