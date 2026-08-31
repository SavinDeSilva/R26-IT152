"""Room type pricing for accommodation (BB / HB / FB × Single / Double / Triple).

Hotel range A–B is price_min–price_max. Nightly rate is:

  Single BB  A
  Single HB  A + 0.125 × (B − A)
  Single FB  A + 0.250 × (B − A)
  Double BB  A + 0.375 × (B − A)
  Double HB  A + 0.500 × (B − A)
  Double FB  A + 0.625 × (B − A)
  Triple BB  A + 0.750 × (B − A)
  Triple HB  A + 0.875 × (B − A)
  Triple FB  B

Older trips stored single / double / triple / family; those aliases still work.
"""

from __future__ import annotations

from components.itinerary.backend.models.accommodation import Accommodation

ROOM_TYPE_STEPS: dict[str, float] = {
    "single_bb": 0.0,
    "single_hb": 0.125,
    "single_fb": 0.250,
    "double_bb": 0.375,
    "double_hb": 0.500,
    "double_fb": 0.625,
    "triple_bb": 0.750,
    "triple_hb": 0.875,
    "triple_fb": 1.0,
}

ROOM_TYPE_CONFIG: dict[str, dict] = {
    "single_bb": {"label": "Single BB", "short": "A", "hint": "Minimum baseline"},
    "single_hb": {"label": "Single HB", "short": "A+12.5%", "hint": "Step 1"},
    "single_fb": {"label": "Single FB", "short": "A+25%", "hint": "Step 2"},
    "double_bb": {"label": "Double BB", "short": "A+37.5%", "hint": "Step 3"},
    "double_hb": {"label": "Double HB", "short": "Mid", "hint": "Mid-point"},
    "double_fb": {"label": "Double FB", "short": "A+62.5%", "hint": "Step 5"},
    "triple_bb": {"label": "Triple BB", "short": "A+75%", "hint": "Step 6"},
    "triple_hb": {"label": "Triple HB", "short": "A+87.5%", "hint": "Step 7"},
    "triple_fb": {"label": "Triple FB", "short": "B", "hint": "Maximum ceiling"},
}

VALID_ROOM_TYPES = tuple(ROOM_TYPE_CONFIG.keys())

ROOM_TYPE_ALIASES = {
    "family": "triple_fb",
    "single": "single_bb",
    "double": "double_hb",
    "triple": "triple_fb",
    "singlebb": "single_bb",
    "singlehb": "single_hb",
    "singlefb": "single_fb",
    "doublebb": "double_bb",
    "doublehb": "double_hb",
    "doublefb": "double_fb",
    "triplebb": "triple_bb",
    "triplehb": "triple_hb",
    "triplefb": "triple_fb",
}

DEFAULT_ROOM_TYPE = "double_hb"


def normalize_room_type(value: str | None) -> str:
    raw = (value or DEFAULT_ROOM_TYPE).strip().lower()
    compact = raw.replace(" ", "").replace("-", "").replace("_", "")
    if raw in ROOM_TYPE_CONFIG:
        return raw
    if raw in ROOM_TYPE_ALIASES:
        return ROOM_TYPE_ALIASES[raw]
    if compact in ROOM_TYPE_ALIASES:
        return ROOM_TYPE_ALIASES[compact]
    keyed = raw.replace(" ", "_").replace("-", "_")
    if keyed in ROOM_TYPE_CONFIG:
        return keyed
    return DEFAULT_ROOM_TYPE


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
    step = ROOM_TYPE_STEPS[normalize_room_type(room_type)]
    return a + step * (b - a)


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
    """Return hotel dict with room-type nightly rate and spreadsheet contact fields."""
    data = hotel.to_dict()
    normalized = normalize_room_type(room_type)
    nightly = room_nightly_rate(hotel.price_min, hotel.price_max, normalized)
    data["room_type"] = normalized
    data["room_type_label"] = room_type_label(normalized)
    data["price_nightly"] = round_near(nightly, lkr=True) if nightly is not None else None
    if nightly is not None:
        near = format_lkr_near(nightly)
        data["price_range_display"] = f"{near} / night ({data['room_type_label']})"
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
