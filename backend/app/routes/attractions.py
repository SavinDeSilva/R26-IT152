from flask import Blueprint, jsonify, request

from app.models.attraction import Attraction

attractions_bp = Blueprint("attractions", __name__)


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
    unique_moods = (
        Attraction.query.with_entities(Attraction.mood_tag)
        .distinct()
        .filter(Attraction.mood_tag.isnot(None))
        .order_by(Attraction.mood_tag)
        .all()
    )

    payload = [_attraction_payload(a) for a in attractions]

    return jsonify(
        {
            "attractions": payload,
            "count": len(payload),
            "available_moods": [m[0] for m in unique_moods if m[0]],
            "filtered_moods": moods,
        }
    )
