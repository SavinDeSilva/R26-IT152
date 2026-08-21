"""Manual re-trigger endpoints (contact/hotel auto-notify on SOS create)."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required

from app import db
from app.sos_models import Incident
from app.services.notify import notify_emergency_contact, notify_hotel

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


def _scoped_incident(incident_id: int):
    incident = Incident.query.get_or_404(incident_id)
    station_id = get_jwt().get("station_id")
    if station_id and incident.station_id != int(station_id):
        return None, (jsonify({"error": "Forbidden"}), 403)
    return incident, None


@notifications_bp.post("/incidents/<int:incident_id>/contact")
@jwt_required()
def re_notify_contact(incident_id: int):
    incident, err = _scoped_incident(incident_id)
    if err:
        return err
    ok = notify_emergency_contact(incident)
    if ok:
        incident.contact_notified_at = datetime.utcnow()
        db.session.commit()
    return jsonify(
        {
            "ok": ok,
            "contact_notified_at": incident.contact_notified_at.isoformat()
            if incident.contact_notified_at
            else None,
        }
    )


@notifications_bp.post("/incidents/<int:incident_id>/hotel")
@jwt_required()
def re_notify_hotel(incident_id: int):
    incident, err = _scoped_incident(incident_id)
    if err:
        return err
    ok = notify_hotel(incident)
    if ok:
        incident.hotel_notified_at = datetime.utcnow()
        db.session.commit()
    return jsonify(
        {
            "ok": ok,
            "hotel_notified_at": incident.hotel_notified_at.isoformat()
            if incident.hotel_notified_at
            else None,
        }
    )
