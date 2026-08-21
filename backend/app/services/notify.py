"""Notification stubs — console by default; Twilio/SendGrid ready via env."""

from __future__ import annotations

from datetime import datetime

from flask import current_app


def _log(channel: str, recipient: str, message: str):
    stamp = datetime.utcnow().isoformat()
    line = f"[NOTIFY {stamp}] channel={channel} to={recipient} msg={message}"
    print(line)
    current_app.logger.info(line)


def send_sms(to_number: str, message: str) -> bool:
    mode = current_app.config.get("NOTIFY_MODE", "console")
    if mode == "twilio":
        sid = current_app.config.get("TWILIO_ACCOUNT_SID")
        token = current_app.config.get("TWILIO_AUTH_TOKEN")
        from_num = current_app.config.get("TWILIO_FROM_NUMBER")
        if not (sid and token and from_num):
            _log("sms-fallback", to_number, message)
            return False
        try:
            from twilio.rest import Client  # optional dependency

            Client(sid, token).messages.create(body=message, from_=from_num, to=to_number)
            return True
        except Exception as exc:
            current_app.logger.exception("Twilio SMS failed: %s", exc)
            _log("sms-error", to_number, message)
            return False

    _log("sms", to_number or "(missing)", message)
    return True


def send_email(to_email: str, subject: str, body: str) -> bool:
    mode = current_app.config.get("NOTIFY_MODE", "console")
    if mode == "sendgrid":
        api_key = current_app.config.get("SENDGRID_API_KEY")
        from_email = current_app.config.get("NOTIFY_FROM_EMAIL")
        if not api_key:
            _log("email-fallback", to_email, f"{subject}: {body}")
            return False
        try:
            import urllib.request
            import json

            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            }
            req = urllib.request.Request(
                "https://api.sendgrid.com/v3/mail/send",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception as exc:
            current_app.logger.exception("SendGrid email failed: %s", exc)
            _log("email-error", to_email, f"{subject}: {body}")
            return False

    _log("email", to_email or "(missing)", f"{subject}: {body}")
    return True


def notify_emergency_contact(incident) -> bool:
    contact = incident.tourist.emergency_contact if incident.tourist else None
    if not contact:
        return False
    tourist_name = incident.tourist.name
    from app.sos_models import Incident

    type_label = Incident.TYPE_LABELS.get(
        getattr(incident, "incident_type", None) or Incident.TYPE_GENERAL, "General"
    )
    msg = (
        f"EMERGENCY ({type_label}): {tourist_name} triggered an SOS in Sri Lanka. "
        f"Incident #{incident.id}. Location approx "
        f"{incident.initial_lat:.5f}, {incident.initial_lng:.5f}. "
        f"Police station notified: {incident.station.display_name if incident.station else 'N/A'}."
    )
    ok = False
    phone = contact.get_phone()
    email = contact.get_email()
    if phone:
        ok = send_sms(phone, msg) or ok
    if email:
        ok = send_email(email, f"SOS Alert — {tourist_name}", msg) or ok
    return ok


def notify_hotel(incident) -> bool:
    tourist = incident.tourist
    if not tourist or not tourist.hotel_name:
        return False
    contact = tourist.hotel_contact
    if not contact:
        _log("hotel-skip", tourist.hotel_name, "No hotel contact on registration")
        return False
    msg = (
        f"SOS: Guest {tourist.name} triggered an emergency alert. "
        f"Incident #{incident.id}. Police have been notified."
    )
    if "@" in contact:
        return send_email(contact, f"Guest SOS — {tourist.name}", msg)
    return send_sms(contact, msg)


def notify_nearest_station(incident) -> bool:
    """
    Alert only the single assigned (nearest) police station for this incident.
    Other stations are never contacted.
    """
    station = incident.station
    if not station:
        return False
    from app.sos_models import Incident

    type_label = Incident.TYPE_LABELS.get(
        getattr(incident, "incident_type", None) or Incident.TYPE_GENERAL, "General"
    )
    tourist_name = incident.tourist.name if incident.tourist else "Unknown tourist"
    msg = (
        f"SOS ALERT ({type_label}) for {station.display_name} ONLY. "
        f"Incident #{incident.id} — {tourist_name} at "
        f"{incident.initial_lat:.5f}, {incident.initial_lng:.5f} "
        f"({incident.distance_to_station_km} km). "
        f"Open the station dashboard to respond. Do not forward to other stations."
    )
    phone = station.telephone
    if phone:
        return send_sms(phone, msg)
    _log("station-dashboard", station.display_name, msg)
    return True
