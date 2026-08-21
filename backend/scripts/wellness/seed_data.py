#!/usr/bin/env python3
"""
Create wellness tables (if missing) and seed centers from the candidate pool JSON.

Usage (from backend/):
    python scripts/wellness/seed_data.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env", override=True)

from app import create_app, db
from app.models.wellness import WellnessCenter, WellnessConditionMapping
from app.services.matching_engine import DURATION_MAP, OUTCOME_MAP, POOL, detect_risk_flags
from app.services.wellness_persist import persist_pool


def seed_condition_mappings() -> int:
    added = 0
    for name, duration in DURATION_MAP.items():
        existing = WellnessConditionMapping.query.filter_by(condition_name=name).first()
        outcome = OUTCOME_MAP.get(name) or {}
        if existing:
            existing.duration_range = duration.get("range")
            existing.duration_source = duration.get("source")
            existing.outcome_likelihood_pct = outcome.get("pct")
            existing.outcome_source = outcome.get("n")
            continue
        db.session.add(
            WellnessConditionMapping(
                condition_name=name,
                duration_range=duration.get("range"),
                duration_source=duration.get("source"),
                outcome_likelihood_pct=outcome.get("pct"),
                outcome_source=outcome.get("n"),
            )
        )
        added += 1
    db.session.commit()
    return added


def main() -> int:
    app = create_app()
    with app.app_context():
        db.create_all()
        added_conditions = seed_condition_mappings()
        persist_pool(POOL)
        center_count = WellnessCenter.query.count()
        print(f"Wellness tables ready.")
        print(f"  condition mappings upserted ({added_conditions} new)")
        print(f"  centers in database: {center_count}")
        print(f"  in-memory matching pool: {len(POOL)}")
        print(f"  risk-flagged review snippets: {sum(len(detect_risk_flags(c.get('reviews', []))) for c in POOL)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
