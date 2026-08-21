"""Persist wellness matcher pool edits to PostgreSQL (MVC Model layer)."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.wellness import WellnessCenter, WellnessReview
from app.services.matching_engine import detect_risk_flags


def upsert_center(center: dict) -> WellnessCenter | None:
    name = (center.get("name") or "").strip()
    if not name:
        return None

    row = WellnessCenter.query.filter_by(name=name).first()
    if row is None:
        row = WellnessCenter(name=name)
        db.session.add(row)

    row.category = center.get("category") or "Curative"
    row.conditions_text = center.get("conditions_text") or ""
    row.dosha_focus = center.get("dosha_focus") or "General/Unspecified"
    row.price_tier = center.get("price_tier") or "Mid"
    row.phone = center.get("phone") or ""
    row.latitude = center.get("lat")
    row.longitude = center.get("lng")
    row.district = center.get("district") or ""
    row.address = center.get("address") or ""
    row.verified_status = center.get("verified") or ""
    row.notes = center.get("notes") or ""
    row.google_rating = center.get("google_rating") or center.get("google_rating_real")
    row.google_review_count = center.get("review_count_real")
    row.nlp_quality_score = center.get("nlp_quality")
    row.nlp_quality_source = center.get("quality_source") or ""
    return row


def replace_reviews(row: WellnessCenter, reviews: list | None) -> None:
    WellnessReview.query.filter_by(center_id=row.id).delete()
    for text in reviews or []:
        if not text:
            continue
        flagged = bool(detect_risk_flags([text]))
        db.session.add(
            WellnessReview(
                center=row,
                review_text=text,
                is_risk_flagged=flagged,
            )
        )


def persist_pool(pool: list[dict]) -> None:
    """Best-effort sync of the in-memory candidate pool to Postgres."""
    try:
        names = []
        for center in pool:
            row = upsert_center(center)
            if row is None:
                continue
            db.session.flush()
            replace_reviews(row, center.get("reviews"))
            names.append(row.name)

        if names:
            extras = WellnessCenter.query.filter(~WellnessCenter.name.in_(names)).all()
            for extra in extras:
                db.session.delete(extra)

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()


def persist_one(center: dict) -> WellnessCenter | None:
    try:
        row = upsert_center(center)
        if row is None:
            return None
        db.session.flush()
        replace_reviews(row, center.get("reviews"))
        db.session.commit()
        return row
    except SQLAlchemyError:
        db.session.rollback()
        return None


def delete_center_by_name(name: str) -> None:
    try:
        row = WellnessCenter.query.filter_by(name=name).first()
        if row:
            db.session.delete(row)
            db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()


def find_center_id_by_name(name: str) -> int | None:
    if not name:
        return None
    row = WellnessCenter.query.filter_by(name=name).first()
    return row.id if row else None
