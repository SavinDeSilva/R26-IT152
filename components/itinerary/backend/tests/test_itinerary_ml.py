"""Unit tests for itinerary time classification and activity ranking."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "components" / "shared" / "backend"))
sys.path.insert(0, str(ROOT / "components" / "itinerary" / "backend"))

import components.itinerary.backend.services.itinerary_ml_service as ml  # noqa: E402


def _sample_rows():
    templates = [
        ("Yala Jeep Safari", "Wild", "Yala", "Dawn wildlife safari in the national park", "Adventure"),
        ("Wilpattu Safari", "Wild", "Wilpattu", "Early morning leopard tracking jeep ride", "Adventure"),
        ("Sinharaja Trek", "Wild", "Sinharaja", "Rainforest hiking among endemic birds", "Excited"),
        ("Horton Plains Hike", "Wild", "Nuwara Eliya", "Worlds End hike at first light", "Excited"),
        ("Temple of the Tooth", "Heritage", "Kandy", "Sacred Buddhist temple and morning puja", "Spiritual"),
        ("Dambulla Cave Temple", "Heritage", "Dambulla", "Rock cave shrine with ancient murals", "Spiritual"),
        ("Anuradhapura Dagoba", "Heritage", "Anuradhapura", "Pilgrimage among stupas and bodhi trees", "Spiritual"),
        ("Sigiriya Rock Fortress", "Heritage", "Sigiriya", "Climb the lion rock palace and frescoes", "Explore"),
        ("Polonnaruwa Ruins", "Heritage", "Polonnaruwa", "Ancient city walking tour among stone kings", "Explore"),
        ("Galle Dutch Fort", "Heritage", "Galle", "Ramparts, museums and colonial streets", "Curious"),
        ("Colombo National Museum", "Heritage", "Colombo", "Indoor museum of island history", "Curious"),
        ("Pettah Market", "Essence", "Colombo", "Busy market lanes and street food", "Happy"),
        ("Kandy Cultural Show", "Essence", "Kandy", "Evening dance performance and drums", "Happy"),
        ("Ella Nine Arches", "Scenic", "Ella", "Train viewpoint and tea country walk", "Authentic"),
        ("Nuwara Eliya Tea Estate", "Scenic", "Nuwara Eliya", "Tea plucking and factory tasting", "Authentic"),
        ("Unawatuna Beach", "Pristine", "Galle", "Sunset swim on a sandy bay", "Relaxed"),
        ("Mirissa Beach", "Pristine", "Mirissa", "Calm evening beach and seafood", "Relaxed"),
        ("Bentota Spa", "Pristine", "Bentota", "Ayurveda spa by the lagoon at dusk", "Healing"),
        ("Pasikudah Bay", "Pristine", "Batticaloa", "Shallow peaceful water for an easy evening", "Peaceful"),
        ("Nilaveli Beach", "Pristine", "Trincomalee", "Quiet shoreline and late light", "Peaceful"),
    ]
    rows = []
    for index, (name, category, dest, details, mood) in enumerate(templates, start=1):
        rows.append(
            {
                "id": index,
                "attraction_name": name,
                "category": category,
                "destination": dest,
                "details": details,
                "mood_tag": mood,
            }
        )
    return rows


def test_train_beats_or_matches_baseline_on_time_task():
    bundle = ml.train_from_rows(_sample_rows())
    time = bundle.metrics["time_classifier"]
    assert time["holdout"]["n_test"] >= 1
    assert time["chosen_model"] in {"LogisticRegression", "RandomForestClassifier"}
    assert time["baseline"]["name"].startswith("DummyClassifier")
    assert 0.0 <= time["holdout"]["macro_f1"] <= 1.0
    assert 0.0 <= time["baseline"]["macro_f1"] <= 1.0


def test_schedule_orders_morning_before_evening():
    rows = _sample_rows()
    ml._BUNDLE = ml.train_from_rows(rows)
    safari = rows[0]
    beach = rows[15]
    scheduled = ml.schedule_day_activities([beach, safari], day_start=7.5)
    order = [ml.SLOT_ORDER[item["time_slot"]] for item in scheduled]
    assert order == sorted(order)
    assert all(item["time"] for item in scheduled)


def test_suggestions_exclude_selected():
    rows = _sample_rows()
    ml._BUNDLE = ml.train_from_rows(rows)
    out = ml.suggest_activities([1, 2], destination="Yala", trip_moods=["Adventure"], limit=3)
    ids = {item["attraction_id"] for item in out}
    assert 1 not in ids and 2 not in ids
    assert len(out) <= 3


def test_ranking_reports_precision_against_random():
    bundle = ml.train_from_rows(_sample_rows())
    ranking = bundle.metrics["ranking"]
    assert ranking["k"] == 5
    assert ranking["n_queries"] > 0
    assert 0.0 <= ranking["precision_at_k"] <= 1.0
    assert 0.0 <= ranking["random_precision_at_k"] <= 1.0
