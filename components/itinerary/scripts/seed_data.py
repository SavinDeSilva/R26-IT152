#!/usr/bin/env python3
"""
Load static reference tables from Excel into PostgreSQL.

ONLY seeds: accommodation, attractions, business_directory, travel_agencies, tourist_guides
Never seeds dynamic tables (users, user_trip_input, budget_split, etc.)

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --database-url postgresql://user:pass@localhost/travel_app
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "components" / "shared" / "backend"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SCRIPTS_DIR = Path(__file__).resolve().parent  # scripts/travel/
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from excel_attraction_images import attraction_image_urls_in_order  # noqa: E402

# Explicit alias → canonical mappings discovered during data inspection
LOCATION_NORMALIZATION: dict[str, str] = {
    "Badulla Pradeshiya Sabha": "Badulla",
    "Bandarawela Pradeshiya Sabha": "Bandarawela",
    "Beruwala Pradeshiya Sabha": "Beruwala",
    "Chilaw Pradeshiya Sabha": "Chilaw",
    "Chilaw Urban Council": "Chilaw",
    "Dambulla Pradeshiya Sabha": "Dambulla",
    "Dodangoda Pradeshiya Sabha": "Dodangoda",
    "Gampaha Pradeshiya Sabha": "Gampaha",
    "Ja-Ela Pradeshiya Sabha": "Ja-Ela",
    "Kalpitiya Pradeshiya Sabha": "Kalpitiya",
    "Kalutara Pradeshiya Sabha": "Kalutara",
    "Kurunegala Pradeshiya Sabha": "Kurunegala",
    "Matale Pradeshiya Sabha": "Matale",
    "Minuwangoda Pradeshiya Sabha": "Minuwangoda",
    "Panadura Pradeshiya Sabha": "Panadura",
    "Puttalam Pradeshiya Sabha": "Puttalam",
    "Tangalle Pradeshiya Sabha": "Tangalle",
    "Weligama Pradeshiya Sabha": "Weligama",
    "Ella Pradeshiya Sabha": "Ella",
    "Katana Pradeshiya Sabha": "Katana",
    "Akurana Pradeshiya Sabha": "Akurana",
    "Badulla Pradeshiya Sabha": "Badulla",
    "balapitiya": "Balapitiya",
    "dodangoda": "Dodangoda",
    "mirigama": "Mirigama",
    "Katharagama": "Kataragama",
    "Dehiwala": "Dehiwala-Mount Lavinia",
    "Colombo (Boralesgamuwa)": "Boralesgamuwa",
    "Kegalle (Aranayaka)": "Kegalle",
    "Ratnapura (Kalthota)": "Ratnapura",
    "MC (Municipal Council)": "MC",
    "Kotte Muncipal Council": "Sri Jayawardenapura-Kotte",
}

FUZZY_THRESHOLD = 0.88
AMBIGUOUS_REVIEWS: list[dict] = []


def strip_pradeshiya_suffix(value: str) -> str:
    cleaned = re.sub(
        r"\s+(Pradeshiya Sabha|Urban Council|Municipal Council|Muncipal Council)$",
        "",
        value.strip(),
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def normalize_location(raw: str | None, field_name: str, source_file: str) -> str | None:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None

    value = str(raw).strip()
    if not value:
        return None

    if value in LOCATION_NORMALIZATION:
        return LOCATION_NORMALIZATION[value]

    stripped = strip_pradeshiya_suffix(value)
    if stripped in LOCATION_NORMALIZATION:
        return LOCATION_NORMALIZATION[stripped]

    canonical_values = set(LOCATION_NORMALIZATION.values())
    best_match = None
    best_score = 0.0
    for candidate in canonical_values:
        score = SequenceMatcher(None, value.lower(), candidate.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_score >= FUZZY_THRESHOLD and best_match:
        if best_match.lower() != value.lower():
            AMBIGUOUS_REVIEWS.append(
                {
                    "source_file": source_file,
                    "field": field_name,
                    "original": value,
                    "normalized": best_match,
                    "method": "fuzzy",
                    "score": round(best_score, 3),
                }
            )
        return best_match

    if stripped != value:
        return stripped

    return value


def parse_price_range(price_range: str | None) -> tuple[float | None, float | None]:
    if not price_range or (isinstance(price_range, float) and pd.isna(price_range)):
        return None, None
    text_val = str(price_range).strip()
    numbers = re.findall(r"[\d,]+", text_val.replace(",", ""))
    if not numbers:
        return None, None
    nums = [float(n.replace(",", "")) for n in numbers]
    if len(nums) == 1:
        return nums[0], nums[0]
    return min(nums), max(nums)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df.where(pd.notnull(df), None)


def normalize_accommodation_image(value) -> str | None:
    """Turn Excel Images cell into a usable <img src> (URL or data URI)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "#value!"):
        return None
    if text.startswith("data:image"):
        return text
    if not text.startswith("http"):
        return None

    try:
        parsed = urllib.parse.urlparse(text)
    except Exception:
        return None

    host = (parsed.netloc or "").lower()
    # Google image result pages store the real photo in imgurl=
    if "google." in host and ("/imgres" in parsed.path or "imgurl=" in text):
        qs = urllib.parse.parse_qs(parsed.query)
        imgurl = qs.get("imgurl", [None])[0]
        if imgurl:
            return urllib.parse.unquote(imgurl)
        return None

    # Google image search pages are not displayable as img src
    if "google." in host and "/search" in parsed.path:
        return None

    return text


def load_accommodation() -> pd.DataFrame:
    path = DATA_DIR / "accomadation.xlsx"
    df = clean_dataframe(pd.read_excel(path, sheet_name="Sheet"))
    # Excel column is "Images" (or "Image") — store as image for the API/UI
    for col in list(df.columns):
        if str(col).strip().lower() in ("image", "images"):
            if col != "image":
                df = df.rename(columns={col: "image"})
            break
    if "image" not in df.columns:
        df["image"] = None
    df["image"] = df["image"].apply(normalize_accommodation_image)
    found = int(df["image"].notna().sum())
    print(f"  accommodation images: {found}/{len(df)}")
    df["normalized_local_authority"] = df["Local Authority"].apply(
        lambda v: normalize_location(v, "Local Authority", path.name)
    )
    parsed = df["Price Range"].apply(parse_price_range)
    df["price_min"] = parsed.apply(lambda x: x[0])
    df["price_max"] = parsed.apply(lambda x: x[1])
    return df


def load_attractions() -> pd.DataFrame:
    path = DATA_DIR / "attractions.xlsx"
    df = clean_dataframe(pd.read_excel(path, sheet_name="Attractions"))
    # Image cells are Excel rich-data embeds (#VALUE! to pandas). Extract real photos.
    names = [
        "" if n is None else str(n)
        for n in df.get("Attraction Name", pd.Series(dtype=object)).tolist()
    ]
    extracted = attraction_image_urls_in_order(xlsx_path=path, attraction_names=names)
    df["image"] = extracted
    found = sum(1 for u in extracted if u)
    local = sum(1 for u in extracted if u and str(u).startswith("/api/media/"))
    external = found - local
    print(
        f"  attraction images: {found}/{len(extracted)} "
        f"({local} local files, {external} external URLs)"
    )
    df["normalized_destination"] = df["Destination"].apply(
        lambda v: normalize_location(v, "Destination", path.name)
    )
    return df


def load_business_directory() -> pd.DataFrame:
    path = DATA_DIR / "business_directory.xlsx"
    df = clean_dataframe(pd.read_excel(path, sheet_name="Directory"))
    df["normalized_local_authority"] = df["Local Authority"].apply(
        lambda v: normalize_location(v, "Local Authority", path.name)
    )
    return df


def load_travel_agencies() -> pd.DataFrame:
    path = DATA_DIR / "travel_agencies.xlsx"
    df = clean_dataframe(pd.read_excel(path, sheet_name="Sheet"))
    df["normalized_local_authority"] = df["Local Authority"].apply(
        lambda v: normalize_location(v, "Local Authority", path.name)
    )
    return df


KNOWN_GUIDE_TYPES = {"National", "Chauffeur", "Area", "Site"}
KNOWN_LANGUAGES = [
    "Arabic",
    "Chinese",
    "Dutch",
    "English",
    "French",
    "German",
    "Greek",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Italian",
    "Japanese",
    "Korean",
    "Mandarin",
    "Mandarian",
    "Russian",
    "Spanish",
    "Swedish",
    "Tamil",
    "Thai",
    "Urdu",
]
JUNK_GUIDE_NAMES = {"search for a tour guide", "tour guides"}


def clean_guide_languages(raw) -> str | None:
    """Keep only recognized language names from noisy scraped language cells."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip()
    if not text:
        return None

    found: list[str] = []
    for lang in KNOWN_LANGUAGES:
        if re.search(rf"\b{re.escape(lang)}\b", text, flags=re.IGNORECASE):
            normalized = "Mandarin" if lang.lower() in ("mandarin", "mandarian") else lang
            if normalized not in found:
                found.append(normalized)
    return ", ".join(found) if found else None


def load_tourist_guides() -> pd.DataFrame:
    path = DATA_DIR / "tourist_guides.csv"
    df = clean_dataframe(pd.read_csv(path))

    rename_map = {
        "name": "name",
        "category": "guide_type",
        "languages": "languages",
        "tel": "tel",
        "address": "address",
        "registration_no": "registration_no",
        "email": "email",
        "validity": "validity",
        "image_url": "image_url",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    name = df.get("name", pd.Series(dtype=object)).astype(str).str.strip()
    reg = df.get("registration_no", pd.Series(dtype=object))
    guide_type = df.get("guide_type", pd.Series(dtype=object)).astype(str).str.strip()

    valid_name = ~name.str.lower().isin(JUNK_GUIDE_NAMES) & name.ne("") & name.ne("nan")
    valid_reg = reg.notna() & reg.astype(str).str.strip().ne("") & reg.astype(str).str.lower().ne("nan")
    valid_type = guide_type.isin(KNOWN_GUIDE_TYPES)
    df = df[valid_name & valid_reg & valid_type].copy()

    df["name"] = df["name"].astype(str).str.strip()
    df["guide_type"] = df["guide_type"].astype(str).str.strip()
    df["registration_no"] = df["registration_no"].astype(str).str.strip()
    df["languages"] = df["languages"].apply(clean_guide_languages)

    for col in ("tel", "address", "email", "validity", "image_url"):
        if col not in df.columns:
            df[col] = None
        else:
            df[col] = df[col].apply(
                lambda v: None
                if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip().lower() in ("", "nan", "none")
                else str(v).strip()
            )

    # Drop duplicate registration numbers, keep first occurrence
    df = df.drop_duplicates(subset=["registration_no"], keep="first")
    return df.reset_index(drop=True)


def ensure_tourist_guides_schema(engine) -> None:
    """Apply tourist_guides migration for existing databases."""
    migration = Path(__file__).resolve().parents[1] / "backend" / "migrations" / "001_tourist_guides.sql"
    sql = migration.read_text(encoding="utf-8")
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(sql))


def truncate_reference_tables(engine) -> None:
    """Only truncate static reference tables — never touch user/trip data."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE TABLE
                    accommodation,
                    attractions,
                    business_directory,
                    travel_agencies,
                    tourist_guides
                RESTART IDENTITY CASCADE
                """
            )
        )


def seed_table(engine, table_name: str, df: pd.DataFrame, columns: list[str]) -> int:
    subset = df[columns].copy()
    subset.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=500)
    return len(subset)


TABLE_COLUMNS = {
    "accommodation": [
        "Name", "Category", "Rooms", "Address", "Local Authority",
        "normalized_local_authority", "Web", "Email", "Registration No:",
        "Tel", "Mobile", "Price Range", "price_min", "price_max", "image",
    ],
    "attractions": [
        "Attraction Name", "Category", "Destination", "normalized_destination",
        "Details", "mood_tag", "image",
    ],
    "business_directory": [
        "Business Name", "Address", "Local Authority", "normalized_local_authority",
        "District", "Website", "Email", "Telephone", "Fax",
    ],
    "travel_agencies": [
        "Name", "Address", "Local Authority", "normalized_local_authority",
        "Website", "Email", "Registration No.", "Licence No.",
        "Licence Validity", "Telephone",
    ],
    "tourist_guides": [
        "name", "guide_type", "languages", "tel", "address",
        "registration_no", "email", "validity", "image_url",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed static reference tables from Excel")
    parser.add_argument(
        "--database-url",
        default=None,
        help="PostgreSQL URL (defaults to DATABASE_URL env var)",
    )
    parser.add_argument(
        "--skip-truncate",
        action="store_true",
        help="Append without truncating (may cause duplicates)",
    )
    args = parser.parse_args()

    database_url = args.database_url
    if not database_url:
        from dotenv import load_dotenv
        import os

        load_dotenv(BACKEND_DIR / ".env")
        database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: Set DATABASE_URL or pass --database-url", file=sys.stderr)
        return 1

    print(f"Loading reference data from {DATA_DIR}")
    accommodation_df = load_accommodation()
    attractions_df = load_attractions()
    business_df = load_business_directory()
    agencies_df = load_travel_agencies()
    guides_df = load_tourist_guides()

    print(f"  accommodation:        {len(accommodation_df)} rows")
    print(f"  attractions:          {len(attractions_df)} rows")
    print(f"  business_directory:   {len(business_df)} rows")
    print(f"  travel_agencies:      {len(agencies_df)} rows")
    print(f"  tourist_guides:       {len(guides_df)} rows")

    engine = create_engine(database_url)

    print("Ensuring tourist_guides schema...")
    try:
        ensure_tourist_guides_schema(engine)
    except Exception as exc:
        print(f"WARNING: tourist_guides migration note: {exc}")

    if not args.skip_truncate:
        print("Truncating static reference tables...")
        try:
            truncate_reference_tables(engine)
        except Exception as exc:
            if "does not exist" in str(exc).lower() or "undefinedtable" in str(exc).lower():
                print(
                    "\nERROR: Database tables not found. Apply the schema first:\n"
                    "  python scripts/apply_schema.py\n"
                    "Or in pgAdmin: Query Tool → Open database/schema.sql → Execute\n",
                    file=sys.stderr,
                )
                return 1
            raise

    print("Inserting reference data...")
    seed_table(engine, "accommodation", accommodation_df, TABLE_COLUMNS["accommodation"])
    seed_table(engine, "attractions", attractions_df, TABLE_COLUMNS["attractions"])
    seed_table(engine, "business_directory", business_df, TABLE_COLUMNS["business_directory"])
    seed_table(engine, "travel_agencies", agencies_df, TABLE_COLUMNS["travel_agencies"])
    seed_table(engine, "tourist_guides", guides_df, TABLE_COLUMNS["tourist_guides"])

    if AMBIGUOUS_REVIEWS:
        review_path = Path(__file__).resolve().parent / "location_normalization_review.json"
        review_path.write_text(json.dumps(AMBIGUOUS_REVIEWS, indent=2), encoding="utf-8")
        print(f"\nWARNING: {len(AMBIGUOUS_REVIEWS)} fuzzy-normalized locations flagged for review.")
        print(f"  See {review_path}")

    print("\nSeed complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
