"""
Itinerary ML — visit-window classification + content-based activity ranking.

Panel mapping
-------------
Model choice : Logistic Regression vs Random Forest; DummyClassifier is the baseline.
Dataset      : seeded attractions catalogue (name, category, destination, details, mood_tag).
Metrics      : accuracy + macro-F1 (classification); Precision@5 (ranking).
Baseline     : majority-class dummy; random ranking.
Validity     : stratified 80/20 hold-out (random_state=42); vectorizer fit on train only.

Time-slot labels are weakly supervised: mood_tag in the catalogue is mapped to
morning / afternoon / evening. The classifiers never see mood_tag as a feature —
only name + category + destination + details — so hold-out scores measure whether
visit windows can be recovered from attraction text.

This is sklearn, not OpenAI. PDF export still uses a template; ML fills times
and suggested add-ons that the PDF prints.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

MOOD_TO_SLOT = {
    "Spiritual": "morning",
    "Adventure": "morning",
    "Excited": "morning",
    "Explore": "afternoon",
    "Curious": "afternoon",
    "Happy": "afternoon",
    "Authentic": "afternoon",
    "Healing": "evening",
    "Peaceful": "evening",
    "Relaxed": "evening",
}

SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2}
SLOT_START_HOUR = {"morning": 7.5, "afternoon": 13.0, "evening": 16.5}
DEFAULT_SLOT = "afternoon"
RANDOM_STATE = 42
HOLDOUT_SIZE = 0.2
RANK_K = 5

ML_DIR = Path(__file__).resolve().parents[1] / "ml"
BUNDLE_PATH = ML_DIR / "itinerary_models.joblib"
METRICS_PATH = ML_DIR / "metrics.json"


def _row_text(row: dict) -> str:
    parts = [
        str(row.get("attraction_name") or ""),
        str(row.get("category") or ""),
        str(row.get("destination") or ""),
        str(row.get("details") or ""),
    ]
    return " ".join(p.strip() for p in parts if p and p.strip() and p != "None")


def time_slot_label(mood_tag: str | None) -> str:
    if not mood_tag:
        return DEFAULT_SLOT
    return MOOD_TO_SLOT.get(str(mood_tag).strip(), DEFAULT_SLOT)


def _format_clock(hour_float: float) -> str:
    total_minutes = int(round(hour_float * 60)) % (24 * 60)
    dt = datetime(2000, 1, 1) + timedelta(minutes=total_minutes)
    return dt.strftime("%I:%M %p").lstrip("0")


def _attraction_to_row(attraction) -> dict:
    if isinstance(attraction, dict):
        return {
            "id": attraction.get("id"),
            "attraction_name": attraction.get("attraction_name") or "",
            "category": attraction.get("category") or "",
            "destination": attraction.get("destination") or "",
            "details": attraction.get("details") or "",
            "mood_tag": attraction.get("mood_tag") or "",
        }
    return {
        "id": getattr(attraction, "id", None),
        "attraction_name": getattr(attraction, "attraction_name", None) or "",
        "category": getattr(attraction, "category", None) or "",
        "destination": getattr(attraction, "destination", None) or "",
        "details": getattr(attraction, "details", None) or "",
        "mood_tag": getattr(attraction, "mood_tag", None) or "",
    }


def _rows_from_db() -> list[dict]:
    from components.itinerary.backend.models.attraction import Attraction

    return [_attraction_to_row(row) for row in Attraction.query.all()]


def _split(y: list[str], n: int):
    from sklearn.model_selection import train_test_split

    indices = np.arange(n)
    counts: dict[str, int] = {}
    for label in y:
        counts[label] = counts.get(label, 0) + 1
    can_stratify = all(c >= 2 for c in counts.values()) and len(counts) >= 2
    try:
        return train_test_split(
            indices,
            test_size=HOLDOUT_SIZE,
            random_state=RANDOM_STATE,
            stratify=y if can_stratify else None,
        )
    except ValueError:
        return train_test_split(indices, test_size=HOLDOUT_SIZE, random_state=RANDOM_STATE)


def _classify_holdout(texts: list[str], labels: list[str]) -> dict[str, Any]:
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report, f1_score

    train_idx, test_idx = _split(labels, len(labels))
    y = np.array(labels)
    x_train = [texts[i] for i in train_idx]
    x_test = [texts[i] for i in test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2), max_features=4000)
    x_train_t = vectorizer.fit_transform(x_train)
    x_test_t = vectorizer.transform(x_test)

    baseline = DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE)
    baseline.fit(x_train_t, y_train)
    base_pred = baseline.predict(x_test_t)
    baseline_scores = {
        "name": "DummyClassifier(most_frequent)",
        "accuracy": round(float(accuracy_score(y_test, base_pred)), 4),
        "macro_f1": round(float(f1_score(y_test, base_pred, average="macro", zero_division=0)), 4),
    }

    candidates = {
        "LogisticRegression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=160,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    scored = []
    for name, model in candidates.items():
        model.fit(x_train_t, y_train)
        pred = model.predict(x_test_t)
        scored.append(
            {
                "name": name,
                "accuracy": round(float(accuracy_score(y_test, pred)), 4),
                "macro_f1": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
                "report": classification_report(y_test, pred, zero_division=0),
                "estimator": model,
            }
        )

    scored.sort(key=lambda row: (row["macro_f1"], row["accuracy"]), reverse=True)
    winner = scored[0]

    full_vec = TfidfVectorizer(min_df=1, ngram_range=(1, 2), max_features=4000)
    x_all = full_vec.fit_transform(texts)
    if winner["name"] == "LogisticRegression":
        production = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )
    else:
        production = RandomForestClassifier(
            n_estimators=160,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    production.fit(x_all, labels)

    return {
        "vectorizer": full_vec,
        "model": production,
        "chosen_model": winner["name"],
        "baseline": baseline_scores,
        "holdout": {
            "n_train": int(len(train_idx)),
            "n_test": int(len(test_idx)),
            "accuracy": winner["accuracy"],
            "macro_f1": winner["macro_f1"],
            "report": winner["report"],
        },
        "candidates": [
            {"name": row["name"], "accuracy": row["accuracy"], "macro_f1": row["macro_f1"]}
            for row in scored
        ],
    }


def _ranking_holdout(texts: list[str], rows: list[dict], k: int = RANK_K) -> dict[str, Any]:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    n = len(rows)
    if n < k + 1:
        return {"k": k, "precision_at_k": 0.0, "random_precision_at_k": 0.0, "n_queries": 0}

    vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2), max_features=4000)
    matrix = vectorizer.fit_transform(texts)
    sim = cosine_similarity(matrix)

    moods = [str(r.get("mood_tag") or "") for r in rows]
    dests = [str(r.get("destination") or "") for r in rows]
    rng = np.random.RandomState(RANDOM_STATE)
    model_scores = []
    random_scores = []

    for i in range(n):
        relevant = {
            j
            for j in range(n)
            if j != i
            and (
                (moods[i] and moods[i] == moods[j])
                or (dests[i] and dests[i] == dests[j])
            )
        }
        if not relevant:
            continue
        order = np.argsort(-sim[i])
        ranked = [int(j) for j in order if int(j) != i][:k]
        model_scores.append(sum(1 for j in ranked if j in relevant) / k)

        others = [j for j in range(n) if j != i]
        rng.shuffle(others)
        random_scores.append(sum(1 for j in others[:k] if j in relevant) / k)

    return {
        "k": k,
        "relevance": "same destination or same mood_tag",
        "n_queries": len(model_scores),
        "precision_at_k": round(float(np.mean(model_scores)) if model_scores else 0.0, 4),
        "random_precision_at_k": round(float(np.mean(random_scores)) if random_scores else 0.0, 4),
    }


@dataclass
class MlBundle:
    rows: list[dict]
    texts: list[str]
    vectorizer: Any
    matrix: Any
    mood_model: Any
    time_model: Any
    metrics: dict[str, Any] = field(default_factory=dict)

    def transform(self, texts: list[str]):
        return self.vectorizer.transform(texts)


_BUNDLE: MlBundle | None = None


def train_from_rows(rows: list[dict]) -> MlBundle:
    from sklearn.feature_extraction.text import TfidfVectorizer

    cleaned = []
    for row in rows:
        item = _attraction_to_row(row)
        if not _row_text(item).strip():
            continue
        cleaned.append(item)
    if len(cleaned) < 12:
        raise ValueError("Need at least 12 attractions with text to train itinerary models")

    texts = [_row_text(row) for row in cleaned]
    mood_labels = [(row.get("mood_tag") or "Explore").strip() or "Explore" for row in cleaned]
    time_labels = [time_slot_label(row.get("mood_tag")) for row in cleaned]

    mood_result = _classify_holdout(texts, mood_labels)
    time_result = _classify_holdout(texts, time_labels)
    ranking = _ranking_holdout(texts, cleaned)

    vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2), max_features=4000)
    matrix = vectorizer.fit_transform(texts)

    metrics = {
        "dataset": {
            "n_attractions": len(cleaned),
            "features": "TF-IDF unigrams+bigrams of name, category, destination, details",
            "label_mood": "catalogue mood_tag (supervised)",
            "label_time": "weak labels: mood_tag mapped to morning/afternoon/evening",
            "mood_not_used_as_feature": True,
        },
        "mood_classifier": {
            "task": "Predict attraction mood from text",
            "chosen_model": mood_result["chosen_model"],
            "baseline": mood_result["baseline"],
            "holdout": {
                "n_train": mood_result["holdout"]["n_train"],
                "n_test": mood_result["holdout"]["n_test"],
                "accuracy": mood_result["holdout"]["accuracy"],
                "macro_f1": mood_result["holdout"]["macro_f1"],
            },
            "candidates": mood_result["candidates"],
        },
        "time_classifier": {
            "task": "Predict visit window (morning / afternoon / evening)",
            "chosen_model": time_result["chosen_model"],
            "baseline": time_result["baseline"],
            "holdout": {
                "n_train": time_result["holdout"]["n_train"],
                "n_test": time_result["holdout"]["n_test"],
                "accuracy": time_result["holdout"]["accuracy"],
                "macro_f1": time_result["holdout"]["macro_f1"],
            },
            "candidates": time_result["candidates"],
            "label_map": MOOD_TO_SLOT,
        },
        "ranking": ranking,
        "validity": {
            "split": "stratified 80/20 hold-out",
            "random_state": RANDOM_STATE,
            "vectorizer_fit": "training fold only during evaluation; refit on full catalogue for serving",
        },
    }

    return MlBundle(
        rows=cleaned,
        texts=texts,
        vectorizer=vectorizer,
        matrix=matrix,
        mood_model=mood_result["model"],
        time_model=time_result["model"],
        metrics=metrics,
    )


def save_bundle(bundle: MlBundle) -> None:
    import joblib

    ML_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "rows": bundle.rows,
            "texts": bundle.texts,
            "vectorizer": bundle.vectorizer,
            "matrix": bundle.matrix,
            "mood_model": bundle.mood_model,
            "time_model": bundle.time_model,
            "metrics": bundle.metrics,
        },
        BUNDLE_PATH,
    )
    METRICS_PATH.write_text(json.dumps(bundle.metrics, indent=2), encoding="utf-8")


def load_bundle() -> MlBundle | None:
    import joblib

    if not BUNDLE_PATH.is_file():
        return None
    payload = joblib.load(BUNDLE_PATH)
    return MlBundle(
        rows=payload["rows"],
        texts=payload["texts"],
        vectorizer=payload["vectorizer"],
        matrix=payload["matrix"],
        mood_model=payload["mood_model"],
        time_model=payload["time_model"],
        metrics=payload.get("metrics") or {},
    )


def train_from_database() -> MlBundle:
    bundle = train_from_rows(_rows_from_db())
    save_bundle(bundle)
    return bundle


def ensure_ready(force: bool = False) -> MlBundle | None:
    global _BUNDLE
    if _BUNDLE is not None and not force:
        return _BUNDLE
    if not force:
        loaded = load_bundle()
        if loaded is not None:
            _BUNDLE = loaded
            return _BUNDLE
    try:
        _BUNDLE = train_from_database()
    except Exception:
        _BUNDLE = None
    return _BUNDLE


def metrics_snapshot() -> dict[str, Any] | None:
    bundle = ensure_ready()
    if bundle is None:
        if METRICS_PATH.is_file():
            return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        return None
    mood = bundle.metrics.get("mood_classifier") or {}
    time = bundle.metrics.get("time_classifier") or {}
    holdout = time.get("holdout") or mood.get("holdout") or {}
    return {
        "chosen_model": time.get("chosen_model") or mood.get("chosen_model"),
        "baseline": time.get("baseline") or mood.get("baseline"),
        "holdout": holdout,
        "ranking": bundle.metrics.get("ranking"),
        "mood_classifier": mood,
        "time_classifier": time,
        "dataset": bundle.metrics.get("dataset"),
        "validity": bundle.metrics.get("validity"),
    }


def predict_time_slots(attractions: list) -> list[dict[str, Any]]:
    bundle = ensure_ready()
    rows = [_attraction_to_row(item) for item in attractions]
    if bundle is None:
        return [
            {
                "time_slot": time_slot_label(row.get("mood_tag")),
                "confidence": None,
                "source": "mood_map",
            }
            for row in rows
        ]

    texts = [_row_text(row) for row in rows]
    matrix = bundle.transform(texts)
    labels = bundle.time_model.predict(matrix)
    confidences: list[float | None] = [None] * len(labels)
    if hasattr(bundle.time_model, "predict_proba"):
        proba = bundle.time_model.predict_proba(matrix)
        classes = list(bundle.time_model.classes_)
        for i, label in enumerate(labels):
            confidences[i] = round(float(proba[i][classes.index(label)]), 3)

    return [
        {
            "time_slot": str(label),
            "confidence": confidences[i],
            "source": "sklearn",
        }
        for i, label in enumerate(labels)
    ]


def schedule_day_activities(attractions: list, day_start: float | None = None) -> list[dict[str, Any]]:
    """Order a day's stops by predicted visit window and assign clock times."""
    predictions = predict_time_slots(attractions)
    paired = list(enumerate(zip(attractions, predictions)))
    paired.sort(key=lambda item: (SLOT_ORDER.get(item[1][1]["time_slot"], 1), item[0]))

    morning_start = day_start if day_start is not None else SLOT_START_HOUR["morning"]
    cursors = {
        "morning": float(morning_start),
        "afternoon": SLOT_START_HOUR["afternoon"],
        "evening": SLOT_START_HOUR["evening"],
    }
    gap = 1.75
    scheduled = []
    for _, (attraction, pred) in paired:
        slot = pred["time_slot"] if pred["time_slot"] in cursors else DEFAULT_SLOT
        hour = min(max(cursors[slot], 5.0), 19.5)
        if 12.0 <= hour < 13.0 and slot != "afternoon":
            hour = 13.0
        scheduled.append(
            {
                "attraction": attraction,
                "time": _format_clock(hour),
                "time_slot": slot,
                "time_confidence": pred.get("confidence"),
                "time_source": pred.get("source"),
            }
        )
        cursors[slot] = hour + gap
        if slot == "morning" and cursors["afternoon"] <= cursors["morning"]:
            cursors["afternoon"] = cursors["morning"] + 0.25
        if slot == "afternoon" and cursors["evening"] <= cursors["afternoon"]:
            cursors["evening"] = cursors["afternoon"] + 0.25
    return scheduled


def suggest_activities(
    selected_ids: list[int],
    destination: str | None,
    trip_moods: list[str] | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Content-based suggestions: TF-IDF cosine vs selected stops, same city first."""
    from sklearn.metrics.pairwise import cosine_similarity

    bundle = ensure_ready()
    if bundle is None:
        return []

    selected = set(int(i) for i in (selected_ids or []) if i is not None)
    catalogue = bundle.rows
    if not catalogue:
        return []

    query_idx = [i for i, row in enumerate(catalogue) if row.get("id") in selected]
    if not query_idx:
        query_idx = list(range(min(3, len(catalogue))))

    query_vec = np.asarray(bundle.matrix[query_idx].mean(axis=0))
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
    scores = cosine_similarity(query_vec, bundle.matrix)[0]
    dest_key = (destination or "").strip().lower()
    mood_set = {m.strip() for m in (trip_moods or []) if m}

    ranked = []
    for i, row in enumerate(catalogue):
        rid = row.get("id")
        if rid in selected:
            continue
        score = float(scores[i])
        row_dest = str(row.get("destination") or "").strip().lower()
        if dest_key and row_dest == dest_key:
            score += 0.15
        if mood_set and str(row.get("mood_tag") or "") in mood_set:
            score += 0.08
        ranked.append((score, row))
    ranked.sort(key=lambda item: item[0], reverse=True)

    out = []
    for score, row in ranked[:limit]:
        out.append(
            {
                "attraction_id": row.get("id"),
                "title": row.get("attraction_name"),
                "category": row.get("category"),
                "mood_tag": row.get("mood_tag"),
                "destination": row.get("destination"),
                "description": (row.get("details") or "")[:280],
                "score": round(score, 4),
                "reason": "TF-IDF cosine similarity to your selected stops",
            }
        )
    return out
