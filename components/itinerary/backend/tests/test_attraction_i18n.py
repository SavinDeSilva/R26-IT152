"""Tests for attraction catalog localization."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "components" / "shared" / "backend"))
sys.path.insert(0, str(ROOT / "components" / "itinerary" / "backend"))
sys.path.insert(0, str(ROOT / "components" / "sos" / "backend"))

from app.services.attraction_i18n import localize_attraction, normalize_site_lang  # noqa: E402


def test_normalize_site_lang():
    assert normalize_site_lang("ta") == "ta"
    assert normalize_site_lang("TA-LK") == "ta"
    assert normalize_site_lang("xx") == "en"


def test_localize_skips_english():
    raw = {
        "id": 1,
        "attraction_name": "Sigiriya Rock",
        "destination": "Sigiriya",
        "details": "Ancient fortress.",
        "category": "Heritage",
    }
    assert localize_attraction(raw, "en") == raw


def test_localize_list_skips_details(monkeypatch):
    import app.services.attraction_i18n as mod

    calls = []

    def fake(text, lang):
        calls.append(text)
        return f"[{lang}]{text}"

    monkeypatch.setattr(mod, "_translate_en_text", fake)
    items = [
        {"id": 1, "attraction_name": "Sigiriya Rock", "destination": "Sigiriya", "details": "Long text."},
        {"id": 2, "attraction_name": "Dambulla Cave", "destination": "Dambulla", "details": "Other long text."},
    ]
    out = mod.localize_attraction_list(items, "si", include_details=False)
    assert out[0]["attraction_name"].startswith("[si]")
    assert out[0]["details"] == "Long text."
    assert "Long text." not in calls
    assert "Other long text." not in calls
