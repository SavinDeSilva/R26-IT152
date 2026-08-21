#!/usr/bin/env python3
"""Apply database/migrations/002_google_auth.sql"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
SQL_PATH = BACKEND_DIR / "database" / "migrations" / "002_google_auth.sql"


def main() -> int:
    load_dotenv(BACKEND_DIR / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        return 1
    if not SQL_PATH.exists():
        print(f"ERROR: missing {SQL_PATH}", file=sys.stderr)
        return 1

    sql = SQL_PATH.read_text(encoding="utf-8")
    engine = create_engine(url)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(sql))
    print("Google auth migration applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
