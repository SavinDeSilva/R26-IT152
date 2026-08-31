"""
db_seed.py — Populates the `sites` table from data/tourist_sites.csv.

Usage:
    python db_seed.py

Safe to re-run: uses ON CONFLICT (site_id) DO UPDATE, so re-running this
after editing the CSV will update existing rows rather than erroring or
creating duplicates.

Assumes database.py has already been run once to create the tables.
"""

import os
import csv
from database import get_connection

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "tourist_sites.csv")

UPSERT_SQL = """
INSERT INTO sites (
    site_id, site_name, district, province, latitude, longitude,
    category, annual_visitors_2024, capacity_per_day, entrance_fee_lkr,
    is_unesco, is_eco_friendly
) VALUES (
    %(site_id)s, %(site_name)s, %(district)s, %(province)s, %(latitude)s, %(longitude)s,
    %(category)s, %(annual_visitors_2024)s, %(capacity_per_day)s, %(entrance_fee_lkr)s,
    %(is_unesco)s, %(is_eco_friendly)s
)
ON CONFLICT (site_id) DO UPDATE SET
    site_name = EXCLUDED.site_name,
    district = EXCLUDED.district,
    province = EXCLUDED.province,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    category = EXCLUDED.category,
    annual_visitors_2024 = EXCLUDED.annual_visitors_2024,
    capacity_per_day = EXCLUDED.capacity_per_day,
    entrance_fee_lkr = EXCLUDED.entrance_fee_lkr,
    is_unesco = EXCLUDED.is_unesco,
    is_eco_friendly = EXCLUDED.is_eco_friendly;
"""


def seed_sites():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Could not find {CSV_PATH}. Run this script from the project root "
            "(the folder containing app.py and the data/ subfolder)."
        )

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "site_id": int(row["site_id"]),
                "site_name": row["site_name"],
                "district": row["district"],
                "province": row["province"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "category": row["category"],
                "annual_visitors_2024": int(row["annual_visitors_2024"]),
                "capacity_per_day": int(row["capacity_per_day"]),
                "entrance_fee_lkr": int(row["entrance_fee_lkr"]),
                "is_unesco": bool(int(row["is_unesco"])),
                "is_eco_friendly": bool(int(row["is_eco_friendly"])),
            })

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for row in rows:
                cur.execute(UPSERT_SQL, row)
        conn.commit()
        print(f"Seeded/updated {len(rows)} sites into the sites table.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_sites()
