"""Budget split calculation helpers."""

from flask import current_app

CORE_PCT_KEYS = ("food_pct", "accommodation_pct", "shopping_pct", "transport_pct")


def get_default_percentages(include_guide: bool = False) -> dict[str, float]:
    food = float(current_app.config["DEFAULT_FOOD_PCT"])
    accommodation = float(current_app.config["DEFAULT_ACCOMMODATION_PCT"])
    shopping = float(current_app.config["DEFAULT_SHOPPING_PCT"])
    transport = float(current_app.config["DEFAULT_TRANSPORT_PCT"])
    guide = 0.0

    if include_guide:
        guide = float(current_app.config.get("DEFAULT_GUIDE_PCT", 10))
        from_shopping = min(shopping, round(guide / 2, 2))
        from_transport = min(transport, round(guide - from_shopping, 2))
        leftover = round(guide - from_shopping - from_transport, 2)
        shopping = round(shopping - from_shopping, 2)
        transport = round(transport - from_transport, 2)
        if leftover > 0:
            take_food = min(food, leftover)
            food = round(food - take_food, 2)
            leftover = round(leftover - take_food, 2)
        if leftover > 0:
            accommodation = round(accommodation - min(accommodation, leftover), 2)

    return {
        "food_pct": food,
        "accommodation_pct": accommodation,
        "shopping_pct": shopping,
        "transport_pct": transport,
        "guide_pct": guide,
    }


def percentages_for_request(data: dict, use_custom: bool) -> dict[str, float]:
    include_guide = bool(data.get("include_guide"))
    if not use_custom:
        return get_default_percentages(include_guide=include_guide)

    percentages = {
        "food_pct": float(data.get("food_pct", 0)),
        "accommodation_pct": float(data.get("accommodation_pct", 0)),
        "shopping_pct": float(data.get("shopping_pct", 0)),
        "transport_pct": float(data.get("transport_pct", 0)),
        "guide_pct": float(data.get("guide_pct", 0)) if include_guide else 0.0,
    }
    return percentages


def validate_percentages(percentages: dict[str, float]) -> tuple[bool, str | None]:
    total = sum(percentages.values())
    if round(total, 2) != 100.0:
        return False, f"Percentages must sum to 100 (got {total})"
    for key, value in percentages.items():
        if value < 0:
            return False, f"{key} cannot be negative"
    return True, None


def calculate_amounts(total_budget: float, percentages: dict[str, float]) -> dict[str, float]:
    return {
        "food": round(total_budget * percentages.get("food_pct", 0) / 100, 2),
        "accommodation": round(total_budget * percentages.get("accommodation_pct", 0) / 100, 2),
        "shopping": round(total_budget * percentages.get("shopping_pct", 0) / 100, 2),
        "transport": round(total_budget * percentages.get("transport_pct", 0) / 100, 2),
        "guide": round(total_budget * percentages.get("guide_pct", 0) / 100, 2),
    }


def accommodation_budget_per_night(accommodation_amount: float, days: int) -> float:
    nights = max(days - 1, 1)
    return accommodation_amount / nights
