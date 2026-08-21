from flask import Blueprint, jsonify, request

from app.services.image_resolver import is_direct_image_url, resolve_image_url

images_bp = Blueprint("images", __name__)


@images_bp.route("/images/resolve", methods=["GET"])
def resolve_image():
    url = (request.args.get("url") or "").strip()
    query = (request.args.get("q") or "").strip()
    if not url and not query:
        return jsonify({"error": "url or q query parameter is required"}), 400

    if url and is_direct_image_url(url):
        return jsonify({"url": url, "resolved": True})

    resolved = resolve_image_url(url or None, query or None)
    return jsonify({"url": resolved, "resolved": bool(resolved)})
