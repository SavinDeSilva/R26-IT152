"""
generated_itinerary.py — database table for finished itineraries.

Simple job: store the big itinerary JSON after generate runs.

Flow:
  ai_service makes a dict → this class saves it as a row → UI / PDF reads it later.
"""

from datetime import datetime

from app import db


class GeneratedItinerary(db.Model):
    """
    Class = one saved itinerary row in Postgres table `generated_itinerary`.

    Fields (what each column is):
      id         — row number
      trip_id    — which trip this plan belongs to
      itinerary  — the full plan as JSON (days, times, hotels, summary)
      created_at — when it was saved
      trip       — link back to the UserTripInput object
    """

    __tablename__ = "generated_itinerary"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("user_trip_input.trip_id", ondelete="CASCADE"),
        nullable=False,
    )
    # itinerary = dict/JSON built by ai_service (not from OpenAI)
    itinerary = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # trip = related UserTripInput object (the wizard trip)
    trip = db.relationship("UserTripInput", back_populates="itineraries")

    def to_dict(self):
        """
        What it does: turns this database row into a normal Python dict
        so Flask can send it as JSON to the browser.
        """
        return {
            "id": self.id,
            "trip_id": str(self.trip_id),
            "itinerary": self.itinerary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
