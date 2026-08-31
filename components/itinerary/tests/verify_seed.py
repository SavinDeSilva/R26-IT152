#!/usr/bin/env python3
"""Verify reference table row counts after seeding."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parents[3] / "components" / "shared" / "backend"
EXPECTED = {
    "accommodation": 944,
    "attractions": 130,
    "business_directory": 126,
    "travel_agencies": 417,
    "tourist_guides": 2906,
}


def main() -> int:
    load_dotenv(BACKEND_DIR / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set in .env", file=sys.stderr)
        return 1

    engine = create_engine(url)
    ok = True
    with engine.connect() as conn:
        for table, expected in EXPECTED.items():
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            status = "OK" if count == expected else "MISMATCH"
            if count != expected:
                ok = False
            print(f"  {table:22} {count:5}  (expected {expected})  [{status}]")

        moods = conn.execute(
            text("SELECT COUNT(DISTINCT mood_tag) FROM attractions WHERE mood_tag IS NOT NULL")
        ).scalar()
        print(f"\n  distinct mood_tags:     {moods}")

    print("\nAll counts match." if ok else "\nSome counts differ — check seed output.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
