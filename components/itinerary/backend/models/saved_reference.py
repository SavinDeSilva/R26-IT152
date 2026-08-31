from datetime import datetime

from app import db


class SavedReference(db.Model):
    __tablename__ = "saved_references"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("user_trip_input.trip_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ref_type = db.Column(
        db.Enum(
            "business_directory",
            "travel_agency",
            "tourist_guide",
            name="saved_ref_type",
            create_type=False,
        ),
        nullable=False,
    )
    ref_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    trip = db.relationship("UserTripInput", back_populates="saved_references")

    def to_dict(self):
        ref_type = self.ref_type
        if hasattr(ref_type, "value"):
            ref_type = ref_type.value
        return {
            "id": self.id,
            "trip_id": str(self.trip_id),
            "user_id": self.user_id,
            "ref_type": ref_type,
            "ref_id": self.ref_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
