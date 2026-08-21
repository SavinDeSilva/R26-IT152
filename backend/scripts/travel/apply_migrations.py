#!/usr/bin/env python3
"""Apply SQL migrations in database/migrations/."""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
MIGRATIONS = sorted((BACKEND_DIR / "database" / "migrations").glob("*.sql"))


def main() -> int:
    load_dotenv(BACKEND_DIR / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        return 1

    conn = psycopg2.connect(url)
    conn.autocommit = True
    for path in MIGRATIONS:
        sql = path.read_text(encoding="utf-8")
        print(f"Applying {path.name} ...")
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"  OK")
    conn.close()
    print("Migrations complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
