from datetime import datetime

from app import db


class BudgetSplit(db.Model):
    __tablename__ = "budget_split"

    trip_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("user_trip_input.trip_id", ondelete="CASCADE"),
        primary_key=True,
    )
    transport = db.Column(db.Numeric, nullable=False, default=0)
    food = db.Column(db.Numeric, nullable=False, default=0)
    shopping = db.Column(db.Numeric, nullable=False, default=0)
    accommodation = db.Column(db.Numeric, nullable=False, default=0)
    guide = db.Column(db.Numeric, nullable=False, default=0)
    transport_pct = db.Column(db.Numeric, nullable=False, default=25)
    food_pct = db.Column(db.Numeric, nullable=False, default=25)
    accommodation_pct = db.Column(db.Numeric, nullable=False, default=35)
    shopping_pct = db.Column(db.Numeric, nullable=False, default=15)
    guide_pct = db.Column(db.Numeric, nullable=False, default=0)
    include_guide = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    trip = db.relationship("UserTripInput", back_populates="budget_split")

    def to_dict(self):
        guide_pct = float(self.guide_pct or 0)
        include_guide = bool(self.include_guide) or guide_pct > 0
        return {
            "trip_id": str(self.trip_id),
            "transport": float(self.transport),
            "food": float(self.food),
            "shopping": float(self.shopping),
            "accommodation": float(self.accommodation),
            "guide": float(self.guide or 0),
            "transport_pct": float(self.transport_pct),
            "food_pct": float(self.food_pct),
            "accommodation_pct": float(self.accommodation_pct),
            "shopping_pct": float(self.shopping_pct),
            "guide_pct": guide_pct,
            "include_guide": include_guide,
        }
