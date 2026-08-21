#!/usr/bin/env python3
"""Resolve Google Image Search links in attractions.image to direct photo URLs."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env")

from app import create_app, db
from app.models.attraction import Attraction
from app.services.image_resolver import resolve_image_url


def main() -> int:
    app = create_app()
    with app.app_context():
        rows = Attraction.query.order_by(Attraction.id).all()
        print(f"Resolving images for {len(rows)} attractions...")
        updated = 0
        found = 0
        for index, row in enumerate(rows, start=1):
            resolved = resolve_image_url(row.image, row.attraction_name)
            if resolved:
                found += 1
                if row.image != resolved:
                    row.image = resolved
                    updated += 1
            if index % 20 == 0 or index == len(rows):
                print(f"  {index}/{len(rows)} checked ({found} photos found, {updated} rows updated)")
        db.session.commit()
        print(f"Done. {found}/{len(rows)} have displayable image URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
