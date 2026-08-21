"""Budget split calculation helpers."""

from flask import current_app


def get_default_percentages() -> dict[str, float]:
    return {
        "food_pct": current_app.config["DEFAULT_FOOD_PCT"],
        "accommodation_pct": current_app.config["DEFAULT_ACCOMMODATION_PCT"],
        "shopping_pct": current_app.config["DEFAULT_SHOPPING_PCT"],
        "transport_pct": current_app.config["DEFAULT_TRANSPORT_PCT"],
    }


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
        "food": round(total_budget * percentages["food_pct"] / 100, 2),
        "accommodation": round(total_budget * percentages["accommodation_pct"] / 100, 2),
        "shopping": round(total_budget * percentages["shopping_pct"] / 100, 2),
        "transport": round(total_budget * percentages["transport_pct"] / 100, 2),
    }


def accommodation_budget_per_night(accommodation_amount: float, days: int) -> float:
    nights = max(days - 1, 1)
    return accommodation_amount / nights
