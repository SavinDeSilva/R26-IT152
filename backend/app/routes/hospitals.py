"""Nearest-hospital lookup for tourist-initiated dialer (tel:)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.sos_models import Hospital
from app.services.routing import nearest_entity

hospitals_bp = Blueprint("hospitals", __name__, url_prefix="/api/hospitals")


@hospitals_bp.get("/nearest")
def nearest_hospital():
    """
    Find nearest hospital with coordinates + phone for tel: dialer.
    Query: lat / latitude, lng / longitude
    """
    lat = request.args.get("lat", type=float)
    if lat is None:
        lat = request.args.get("latitude", type=float)
    lng = request.args.get("lng", type=float)
    if lng is None:
        lng = request.args.get("longitude", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400

    hospitals = Hospital.query.filter(
        Hospital.latitude.isnot(None),
        Hospital.longitude.isnot(None),
        Hospital.is_hotline_only.is_(False),
    ).all()
    hospital, dist = nearest_entity(lat, lng, hospitals)
    if not hospital:
        # Fall back to hotlines with a phone number if no geo match
        hotline = (
            Hospital.query.filter(Hospital.local_number.isnot(None))
            .order_by(Hospital.id.asc())
            .first()
        )
        if not hotline:
            return jsonify({"error": "No hospitals available"}), 404
        return jsonify(
            {
                "hospital": hotline.to_dict(),
                "distance_km": None,
                "dial_number": _dial_number(hotline),
            }
        )

    return jsonify(
        {
            "hospital": hospital.to_dict(),
            "distance_km": round(dist, 3) if dist is not None else None,
            "dial_number": _dial_number(hospital),
        }
    )


def _dial_number(hospital: Hospital) -> str | None:
    raw = hospital.local_number or hospital.international_number
    if not raw:
        return None
    digits = "".join(ch for ch in str(raw) if ch.isdigit() or ch == "+")
    return digits or None
