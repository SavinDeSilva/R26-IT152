"""Wellness matcher controllers (Ayurveda & spiritual tourism).

Public API paths stay the same as the standalone component so the vanilla
frontend can keep calling /api/recommend, /api/match, /api/admin/..., etc.
"""

from flask import Blueprint, current_app, jsonify, request, session
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app import db
from app.models.wellness import WellnessMatchingSession
from app.services import wellness_persist
from app.services.matching_engine import (
    CONDITIONS_BY_PATH,
    POOL,
    detect_risk_flags,
    get_analytics,
    get_ayurveda_offers,
    get_cost_estimate,
    get_duration_info,
    get_flagged_centers,
    get_outcome_info,
    get_path_pool,
    get_session_schedule,
    match_centers,
    predict_dosha,
    save_pool,
)

wellness_bp = Blueprint("wellness", __name__)


def _admin_password():
    return current_app.config.get("WELLNESS_ADMIN_PASSWORD") or "tourceylon2026"


def require_admin():
    return session.get("is_wellness_admin") is True


def _optional_identities():
    tourist_id = None
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        claims = get_jwt() or {}
        if identity is None:
            return None, None
        role = claims.get("role")
        if role == "officer":
            return None, None
        parsed = int(identity)
        if role == "tourist":
            tourist_id = parsed
        else:
            user_id = parsed
    except Exception:
        return None, None
    return tourist_id, user_id


def _record_session(payload, dosha, confidence, results):
    top = results[0] if results else None
    tourist_id, user_id = _optional_identities()
    try:
        row = WellnessMatchingSession(
            tourist_id=tourist_id,
            user_id=user_id,
            path=payload.get("path") or "ayurveda",
            condition_name=payload.get("condition"),
            companion_condition_name=payload.get("companion_condition"),
            predicted_dosha=dosha,
            dosha_confidence_pct=confidence,
            budget_tier=payload.get("budget_tier"),
            matched_center_id=wellness_persist.find_center_id_by_name(
                top.get("name") if top else None
            ),
            match_pct=(top or {}).get("combined_pct") or (top or {}).get("match_pct"),
        )
        db.session.add(row)
        db.session.commit()
    except Exception:
        db.session.rollback()


@wellness_bp.get("/wellness/health")
def wellness_health():
    return jsonify({"status": "ok", "component": "wellness", "centers_loaded": len(POOL)})


@wellness_bp.get("/centers")
def list_centers():
    path = request.args.get("path", "ayurveda")
    pool = get_path_pool(path)
    return jsonify({
        "path": path,
        "count": len(pool),
        "centers": [
            {"name": c["name"], "category": c["category"], "district": c.get("district")}
            for c in pool
        ],
    })


@wellness_bp.get("/conditions")
def list_conditions():
    path = request.args.get("path", "ayurveda")
    return jsonify({"path": path, "conditions": CONDITIONS_BY_PATH.get(path, [])})


@wellness_bp.post("/recommend")
def recommend():
    data = request.get_json(force=True) or {}

    required = [
        "condition", "age", "gender", "sleep_pattern", "appetite",
        "cold_heat_sensitivity", "emotional_tendency", "budget_tier",
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    path = data.get("path", "ayurveda")
    dosha, confidence = predict_dosha(
        data["age"], data["gender"], data["sleep_pattern"],
        data["appetite"], data["cold_heat_sensitivity"], data["emotional_tendency"],
    )

    top_n = data.get("top_n", 6)
    companion_condition = data.get("companion_condition")
    results = match_centers(
        data["condition"], dosha, data["budget_tier"],
        top_n=top_n, companion_condition=companion_condition, path=path,
    )

    duration = get_duration_info(data["condition"])
    outcome = get_outcome_info(data["condition"])
    _record_session(data, dosha, confidence, results)

    return jsonify({
        "input": {
            "condition": data["condition"],
            "budget_tier": data["budget_tier"],
            "path": path,
            "companion_condition": companion_condition,
        },
        "predicted_dosha": dosha,
        "dosha_confidence_pct": confidence,
        "expected_duration": duration,
        "outcome_likelihood": outcome,
        "recommendations": results,
    })


@wellness_bp.post("/match")
def match_only():
    """Matching with a known dosha (used by Try a Different Scenario)."""
    data = request.get_json(force=True) or {}
    required = ["condition", "dosha", "budget_tier"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    path = data.get("path", "ayurveda")
    top_n = data.get("top_n", 1)
    companion_condition = data.get("companion_condition")
    results = match_centers(
        data["condition"], data["dosha"], data["budget_tier"],
        top_n=top_n, companion_condition=companion_condition, path=path,
    )
    return jsonify({"recommendations": results})


@wellness_bp.get("/center/<path:name>")
def center_detail(name):
    match = next((c for c in POOL if c["name"].lower() == name.lower()), None)
    if not match:
        return jsonify({"error": "Center not found"}), 404

    result = dict(match)
    result["risk_flags"] = detect_risk_flags(match.get("reviews", []))
    if match["category"] == "Spiritual/Meditation":
        result["session_pattern"] = get_session_schedule(match)
    else:
        result["typical_offers"] = get_ayurveda_offers(match["category"])
    return jsonify(result)


@wellness_bp.post("/cost-estimate")
def cost_estimate():
    data = request.get_json(force=True) or {}
    required = ["condition", "price_tier"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    travelers = data.get("travelers", 1)
    est = get_cost_estimate(data["condition"], data["price_tier"], travelers)
    if est is None:
        return jsonify({"error": "No duration data available for this condition"}), 404
    return jsonify(est)


@wellness_bp.post("/admin/login")
def admin_login():
    data = request.get_json(force=True) or {}
    if data.get("password") == _admin_password():
        session["is_wellness_admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Incorrect password"}), 401


@wellness_bp.post("/admin/logout")
def admin_logout():
    session.pop("is_wellness_admin", None)
    return jsonify({"ok": True})


@wellness_bp.get("/admin/check")
def admin_check():
    return jsonify({"is_admin": require_admin()})


@wellness_bp.get("/admin/centers")
def admin_list_centers():
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    return jsonify({"centers": POOL})


@wellness_bp.put("/admin/centers/<int:idx>")
def admin_edit_center(idx):
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    if idx < 0 or idx >= len(POOL):
        return jsonify({"error": "Center not found"}), 404
    data = request.get_json(force=True) or {}
    editable_fields = [
        "name", "category", "conditions_text", "dosha_focus", "price_tier",
        "phone", "district", "address", "verified", "notes", "nlp_quality",
    ]
    for field in editable_fields:
        if field in data:
            POOL[idx][field] = data[field]
    save_pool()
    wellness_persist.persist_one(POOL[idx])
    return jsonify({"ok": True, "center": POOL[idx]})


@wellness_bp.post("/admin/centers")
def admin_add_center():
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    data = request.get_json(force=True) or {}
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    new_center = {
        "name": data.get("name"),
        "category": data.get("category", "Curative"),
        "conditions_text": data.get("conditions_text", ""),
        "dosha_focus": data.get("dosha_focus", "General/Unspecified"),
        "nlp_quality": float(data.get("nlp_quality", 3.5)),
        "quality_source": "Manually added (admin)",
        "price_tier": data.get("price_tier", "Mid"),
        "google_rating": None,
        "phone": data.get("phone", ""),
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "reviews": [],
        "verified": data.get("verified", "Needs verification"),
        "notes": data.get("notes", ""),
        "address": data.get("address", ""),
        "district": data.get("district", ""),
        "google_rating_real": None,
        "review_count_real": None,
    }
    POOL.append(new_center)
    save_pool()
    wellness_persist.persist_one(new_center)
    return jsonify({"ok": True, "center": new_center, "index": len(POOL) - 1})


@wellness_bp.delete("/admin/centers/<int:idx>")
def admin_delete_center(idx):
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    if idx < 0 or idx >= len(POOL):
        return jsonify({"error": "Center not found"}), 404
    removed = POOL.pop(idx)
    save_pool()
    wellness_persist.delete_center_by_name(removed["name"])
    return jsonify({"ok": True, "removed": removed["name"]})


@wellness_bp.get("/admin/flagged-reviews")
def admin_flagged_reviews():
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    return jsonify({"flagged": get_flagged_centers()})


@wellness_bp.get("/admin/analytics")
def admin_analytics():
    if not require_admin():
        return jsonify({"error": "Not authorized"}), 401
    return jsonify(get_analytics())
