"""Wellness matcher models (Ayurveda & spiritual centers)."""

from datetime import datetime

from app import db


class WellnessCenter(db.Model):
    __tablename__ = "wellness_centers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    conditions_text = db.Column(db.Text)
    dosha_focus = db.Column(db.String(50))
    price_tier = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    latitude = db.Column(db.Numeric(9, 6))
    longitude = db.Column(db.Numeric(9, 6))
    district = db.Column(db.String(100))
    address = db.Column(db.String(500))
    verified_status = db.Column(db.String(255))
    notes = db.Column(db.Text)
    google_rating = db.Column(db.Numeric(3, 1))
    google_review_count = db.Column(db.Integer)
    nlp_quality_score = db.Column(db.Numeric(4, 2))
    nlp_quality_source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reviews = db.relationship(
        "WellnessReview",
        back_populates="center",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_pool_dict(self):
        """Shape used by the matching engine candidate pool."""
        return {
            "name": self.name,
            "category": self.category,
            "conditions_text": self.conditions_text or "",
            "dosha_focus": self.dosha_focus or "General/Unspecified",
            "nlp_quality": float(self.nlp_quality_score or 3.5),
            "quality_source": self.nlp_quality_source or "",
            "price_tier": self.price_tier or "Mid",
            "google_rating": float(self.google_rating) if self.google_rating is not None else None,
            "phone": self.phone or "",
            "lat": float(self.latitude) if self.latitude is not None else None,
            "lng": float(self.longitude) if self.longitude is not None else None,
            "reviews": [r.review_text for r in self.reviews],
            "verified": self.verified_status or "",
            "notes": self.notes or "",
            "address": self.address or "",
            "district": self.district or "",
            "google_rating_real": float(self.google_rating) if self.google_rating is not None else None,
            "review_count_real": self.google_review_count,
        }


class WellnessReview(db.Model):
    __tablename__ = "wellness_reviews"

    id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(
        db.Integer, db.ForeignKey("wellness_centers.id", ondelete="CASCADE"), nullable=False
    )
    review_text = db.Column(db.Text, nullable=False)
    is_risk_flagged = db.Column(db.Boolean, default=False, nullable=False)

    center = db.relationship("WellnessCenter", back_populates="reviews")


class WellnessConditionMapping(db.Model):
    __tablename__ = "wellness_condition_mappings"

    id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.String(255), nullable=False, unique=True)
    duration_range = db.Column(db.String(100))
    duration_source = db.Column(db.String(500))
    outcome_likelihood_pct = db.Column(db.Integer)
    outcome_source = db.Column(db.String(500))

    def to_dict(self):
        return {
            "condition_name": self.condition_name,
            "duration_range": self.duration_range,
            "duration_source": self.duration_source,
            "outcome_likelihood_pct": self.outcome_likelihood_pct,
            "outcome_source": self.outcome_source,
        }


class WellnessMatchingSession(db.Model):
    __tablename__ = "wellness_matching_sessions"

    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer)  # optional SOS tourist id; no FK so travel-only DBs still migrate
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    path = db.Column(db.String(32), nullable=False)
    condition_name = db.Column(db.String(255))
    companion_condition_name = db.Column(db.String(255))
    predicted_dosha = db.Column(db.String(20))
    dosha_confidence_pct = db.Column(db.Numeric(5, 1))
    budget_tier = db.Column(db.String(50))
    matched_center_id = db.Column(
        db.Integer, db.ForeignKey("wellness_centers.id", ondelete="SET NULL")
    )
    match_pct = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
