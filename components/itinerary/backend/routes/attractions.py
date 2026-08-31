from flask import Blueprint, jsonify, request

from components.itinerary.backend.models.attraction import Attraction
from app.services.attraction_i18n import localize_attraction, localize_attraction_list, normalize_site_lang

attractions_bp = Blueprint("attractions", __name__)


def _request_lang() -> str:
    return normalize_site_lang(
        request.args.get("lang") or request.headers.get("X-Site-Language")
    )


def _attraction_payload(attraction: Attraction) -> dict:
    # Prefer Excel-extracted local paths; do not substitute Google/Openverse photos.
    data = attraction.to_dict()
    image = (attraction.image or "").strip()
    data["image"] = image or None
    return data


@attractions_bp.route("/attractions", methods=["GET"])
def list_attractions():
    moods_param = request.args.get("moods", "")
    moods = [m.strip() for m in moods_param.split(",") if m.strip()]

    query = Attraction.query
    if moods:
        query = query.filter(Attraction.mood_tag.in_(moods))

    attractions = query.order_by(Attraction.attraction_name).all()
    lang = _request_lang()
    unique_moods = (
        Attraction.query.with_entities(Attraction.mood_tag)
        .distinct()
        .filter(Attraction.mood_tag.isnot(None))
        .order_by(Attraction.mood_tag)
        .all()
    )

    payload = [_attraction_payload(a) for a in attractions]
    # List stays English unless translate=1 — bulk Google Translate blocked the UI 20–120s.
    translate_list = request.args.get("translate", "").lower() in ("1", "true", "yes")
    if lang != "en" and translate_list:
        payload = localize_attraction_list(payload, lang, include_details=False)

    return jsonify(
        {
            "attractions": payload,
            "count": len(payload),
            "available_moods": [m[0] for m in unique_moods if m[0]],
            "filtered_moods": moods,
            "language": lang,
        }
    )


@attractions_bp.route("/attractions/<int:attraction_id>", methods=["GET"])
def get_attraction(attraction_id: int):
    attraction = Attraction.query.get_or_404(attraction_id)
    lang = _request_lang()
    data = _attraction_payload(attraction)
    if lang != "en":
        data = localize_attraction(data, lang, include_details=True)
    return jsonify({"attraction": data, "language": lang})
