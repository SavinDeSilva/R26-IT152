"""
trip_helpers.py — small helpers for trip API routes.

Simple job: find the logged-in user, and load only THEIR trip.
"""

import uuid

from flask_jwt_extended import get_jwt_identity

from components.itinerary.backend.models.user_trip_input import UserTripInput


def get_current_user_id() -> int:
    """
    What it does: reads the user id from the login token (JWT).
    Returns: integer user id.
    """
    return int(get_jwt_identity())


def get_user_trip(trip_id: str, user_id: int | None = None) -> UserTripInput | None:
    """
    What it does: loads one trip from the database for this user only.

    Returns:
      UserTripInput object if found and owned by this user
      None if bad id or someone else's trip (route will show 404)
    """
    uid = user_id or get_current_user_id()
    try:
        tid = uuid.UUID(trip_id)
    except ValueError:
        return None
    return UserTripInput.query.filter_by(trip_id=tid, user_id=uid).first()
