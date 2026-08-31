#!/usr/bin/env python3
"""Train itinerary sklearn models and write metrics.json.

Usage (from repo root, with DATABASE_URL set):
    python components/itinerary/scripts/train_itinerary_ml.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT / "components" / "shared" / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND_DIR))


def _rows_from_sql(database_url: str) -> list[dict]:
    import pandas as pd
    from sqlalchemy import create_engine, text

    engine = create_engine(database_url)
    query = text(
        """
        SELECT
            id,
            "Attraction Name" AS attraction_name,
            "Category" AS category,
            "Destination" AS destination,
            "Details" AS details,
            mood_tag
        FROM attractions
        """
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.fillna("").to_dict("records")


def main() -> int:
    from dotenv import load_dotenv

    from components.itinerary.backend.services.itinerary_ml_service import (
        METRICS_PATH,
        save_bundle,
        train_from_rows,
    )

    load_dotenv(BACKEND_DIR / ".env")
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: Set DATABASE_URL", file=sys.stderr)
        return 1

    rows = _rows_from_sql(database_url)
    print(f"Loaded {len(rows)} attractions")
    bundle = train_from_rows(rows)
    save_bundle(bundle)
    print(json.dumps(bundle.metrics, indent=2))
    print(f"\nWrote {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
