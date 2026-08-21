"""Room type pricing for accommodation (Single / Double / Family).

Given hotel price range A–B (price_min–price_max):
  Single  → A
  Double  → (A + B) / 2
  Family  → B
"""

from __future__ import annotations

from app.models.accommodation import Accommodation

VALID_ROOM_TYPES = ("single", "double", "family")

ROOM_TYPE_CONFIG: dict[str, dict] = {
    "single": {"label": "Single", "short": "A", "hint": "Uses minimum rate (A)"},
    "double": {"label": "Double", "short": "(A+B)/2", "hint": "Uses average rate (A+B)/2"},
    "family": {"label": "Family", "short": "B", "hint": "Uses maximum rate (B)"},
}


def normalize_room_type(value: str | None) -> str:
    key = (value or "double").strip().lower()
    return key if key in ROOM_TYPE_CONFIG else "double"


def room_type_label(room_type: str | None) -> str:
    return ROOM_TYPE_CONFIG[normalize_room_type(room_type)]["label"]


def room_nightly_rate(
    price_min: float | None,
    price_max: float | None,
    room_type: str | None,
) -> float | None:
    """Effective nightly LKR rate for the selected room type (exact, for filtering)."""
    if price_min is None or price_max is None:
        return None
    a = float(price_min)
    b = float(price_max)
    key = normalize_room_type(room_type)
    if key == "single":
        return a
    if key == "family":
        return b
    return (a + b) / 2.0


def round_near(amount: float, *, lkr: bool = True) -> int:
    """Round to a friendly step so displayed prices feel approximate, not exact."""
    value = float(amount)
    if lkr:
        step = 500 if value < 50_000 else 1_000
    else:
        step = 5 if value < 500 else 10 if value < 2_000 else 50
    return int(round(value / step) * step)


def format_lkr_near(amount: float | None, *, with_tilde: bool = True) -> str | None:
    if amount is None:
        return None
    rounded = round_near(amount, lkr=True)
    prefix = "~" if with_tilde else ""
    return f"{prefix}{rounded:,} LKR"


def format_usd_near(amount: float | None, *, with_tilde: bool = True) -> str | None:
    if amount is None:
        return None
    rounded = round_near(amount, lkr=False)
    prefix = "~" if with_tilde else ""
    return f"{prefix}${rounded:,}"


def format_lkr_range_near(
    price_min: float | None,
    price_max: float | None,
    *,
    with_tilde: bool = True,
) -> str | None:
    if price_min is None or price_max is None:
        return None
    a = format_lkr_near(float(price_min), with_tilde=with_tilde)
    b = format_lkr_near(float(price_max), with_tilde=with_tilde)
    if not a or not b:
        return None
    return f"{a} – {b}"


def enrich_accommodation(hotel: Accommodation, room_type: str | None) -> dict:
    """Return hotel dict with approximate room-type nightly rate for UI and PDF."""
    data = hotel.to_dict()
    normalized = normalize_room_type(room_type)
    nightly = room_nightly_rate(hotel.price_min, hotel.price_max, normalized)
    data["room_type"] = normalized
    data["price_nightly"] = round_near(nightly, lkr=True) if nightly is not None else None
    if nightly is not None:
        near = format_lkr_near(nightly)
        data["price_range_display"] = f"{near} / night (approx.)"
    else:
        data["price_range_display"] = hotel.price_range or "Price on request"
    base_range = format_lkr_range_near(hotel.price_min, hotel.price_max)
    data["price_range_base"] = base_range or hotel.price_range
    return data


def room_types_for_api() -> list[dict]:
    return [
        {
            "id": key,
            "label": cfg["label"],
            "short": cfg["short"],
            "hint": cfg["hint"],
        }
        for key, cfg in ROOM_TYPE_CONFIG.items()
    ]
