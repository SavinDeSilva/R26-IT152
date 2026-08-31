"""Serve locally extracted attraction images from Excel."""

from pathlib import Path

from flask import Blueprint, abort, send_from_directory

media_bp = Blueprint("media", __name__)

STATIC_ATTRACTIONS = Path(__file__).resolve().parents[1] / "static" / "attractions"


@media_bp.route("/media/attractions/<path:filename>", methods=["GET"])
def attraction_image(filename: str):
    # Prevent path traversal
    safe = Path(filename).name
    if safe != filename or ".." in filename:
        abort(404)
    directory = STATIC_ATTRACTIONS
    if not (directory / safe).is_file():
        abort(404)
    return send_from_directory(directory, safe, max_age=86400)
