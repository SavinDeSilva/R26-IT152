#!/usr/bin/env python3
"""
Apply database/schema.sql to PostgreSQL.

Use this when psql is not on your PATH (common on Windows).

Usage:
    python scripts/apply_schema.py
    python scripts/apply_schema.py --database-url postgresql://postgres:password@localhost:5432/travel_app
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
SCHEMA_PATH = BACKEND_DIR / "database" / "schema.sql"


def find_psql() -> Path | None:
    for version in (16, 15, 14, 13):
        candidate = Path(f"C:/Program Files/PostgreSQL/{version}/bin/psql.exe")
        if candidate.exists():
            return candidate
    return None


def apply_with_psql(database_url: str) -> bool:
    psql = find_psql()
    if not psql:
        return False

    # postgresql://user:pass@host:port/dbname
    from urllib.parse import urlparse

    parsed = urlparse(database_url)
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    cmd = [
        str(psql),
        "-h",
        parsed.hostname or "localhost",
        "-p",
        str(parsed.port or 5432),
        "-U",
        parsed.username or "postgres",
        "-d",
        (parsed.path or "/travel_app").lstrip("/"),
        "-f",
        str(SCHEMA_PATH),
        "-v",
        "ON_ERROR_STOP=1",
    ]

    print(f"Running: {psql.name} -f database/schema.sql")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return True


def apply_with_psycopg2(database_url: str) -> None:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply database/schema.sql")
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()

    load_dotenv(BACKEND_DIR / ".env")
    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: Set DATABASE_URL in .env or pass --database-url", file=sys.stderr)
        return 1

    if not SCHEMA_PATH.exists():
        print(f"ERROR: Missing {SCHEMA_PATH}", file=sys.stderr)
        return 1

    print(f"Applying schema to {database_url.split('@')[-1]} ...")

    if apply_with_psql(database_url):
        print("Schema applied successfully (via psql).")
        return 0

    print("psql not found in Program Files — applying via Python/psycopg2 ...")
    try:
        apply_with_psycopg2(database_url)
        print("Schema applied successfully.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "\nManual fallback: In pgAdmin, open Query Tool on travel_app, "
            "load database/schema.sql, and click Execute.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
