from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt, jwt_required
from io import BytesIO

from app import db
from app.sos_models import Incident, LocationPing, Tourist
from app.services.notify import notify_emergency_contact, notify_hotel, notify_nearest_station
from app.services.pdf_export import build_incident_pdf
from app.services.routing import nearest_entity
from app.sos_models import Station

incidents_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")


def _officer_station_id():
    claims = get_jwt()
    return claims.get("station_id")


def _normalize_incident_type(raw) -> str:
    value = (raw or Incident.TYPE_GENERAL).strip().lower()
    aliases = {
        "rape/assault": Incident.TYPE_RAPE,
        "rape_assault": Incident.TYPE_RAPE,
        "assault": Incident.TYPE_RAPE,
        "general emergency": Incident.TYPE_GENERAL,
    }
    value = aliases.get(value, value)
    if value not in Incident.VALID_TYPES:
        return Incident.TYPE_GENERAL
    return value


@incidents_bp.post("")
def create_incident():
    """Tourist SOS trigger — routes ONLY to the nearest dispatchable police station."""
    data = request.get_json(silent=True) or {}
    tourist_id = data.get("tourist_id")

    # Prefer tourist JWT when present
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

        verify_jwt_in_request(optional=True)
        claims = get_jwt() or {}
        if claims.get("role") == "tourist":
            tourist_id = int(get_jwt_identity())
    except Exception:
        pass

    lat = data.get("latitude", data.get("lat"))
    lng = data.get("longitude", data.get("lng"))
    incident_type = _normalize_incident_type(data.get("type") or data.get("incident_type"))

    if not tourist_id or lat is None or lng is None:
        return jsonify({"error": "tourist_id (or tourist login), latitude/lat, and longitude/lng are required"}), 400

    tourist = Tourist.query.get(tourist_id)
    if not tourist:
        return jsonify({"error": "Tourist not found"}), 404

    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400

    tourist.last_known_lat = lat_f
    tourist.last_known_lng = lng_f

    # Only dispatchable stations compete — one nearest station wins; others get nothing
    stations = Station.query.filter_by(is_dispatchable=True).all()
    station, dist = nearest_entity(lat_f, lng_f, stations)
    if not station:
        stations = Station.query.filter(Station.latitude.isnot(None)).all()
        station, dist = nearest_entity(lat_f, lng_f, stations)
    if not station:
        return jsonify({"error": "No police stations available for routing"}), 503

    incident = Incident(
        tourist_id=tourist.id,
        station_id=station.id,
        hospital_id=None,
        incident_type=incident_type,
        status=Incident.STATUS_OPEN,
        initial_lat=lat_f,
        initial_lng=lng_f,
        distance_to_station_km=round(dist, 3) if dist is not None else None,
        triggered_at=datetime.utcnow(),
        tracking_active=False,  # one-shot current location only
    )
    db.session.add(incident)
    db.session.flush()

    ping = LocationPing(
        incident_id=incident.id,
        latitude=lat_f,
        longitude=lng_f,
        accuracy=data.get("accuracy"),
        recorded_at=datetime.utcnow(),
    )
    db.session.add(ping)

    # Notify ONLY the assigned nearest station (+ tourist's emergency contact / hotel)
    if notify_nearest_station(incident):
        incident.station_notified_at = datetime.utcnow()
    if notify_emergency_contact(incident):
        incident.contact_notified_at = datetime.utcnow()
    if notify_hotel(incident):
        incident.hotel_notified_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"incident": incident.to_dict(reveal_tourist=False)}), 201


@incidents_bp.get("")
@jwt_required()
def list_incidents():
    station_id = request.args.get("station_id", type=int) or _officer_station_id()
    if not station_id:
        return jsonify({"error": "station_id required"}), 400

    claim_station = _officer_station_id()
    if claim_station and int(station_id) != int(claim_station):
        return jsonify({"error": "Forbidden: station scope mismatch"}), 403

    status = request.args.get("status")
    active_only = request.args.get("active", "1") != "0"
    incident_type = request.args.get("type") or request.args.get("incident_type")

    q = Incident.query.filter_by(station_id=station_id)
    if status:
        q = q.filter_by(status=status)
    elif active_only:
        q = q.filter(Incident.status != Incident.STATUS_CLOSED)
    if incident_type:
        q = q.filter_by(incident_type=_normalize_incident_type(incident_type))

    incidents = q.order_by(Incident.triggered_at.desc()).all()
    return jsonify({"incidents": [i.to_dict(reveal_tourist=True) for i in incidents]})


@incidents_bp.get("/stats")
@jwt_required()
def incident_stats():
    """Historical stats for Recharts — scoped to officer station."""
    station_id = _officer_station_id()
    if not station_id:
        return jsonify({"error": "No station on token"}), 400

    incidents = Incident.query.filter_by(station_id=station_id).all()
    by_day = {}
    response_times = []
    closed = 0
    active = 0
    by_type = {}

    for inc in incidents:
        day = inc.triggered_at.strftime("%Y-%m-%d") if inc.triggered_at else "unknown"
        by_day[day] = by_day.get(day, 0) + 1
        t = inc.incident_type or Incident.TYPE_GENERAL
        by_type[t] = by_type.get(t, 0) + 1
        if inc.status == Incident.STATUS_CLOSED:
            closed += 1
            if inc.acknowledged_at and inc.triggered_at:
                mins = (inc.acknowledged_at - inc.triggered_at).total_seconds() / 60.0
                response_times.append(
                    {
                        "incident_id": inc.id,
                        "minutes_to_ack": round(mins, 2),
                        "day": day,
                    }
                )
        else:
            active += 1

    volume = [{"day": d, "count": by_day[d]} for d in sorted(by_day.keys())]
    return jsonify(
        {
            "volume_by_day": volume,
            "response_times": response_times,
            "by_type": [
                {"type": t, "label": Incident.TYPE_LABELS.get(t, t), "count": c}
                for t, c in sorted(by_type.items())
            ],
            "closed": closed,
            "active": active,
            "total": len(incidents),
        }
    )


@incidents_bp.get("/<int:incident_id>")
@jwt_required()
def get_incident(incident_id: int):
    incident = Incident.query.get_or_404(incident_id)
    claim_station = _officer_station_id()
    if claim_station and incident.station_id != int(claim_station):
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({"incident": incident.to_dict(include_pings=True, reveal_tourist=True)})


@incidents_bp.get("/<int:incident_id>/status")
def incident_status_for_tourist(incident_id: int):
    """Tourist-facing workflow status (Acknowledge → Dispatched → Closed)."""
    incident = Incident.query.get_or_404(incident_id)
    tourist_id = request.args.get("tourist_id", type=int)

    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

        verify_jwt_in_request(optional=True)
        claims = get_jwt() or {}
        if claims.get("role") == "tourist":
            tourist_id = int(get_jwt_identity())
    except Exception:
        pass

    if not tourist_id or int(tourist_id) != int(incident.tourist_id):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(
        {
            "incident": {
                "id": incident.id,
                "status": incident.status,
                "incident_type": incident.incident_type,
                "incident_type_label": Incident.TYPE_LABELS.get(
                    incident.incident_type or Incident.TYPE_GENERAL, "General"
                ),
                "triggered_at": incident.triggered_at.isoformat() if incident.triggered_at else None,
                "acknowledged_at": incident.acknowledged_at.isoformat() if incident.acknowledged_at else None,
                "dispatched_at": incident.dispatched_at.isoformat() if incident.dispatched_at else None,
                "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
                "station": incident.station.to_dict() if incident.station else None,
                "distance_to_station_km": incident.distance_to_station_km,
            }
        }
    )


@incidents_bp.patch("/<int:incident_id>/acknowledge")
@jwt_required()
def acknowledge(incident_id: int):
    return _transition(incident_id, Incident.STATUS_ACKNOWLEDGED, "acknowledged_at")


@incidents_bp.patch("/<int:incident_id>/dispatch")
@jwt_required()
def dispatch(incident_id: int):
    return _transition(incident_id, Incident.STATUS_DISPATCHED, "dispatched_at")


@incidents_bp.patch("/<int:incident_id>/close")
@jwt_required()
def close(incident_id: int):
    return _transition(incident_id, Incident.STATUS_CLOSED, "closed_at", stop_tracking=True)


def _transition(incident_id: int, new_status: str, ts_field: str, stop_tracking: bool = False):
    incident = Incident.query.get_or_404(incident_id)
    claim_station = _officer_station_id()
    if claim_station and incident.station_id != int(claim_station):
        return jsonify({"error": "Forbidden"}), 403

    if incident.status == Incident.STATUS_CLOSED:
        return jsonify({"error": "Incident already closed"}), 400

    order = [
        Incident.STATUS_OPEN,
        Incident.STATUS_ACKNOWLEDGED,
        Incident.STATUS_DISPATCHED,
        Incident.STATUS_CLOSED,
    ]
    if order.index(new_status) < order.index(incident.status):
        return jsonify({"error": f"Cannot move from {incident.status} to {new_status}"}), 400

    incident.status = new_status
    setattr(incident, ts_field, datetime.utcnow())
    if stop_tracking:
        incident.tracking_active = False

    db.session.commit()
    return jsonify({"incident": incident.to_dict(include_pings=True, reveal_tourist=True)})


@incidents_bp.get("/<int:incident_id>/report.pdf")
@jwt_required()
def export_pdf(incident_id: int):
    incident = Incident.query.get_or_404(incident_id)
    claim_station = _officer_station_id()
    if claim_station and incident.station_id != int(claim_station):
        return jsonify({"error": "Forbidden"}), 403
    if incident.status != Incident.STATUS_CLOSED:
        return jsonify({"error": "PDF export available only for closed incidents"}), 400

    pdf_bytes = build_incident_pdf(incident)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"incident_{incident.id}_report.pdf",
    )
