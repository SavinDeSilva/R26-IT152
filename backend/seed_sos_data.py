"""
Seed hospitals & stations from real Excel sources, plus per-station logins
and demo tourists/incidents.

Usage (from backend/):
  python seed_data.py

Credentials for every police station row are written to:
  data/sos/station_credentials.csv
"""

from __future__ import annotations

import csv
import math
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from app import create_app, db
from app.sos_models import (
    EmergencyContact,
    Hospital,
    Incident,
    LocationPing,
    Officer,
    Station,
    Tourist,
)

SEED_DIR = Path(__file__).resolve().parent / "data" / "sos"
HOSPITALS_XLSX = SEED_DIR / "Sri_Lanka_Government_Hospitals_with_Coordinates.xlsx"
POLICE_XLSX = SEED_DIR / "Sri_Lanka_Police_Emergency_with_Coordinates.xlsx"
CREDENTIALS_CSV = SEED_DIR / "station_credentials.csv"

COORD_PRECISION = 4  # ~11m — used to cluster duplicate HQ desks


def _clean_str(val) -> str | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    return s or None


def _clean_float(val) -> float | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _clean_phone(val) -> str | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, float):
        return str(int(val)) if val == int(val) else str(val)
    return str(val).strip() or None


def _slug(text: str | None, fallback: str = "station") -> str:
    raw = (text or fallback).lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    raw = raw.strip("_")
    return (raw[:40] or fallback)


def load_hospitals() -> tuple[int, int]:
    """Load both sheets. Returns (loaded, hotline_only_flagged)."""
    if not HOSPITALS_XLSX.exists():
        raise FileNotFoundError(f"Missing {HOSPITALS_XLSX}")

    loaded = 0
    flagged = 0

    gov = pd.read_excel(HOSPITALS_XLSX, sheet_name="Government Hospitals")
    for _, row in gov.iterrows():
        lat = _clean_float(row.get("Latitude"))
        lng = _clean_float(row.get("Longitude"))
        hotline = lat is None or lng is None
        if hotline:
            flagged += 1
        db.session.add(
            Hospital(
                district=_clean_str(row.get("District")),
                name=_clean_str(row.get("Hospital")) or "Unknown Hospital",
                local_number=_clean_phone(row.get("Local Number")),
                international_number=_clean_phone(row.get("International Number")),
                latitude=lat,
                longitude=lng,
                is_private=False,
                is_hotline_only=hotline,
            )
        )
        loaded += 1

    priv = pd.read_excel(HOSPITALS_XLSX, sheet_name="Private Hospitals")
    for _, row in priv.iterrows():
        lat = _clean_float(row.get("Latitude"))
        lng = _clean_float(row.get("Longitude"))
        hotline = lat is None or lng is None
        if hotline:
            flagged += 1
            print(f"  [hotline-only] {_clean_str(row.get('Hospital / Hotline'))}")
        db.session.add(
            Hospital(
                district=None,
                name=_clean_str(row.get("Hospital / Hotline")) or "Unknown Private",
                local_number=_clean_phone(row.get("Local Number")),
                international_number=_clean_phone(row.get("International Number")),
                latitude=lat,
                longitude=lng,
                is_private=True,
                is_hotline_only=hotline,
            )
        )
        loaded += 1

    db.session.commit()
    return loaded, flagged


def load_stations() -> tuple[int, int]:
    """
    Load Police Emergency sheet, then mark only one desk per coordinate cluster
    as is_dispatchable so nearest-station routing ignores duplicate HQ rooms.
    """
    if not POLICE_XLSX.exists():
        raise FileNotFoundError(f"Missing {POLICE_XLSX}")

    df = pd.read_excel(POLICE_XLSX, sheet_name="Police Emergency")
    stations: list[Station] = []
    for _, row in df.iterrows():
        range_name = _clean_str(row.get("Range"))
        division = _clean_str(row.get("Division"))
        desk = _clean_str(row.get("Desk"))
        telephone = _clean_phone(row.get("Telephone No"))
        lat = _clean_float(row.get("Latitude"))
        lng = _clean_float(row.get("Longitude"))
        # Skip completely empty trailing rows
        if not any([range_name, division, desk, telephone, lat, lng]):
            continue
        st = Station(
            range_name=range_name or "Unknown Range",
            division=division,
            desk=desk,
            telephone=telephone,
            latitude=lat,
            longitude=lng,
            is_dispatchable=True,
        )
        stations.append(st)
        db.session.add(st)

    db.session.flush()
    dispatchable = dedupe_by_coordinates(stations)
    db.session.commit()
    return len(stations), dispatchable


def dedupe_by_coordinates(stations: list[Station]) -> int:
    """
    Keep the first station in each rounded (lat,lng) cluster as dispatchable.
    Prefer rows that have a Division set (more likely district desks) when choosing.
    """
    clusters: dict[tuple, list[Station]] = {}
    for st in stations:
        if st.latitude is None or st.longitude is None:
            st.is_dispatchable = False
            continue
        key = (round(st.latitude, COORD_PRECISION), round(st.longitude, COORD_PRECISION))
        clusters.setdefault(key, []).append(st)

    count = 0
    for group in clusters.values():
        for st in group:
            st.is_dispatchable = False
        preferred = sorted(
            group,
            key=lambda s: (0 if s.division else 1, s.id or 0),
        )[0]
        preferred.is_dispatchable = True
        count += 1

    print(f"  Dispatchable stations after coordinate dedupe: {count} of {len(stations)}")
    return count


def seed_station_credentials() -> list[dict]:
    """
    Create one officer login for EVERY police station from the Excel file.
    Username pattern: {place}.{desk}.{id}  e.g. galle.emergency.18
    Password pattern: Police{id:03d}!
    """
    stations = Station.query.order_by(Station.id.asc()).all()
    used_usernames: set[str] = set()
    rows: list[dict] = []

    for st in stations:
        place = _slug(st.division or st.range_name, "station")
        desk = _slug(st.desk, "desk")
        # Short stable usernames — long place slugs were getting truncated on login
        username = f"st{st.id:03d}"
        used_usernames.add(username)

        password = f"Police{st.id:03d}!"
        email = f"{username}@police.lk"
        badge = f"SLP-{1000 + st.id}"
        officer_name = f"Duty Officer — {st.display_name}"

        off = Officer(
            name=officer_name[:200],
            badge_number=badge,
            username=username,
            email=email,
            station_id=st.id,
            is_active=True,
        )
        off.set_password(password)
        db.session.add(off)

        rows.append(
            {
                "station_id": st.id,
                "display_name": st.display_name,
                "range": st.range_name or "",
                "division": st.division or "",
                "desk": st.desk or "",
                "telephone": st.telephone or "",
                "latitude": st.latitude if st.latitude is not None else "",
                "longitude": st.longitude if st.longitude is not None else "",
                "is_dispatchable": st.is_dispatchable,
                "username": username,
                "password": password,
                "email": email,
            }
        )

    db.session.commit()

    try:
        CREDENTIALS_CSV.parent.mkdir(parents=True, exist_ok=True)
        with CREDENTIALS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
            if rows:
                writer.writeheader()
                writer.writerows(rows)
        print(f"  Credentials file: {CREDENTIALS_CSV}")
    except PermissionError:
        print(f"  WARNING: could not write {CREDENTIALS_CSV} (file open?). Logins still created in DB.")

    print(f"  Station logins created: {len(rows)}")
    return rows


def seed_demo_tourists():
    """Synthetic tourists and past incidents for demo/testing."""
    dispatchable = Station.query.filter_by(is_dispatchable=True).all()
    if not dispatchable:
        raise RuntimeError("No dispatchable stations — load police data first")

    from app.services.routing import nearest_entity

    colombo_st, _ = nearest_entity(6.9271, 79.8612, dispatchable)
    st0 = colombo_st or dispatchable[0]

    tourists_spec = [
        ("Emma Thompson", "emma@example.com", "UK", "UK1234567", "+447700900001", 6.9271, 79.8612),
        ("Hans Mueller", "hans@example.com", "Germany", "DE9988776", "+4915112345678", 7.2906, 80.6337),
        ("Yuki Tanaka", "yuki@example.com", "Japan", "JP5544332", "+819012345678", 6.0535, 80.2210),
    ]
    tourists = []
    for name, email, nat, doc, phone, lat, lng in tourists_spec:
        t = Tourist(
            name=name,
            email=email,
            auth_provider="local",
            nationality=nat,
            trip_start=(datetime.utcnow() - timedelta(days=3)).date(),
            trip_end=(datetime.utcnow() + timedelta(days=10)).date(),
            hotel_name="Demo Hotel Colombo" if "Emma" in name else None,
            hotel_contact="+94112345678" if "Emma" in name else None,
            last_known_lat=lat,
            last_known_lng=lng,
        )
        t.set_password("tourist123")
        t.set_sensitive(phone=phone, passport_or_nic=doc)
        ec = EmergencyContact(name=f"{name.split()[0]} Contact", relationship="Family")
        ec.set_sensitive(phone=phone[:-1] + "9", email=f"{name.split()[0].lower()}@example.com")
        t.emergency_contact = ec
        db.session.add(t)
        tourists.append(t)

    db.session.flush()

    past = Incident(
        tourist_id=tourists[0].id,
        station_id=st0.id,
        hospital_id=None,
        incident_type=Incident.TYPE_THEFT,
        status=Incident.STATUS_CLOSED,
        initial_lat=6.9271,
        initial_lng=79.8612,
        distance_to_station_km=1.2,
        triggered_at=datetime.utcnow() - timedelta(days=2, hours=1),
        acknowledged_at=datetime.utcnow() - timedelta(days=2, hours=0, minutes=50),
        dispatched_at=datetime.utcnow() - timedelta(days=2, hours=0, minutes=40),
        closed_at=datetime.utcnow() - timedelta(days=2, hours=0, minutes=10),
        contact_notified_at=datetime.utcnow() - timedelta(days=2, hours=1),
        hotel_notified_at=datetime.utcnow() - timedelta(days=2, hours=1),
        station_notified_at=datetime.utcnow() - timedelta(days=2, hours=1),
        tracking_active=False,
    )
    db.session.add(past)
    db.session.flush()
    db.session.add(
        LocationPing(
            incident_id=past.id,
            latitude=6.9271,
            longitude=79.8612,
            accuracy=12,
            recorded_at=past.triggered_at,
        )
    )

    past2 = Incident(
        tourist_id=tourists[1].id,
        station_id=st0.id,
        hospital_id=None,
        incident_type=Incident.TYPE_MEDICAL,
        status=Incident.STATUS_CLOSED,
        initial_lat=6.9340,
        initial_lng=79.8500,
        distance_to_station_km=2.5,
        triggered_at=datetime.utcnow() - timedelta(days=1, hours=3),
        acknowledged_at=datetime.utcnow() - timedelta(days=1, hours=2, minutes=55),
        dispatched_at=datetime.utcnow() - timedelta(days=1, hours=2, minutes=45),
        closed_at=datetime.utcnow() - timedelta(days=1, hours=2),
        contact_notified_at=datetime.utcnow() - timedelta(days=1, hours=3),
        station_notified_at=datetime.utcnow() - timedelta(days=1, hours=3),
        tracking_active=False,
    )
    db.session.add(past2)

    db.session.commit()
    print(f"Demo tourists: {[t.id for t in tourists]}")
    print("Demo tourist logins (password: tourist123):")
    for t in tourists:
        print(f"  {t.email}")
    demo_officer = Officer.query.filter_by(station_id=st0.id).first()
    if demo_officer:
        print(
            f"Sample police login (Colombo-area station): "
            f"username={demo_officer.username}  password=Police{st0.id:03d}!"
        )


def reset_sos_tables_only():
    """
    Drop/recreate ONLY Tourist SOS tables.
    Never touches existing travel_app tables (users, attractions, etc.).
    """
    sos_table_names = [
        "chat_messages",
        "location_pings",
        "incidents",
        "officers",
        "emergency_contacts",
        "tourists",
        "stations",
        "hospitals",
        "hotels",
    ]
    # Drop in dependency-safe order via SQLAlchemy metadata for known models only
    tables = []
    for name in sos_table_names:
        table = db.metadata.tables.get(name)
        if table is not None:
            tables.append(table)

    if tables:
        print(f"  Dropping SOS tables only: {', '.join(t.name for t in tables)}")
        db.metadata.drop_all(bind=db.engine, tables=tables)

    print("  Creating SOS tables…")
    db.create_all()


def main():
    app = create_app()
    with app.app_context():
        print(f"Target database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Resetting SOS tables only (existing travel_app tables kept)…")
        reset_sos_tables_only()

        print("Loading hospitals from Excel…")
        h_count, h_flag = load_hospitals()
        print(f"  Hospitals loaded: {h_count} (hotline-only flagged: {h_flag})")

        print("Loading police stations from Excel…")
        s_count, s_disp = load_stations()
        print(f"  Stations loaded: {s_count} (dispatchable: {s_disp})")

        print("Creating login credentials for each station…")
        seed_station_credentials()

        print("Seeding demo tourists / past incidents…")
        seed_demo_tourists()
        print("Done.")


if __name__ == "__main__":
    main()
