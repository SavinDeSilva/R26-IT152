from __future__ import annotations

import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename

from app import db
from app.sos_models import ChatMessage, Incident

chat_bp = Blueprint("chat", __name__, url_prefix="/api/incidents")

IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "gif"}
VOICE_EXTS = {"webm", "ogg", "mp3", "wav", "m4a", "aac", "mp4"}


def _save_chat_media(file_storage, kind: str) -> str:
    if not file_storage or not file_storage.filename:
        raise ValueError("Media file required")
    filename = secure_filename(file_storage.filename)
    if "." not in filename:
        raise ValueError("Invalid media filename")
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = IMAGE_EXTS if kind == ChatMessage.TYPE_IMAGE else VOICE_EXTS
    if ext not in allowed:
        raise ValueError(f"Unsupported {kind} file type .{ext}")
    folder = Path(current_app.config["UPLOAD_FOLDER"]) / "chat" / kind
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"
    path = folder / name
    file_storage.save(path)
    return f"chat/{kind}/{name}"


def _can_access_incident(incident: Incident, tourist_id=None) -> tuple[bool, str | None]:
    """Officer JWT (same station) or tourist JWT / tourist_id may access the chat."""
    auth = request.headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role == "officer":
                station_id = claims.get("station_id")
                if station_id is None or int(station_id) != int(incident.station_id):
                    return False, "Forbidden: only the assigned nearest station can access this chat"
                return True, ChatMessage.ROLE_OFFICER
            if role == "tourist":
                tid = int(get_jwt_identity())
                if tid != incident.tourist_id:
                    return False, "Forbidden: tourist mismatch"
                return True, ChatMessage.ROLE_TOURIST
        except Exception:
            return False, "Invalid or expired token"

    if tourist_id is not None:
        try:
            tid = int(tourist_id)
        except (TypeError, ValueError):
            return False, "Invalid tourist_id"
        if tid != incident.tourist_id:
            return False, "Forbidden: tourist mismatch"
        return True, ChatMessage.ROLE_TOURIST

    return False, "Authentication required (officer/tourist JWT or tourist_id)"


@chat_bp.get("/<int:incident_id>/messages")
def list_messages(incident_id: int):
    incident = Incident.query.get_or_404(incident_id)
    tourist_id = request.args.get("tourist_id")
    ok, role_or_err = _can_access_incident(incident, tourist_id)
    if not ok:
        return jsonify({"error": role_or_err}), 403

    since_id = request.args.get("since_id", type=int)
    q = ChatMessage.query.filter_by(incident_id=incident_id)
    if since_id:
        q = q.filter(ChatMessage.id > since_id)
    messages = q.order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc()).all()
    return jsonify(
        {
            "messages": [m.to_dict() for m in messages],
            "incident_id": incident.id,
            "station_id": incident.station_id,
            "station": incident.station.to_dict() if incident.station else None,
        }
    )


@chat_bp.post("/<int:incident_id>/messages")
def post_message(incident_id: int):
    """
    Send a chat message to the incident's assigned (nearest) police station.

    Multipart or JSON:
      - message_type: text | image | voice
      - body: optional text / caption
      - media: file (required for image/voice)
      - tourist_id: required when not using officer JWT
    """
    incident = Incident.query.get_or_404(incident_id)

    form = request.form if request.form else {}
    data = request.get_json(silent=True) or {}
    tourist_id = form.get("tourist_id") or data.get("tourist_id") or request.args.get("tourist_id")

    ok, role_or_err = _can_access_incident(incident, tourist_id)
    if not ok:
        return jsonify({"error": role_or_err}), 403
    sender_role = role_or_err

    sender_id = None
    if sender_role == ChatMessage.ROLE_OFFICER:
        try:
            sender_id = int(get_jwt_identity())
        except Exception:
            sender_id = None
    else:
        try:
            # Prefer JWT tourist identity when present
            verify_jwt_in_request(optional=True)
            claims = get_jwt() or {}
            if claims.get("role") == "tourist":
                sender_id = int(get_jwt_identity())
            else:
                sender_id = int(tourist_id)
        except Exception:
            sender_id = int(tourist_id) if tourist_id is not None else None

    raw_type = (form.get("message_type") or data.get("message_type") or ChatMessage.TYPE_TEXT).strip().lower()
    if raw_type not in ChatMessage.VALID_TYPES:
        return jsonify({"error": f"message_type must be one of: {', '.join(sorted(ChatMessage.VALID_TYPES))}"}), 400

    body = (form.get("body") or data.get("body") or "").strip() or None
    media_path = None

    if raw_type in (ChatMessage.TYPE_IMAGE, ChatMessage.TYPE_VOICE):
        file_storage = request.files.get("media") or request.files.get("file")
        try:
            media_path = _save_chat_media(file_storage, raw_type)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    elif not body:
        return jsonify({"error": "body is required for text messages"}), 400

    msg = ChatMessage(
        incident_id=incident.id,
        sender_role=sender_role,
        sender_id=sender_id,
        message_type=raw_type,
        body=body,
        media_path=media_path,
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": msg.to_dict()}), 201
