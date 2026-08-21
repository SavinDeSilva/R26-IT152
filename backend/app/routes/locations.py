from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.sos_models import Incident, LocationPing

locations_bp = Blueprint("locations", __name__, url_prefix="/api/incidents")


@locations_bp.post("/<int:incident_id>/ping")
def post_ping(incident_id: int):
    """
    Legacy live-ping endpoint — disabled.

    SOS now captures current location once at trigger time only.
    Continuous device tracking is not used.
    """
    incident = Incident.query.get_or_404(incident_id)
    return (
        jsonify(
            {
                "error": "Continuous location tracking is disabled. "
                "Only the location captured when SOS was triggered is stored.",
                "tracking_active": False,
                "incident_id": incident.id,
            }
        ),
        409,
    )


@locations_bp.get("/<int:incident_id>/pings")
def list_pings(incident_id: int):
    """Public-ish poll endpoint for tourist app status; police use JWT incident detail."""
    incident = Incident.query.get_or_404(incident_id)
    since_id = request.args.get("since_id", type=int)
    q = LocationPing.query.filter_by(incident_id=incident_id)
    if since_id:
        q = q.filter(LocationPing.id > since_id)
    pings = q.order_by(LocationPing.recorded_at.asc()).all()
    return jsonify(
        {
            "pings": [p.to_dict() for p in pings],
            "status": incident.status,
            "tracking_active": incident.tracking_active,
        }
    )
