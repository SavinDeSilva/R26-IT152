import uuid
from datetime import datetime

from app import db


class UserTripInput(db.Model):
    __tablename__ = "user_trip_input"

    trip_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    selected_moods = db.Column(db.JSON, nullable=False, default=list)
    days = db.Column(db.Integer, nullable=False)
    attractions_by_mood = db.Column(db.JSON, nullable=False, default=list)
    attractions_by_days = db.Column(db.JSON, nullable=False, default=list)
    finalized_attractions = db.Column(db.JSON, nullable=False, default=list)
    budget = db.Column(db.Numeric)
    accommodation = db.Column(db.Text)
    accommodations = db.Column(db.JSON, nullable=False, default=list)
    room_type = db.Column(db.String(16), nullable=False, default="double")
    status = db.Column(
        db.Enum("draft", "in_progress", "completed", name="trip_status", create_type=False),
        nullable=False,
        default="draft",
    )
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="trips")
    budget_split = db.relationship("BudgetSplit", back_populates="trip", uselist=False)
    itineraries = db.relationship("GeneratedItinerary", back_populates="trip", lazy="dynamic")
    saved_references = db.relationship("SavedReference", back_populates="trip", lazy="dynamic")

    def to_dict(self):
        return {
            "trip_id": str(self.trip_id),
            "user_id": self.user_id,
            "selected_moods": self.selected_moods,
            "days": self.days,
            "attractions_by_mood": self.attractions_by_mood,
            "attractions_by_days": self.attractions_by_days,
            "finalized_attractions": self.finalized_attractions,
            "budget": float(self.budget) if self.budget is not None else None,
            "accommodation": self.accommodation,
            "accommodations": self.accommodations or [],
            "room_type": self.room_type or "double",
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
