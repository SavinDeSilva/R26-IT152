"""
Ayurveda & Spiritual Tourism Matching Engine (Python Backend)
================================================================
Synced from the JS reference implementation (tour_ceylon_webapp_desktop.html).
This is the authoritative server-side implementation for production use.

Covers:
  - Path separation (Ayurveda Treatment vs Meditation/Spiritual Retreat)
  - Dosha classification (Random Forest, from Step 4)
  - Weighted matching (condition/dosha/quality/budget)
  - Companion/group matching bonus
  - Safety/risk flag detection (keyword-based NLP scan)
  - Expected treatment duration + illustrative outcome likelihood
  - Trip cost estimation
  - Typical session pattern / offers (by category)
"""

import json
import re
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

import os

# backend/data/wellness  (this file lives in backend/app/services/)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(_BACKEND_DIR, "data", "wellness")

# ---------------------------------------------------------------
# 1. Load candidate pool (83 centers, full enrichment)
# ---------------------------------------------------------------
with open(os.path.join(DATA_DIR, "full_candidate_pool.json"), encoding="utf-8") as f:
    POOL = json.load(f)

WEIGHTS = {"condition": 0.35, "dosha": 0.20, "quality": 0.25, "budget": 0.20}

CONDITIONS_BY_PATH = {
    "ayurveda": ["Arthritis", "Joint Pain", "Sciatica", "Back Pain", "Stress", "Anxiety",
                 "Liver Disease", "Hypertension", "Detox / Weight Management", "General Wellness",
                 "Migraine", "Skin Condition"],
    "spiritual": ["Vipassana (10-day course)", "Forest Monastery Retreat", "Guided Meditation",
                  "Mindfulness & Stress Relief", "Silent Retreat", "Buddhist Philosophy & Dhamma"]
}

DURATION_MAP = {
    "Arthritis": {"range": "18-25 days", "source": "Domain expert case data (21-day real patient case)"},
    "Joint Pain": {"range": "18-30 days", "source": "Domain expert case data, extrapolated from arthritis/frozen shoulder cases"},
    "Sciatica": {"range": "18-25 days", "source": "Domain expert case data (21-day real patient case)"},
    "Back Pain": {"range": "18-30 days", "source": "Domain expert case data (nerve/joint-related protocol)"},
    "Stress": {"range": "25-35 days", "source": "Domain expert case data (1-month real patient case)"},
    "Anxiety": {"range": "25-35 days", "source": "Domain expert case data (1-month real patient case)"},
    "Liver Disease": {"range": "18-25 days", "source": "Domain expert case data (3-week real patient case)"},
    "Hypertension": {"range": "12-18 days", "source": "Market cross-check (Ayurveda Sarana Beach Hospital case)"},
    "Detox / Weight Management": {"range": "10-16 days", "source": "Market cross-check (Heritance Ayurveda case, 14 days)"},
    "General Wellness": {"range": "3-7 days", "source": "Standard short wellness package norm"},
    "Migraine": {"range": "14-30 days (tourist-adapted)", "source": "Literature (clinical protocol studies full course: 90 days)"},
    "Skin Condition": {"range": "14-30 days (tourist-adapted)", "source": "Literature (chronic protocol full course: up to 12 months)"},
}

OUTCOME_MAP = {
    "Arthritis": {"pct": 78, "n": "6 documented cases + literature (n=406 migraine study as reference class)"},
    "Joint Pain": {"pct": 75, "n": "extrapolated from arthritis/frozen shoulder case pattern"},
    "Sciatica": {"pct": 80, "n": "1 documented case (full recovery) + literature pattern"},
    "Back Pain": {"pct": 74, "n": "extrapolated from joint/nerve case pattern"},
    "Stress": {"pct": 70, "n": "1 documented case (symptom reduction) + general wellness literature"},
    "Anxiety": {"pct": 70, "n": "1 documented case (symptom reduction) + general wellness literature"},
    "Liver Disease": {"pct": 82, "n": "1 documented case (normalized report) at 3 weeks"},
    "Hypertension": {"pct": 68, "n": "market cross-check case, no controlled outcome data"},
    "Detox / Weight Management": {"pct": 72, "n": "market cross-check case (5kg reported) at 14 days"},
    "General Wellness": {"pct": 85, "n": "subjective relaxation outcomes, high self-report rate"},
    "Migraine": {"pct": 71, "n": "literature clinical protocol study (n=406, 90-day course)"},
    "Skin Condition": {"pct": 60, "n": "literature chronic-protocol study, longer course needed"},
}

RISK_KEYWORDS = [
    "unhygienic", "unhygenic", "dirty", "unclean", "unsafe", "uncomfortable", "unprofessional",
    "vulnerable", "exposed", "avoid", "not recommend", "be careful", "beware", "warning",
    "rude", "scam", "overpriced", "inconsistent pricing", "inconsistent"
]


# ---------------------------------------------------------------
# 2. Dosha Classification Model (Random Forest, from Step 4)
# ---------------------------------------------------------------
FEATURE_COLS = ["Age", "Gender", "Sleep Pattern", "Digestion/Appetite",
                 "Cold/Heat Sensitivity", "Emotional Tendency"]


def _synthetic_training_data():
    """Fallback training set aligned with the wellness quiz labels.

    Used when tourist_profiles_training_data.xlsx is not present so the
    matching service still boots inside the unified Tour Ceylon backend.
    """
    sleeps = [
        "Light/disturbed sleep",
        "Moderate sleep, wakes if hot",
        "Deep/heavy sleep",
    ]
    appetites = ["Variable appetite", "Strong/sharp appetite", "Slow digestion"]
    sensitivities = [
        "Sensitive to cold",
        "Sensitive to heat",
        "Tolerates temperature well",
    ]
    emotions = [
        "Anxious, overthinking",
        "Irritable when unwell",
        "Calm but sluggish",
    ]
    vata = {
        "sleep": sleeps[0],
        "appetite": appetites[0],
        "sensitivity": sensitivities[0],
        "emotion": emotions[0],
    }
    pitta = {
        "sleep": sleeps[1],
        "appetite": appetites[1],
        "sensitivity": sensitivities[1],
        "emotion": emotions[1],
    }
    kapha = {
        "sleep": sleeps[2],
        "appetite": appetites[2],
        "sensitivity": sensitivities[2],
        "emotion": emotions[2],
    }
    profiles = [("Vata", vata), ("Pitta", pitta), ("Kapha", kapha)]
    rows = []
    rng = np.random.default_rng(RANDOM_STATE)
    for dosha, traits in profiles:
        for _ in range(80):
            row = {
                "Age": int(rng.integers(18, 81)),
                "Gender": str(rng.choice(["F", "M"])),
                "Sleep Pattern": traits["sleep"] if rng.random() > 0.12 else str(rng.choice(sleeps)),
                "Digestion/Appetite": traits["appetite"] if rng.random() > 0.12 else str(rng.choice(appetites)),
                "Cold/Heat Sensitivity": traits["sensitivity"] if rng.random() > 0.12 else str(rng.choice(sensitivities)),
                "Emotional Tendency": traits["emotion"] if rng.random() > 0.12 else str(rng.choice(emotions)),
                "Primary Dosha (Vikruti)": dosha,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def _load_training_frame():
    xlsx = os.path.join(DATA_DIR, "tourist_profiles_training_data.xlsx")
    csv_path = os.path.join(DATA_DIR, "tourist_profiles_training_data.csv")
    if os.path.exists(xlsx):
        df = pd.read_excel(xlsx)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = _synthetic_training_data()
    return df[df["Primary Dosha (Vikruti)"] != "Balanced (N/A)"].copy()


_df = _load_training_frame()
_X = _df[FEATURE_COLS].copy()
_y = _df["Primary Dosha (Vikruti)"].copy()

_encoders = {}
for col in FEATURE_COLS[1:]:
    le = LabelEncoder()
    _X[col] = le.fit_transform(_X[col].astype(str))
    _encoders[col] = le

_y_encoder = LabelEncoder()
_y_enc = _y_encoder.fit_transform(_y)

DOSHA_MODEL = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
DOSHA_MODEL.fit(_X, _y_enc)


def predict_dosha(age, gender, sleep, appetite, sensitivity, emotion):
    row = pd.DataFrame([[age, gender, sleep, appetite, sensitivity, emotion]], columns=FEATURE_COLS)
    for col in FEATURE_COLS[1:]:
        known = set(_encoders[col].classes_)
        val = row[col].iloc[0]
        if val not in known:
            row[col] = _encoders[col].classes_[0]
        row[col] = _encoders[col].transform(row[col].astype(str))
    pred_idx = DOSHA_MODEL.predict(row)[0]
    proba = DOSHA_MODEL.predict_proba(row)[0]
    dosha = _y_encoder.inverse_transform([pred_idx])[0]
    confidence = round(float(max(proba)) * 100, 1)
    return dosha, confidence


# ---------------------------------------------------------------
# 3. Path filtering
# ---------------------------------------------------------------
def get_path_pool(path):
    if path == "spiritual":
        return [c for c in POOL if c["category"] == "Spiritual/Meditation"]
    return [c for c in POOL if c["category"] != "Spiritual/Meditation"]


# ---------------------------------------------------------------
# 4. Risk flag detection
# ---------------------------------------------------------------
def detect_risk_flags(reviews):
    if not reviews:
        return []
    flagged = []
    for text in reviews:
        lower = text.lower()
        if any(k in lower for k in RISK_KEYWORDS):
            flagged.append(text)
    return flagged


# ---------------------------------------------------------------
# 5. Duration / Outcome lookups
# ---------------------------------------------------------------
def get_duration_info(condition):
    return DURATION_MAP.get(condition, {"range": "Varies - ask center directly", "source": "Not yet mapped in duration dataset"})


def get_outcome_info(condition):
    return OUTCOME_MAP.get(condition)


# ---------------------------------------------------------------
# 6. Cost estimation
# ---------------------------------------------------------------
def get_rate_per_day(price_tier):
    t = (price_tier or "").lower()
    if "budget" in t and "mid" in t:
        return 12.5
    if "premium" in t:
        return 20
    if "budget" in t:
        return 10
    return 15


def parse_duration_range(range_str):
    nums = [int(n) for n in re.findall(r"\d+", range_str)]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def get_cost_estimate(condition, price_tier, travelers=1):
    d = get_duration_info(condition)
    min_days, max_days = parse_duration_range(d["range"])
    if min_days is None:
        return None
    rate = get_rate_per_day(price_tier)
    return {
        "min_cost": round(min_days * rate * travelers),
        "max_cost": round(max_days * rate * travelers),
        "min_days": min_days, "max_days": max_days,
        "rate": rate, "travelers": travelers,
    }


# ---------------------------------------------------------------
# 7. Typical session pattern (spiritual) / offers (ayurveda)
# ---------------------------------------------------------------
def get_session_schedule(center):
    text = (center.get("name", "") + " " + center.get("conditions_text", "")).lower()
    if "vipassana" in text:
        return {
            "pattern": "10-day silent courses, typically starting on the 1st and 15th of each month",
            "note": "Vipassana centers following the Goenka tradition generally run fixed-length courses on a recurring monthly cycle.",
            "cta": "Confirm exact upcoming dates directly with the center",
        }
    if any(k in text for k in ["forest monastery", "aranya", "hermitage"]):
        return {
            "pattern": "Flexible-duration stays - no fixed intake dates",
            "note": "Forest monasteries typically accept practitioners on a rolling basis rather than scheduled courses.",
            "cta": "Contact ahead to arrange your stay and confirm house rules",
        }
    return {
        "pattern": "Guided sessions typically offered weekly (often weekend mornings)",
        "note": "General meditation centers commonly run shorter, drop-in-friendly sessions.",
        "cta": "Check with the center for this week's session times",
    }


AYURVEDA_OFFERS = {
    "Curative": ["Daily Yoga & Breathing Sessions", "Doctor-Supervised Treatment Rooms",
                 "Personalized Herbal Preparation", "Traditional Welcome Ritual"],
    "Wellness/Rejuvenative": ["Relaxation & Spa Packages", "Morning Yoga Sessions",
                              "Herbal Welcome Drink", "Therapist-Guided Massage"],
}


def get_ayurveda_offers(category):
    return AYURVEDA_OFFERS.get(category, AYURVEDA_OFFERS["Wellness/Rejuvenative"])


# ---------------------------------------------------------------
# 8. Core matching function
# ---------------------------------------------------------------
def match_centers(condition, dosha, budget_tier, top_n=6, companion_condition=None, path="ayurveda"):
    pool = get_path_pool(path)
    scored = []
    for c in pool:
        cond_match = 1.0 if condition.lower() in c["conditions_text"].lower() else 0.3
        if c["dosha_focus"] == dosha:
            dosha_match = 1.0
        elif c["dosha_focus"] == "General/Unspecified":
            dosha_match = 0.6
        else:
            dosha_match = 0.4
        quality = c["nlp_quality"] / 5.0
        budget_match = 1.0 if budget_tier in c["price_tier"] else 0.5

        score = (WEIGHTS["condition"] * cond_match + WEIGHTS["dosha"] * dosha_match +
                 WEIGHTS["quality"] * quality + WEIGHTS["budget"] * budget_match)

        companion_match = None
        if companion_condition:
            companion_match = 1.0 if companion_condition.lower() in c["conditions_text"].lower() else 0.3

        combined_score = (0.65 * score + 0.35 * companion_match) if companion_match is not None else score

        entry = dict(c)  # copy all enriched fields through (verified, notes, address, district, etc.)
        entry.update({
            "match_pct": round(score * 100),
            "condition_pct": round(cond_match * WEIGHTS["condition"] * 100),
            "dosha_pct": round(dosha_match * WEIGHTS["dosha"] * 100),
            "quality_pct": round(quality * WEIGHTS["quality"] * 100),
            "budget_pct": round(budget_match * WEIGHTS["budget"] * 100),
            "queried_condition": condition,
            "companion_condition": companion_condition,
            "companion_match": companion_match,
            "combined_pct": round(combined_score * 100),
            "risk_flags": detect_risk_flags(c.get("reviews", [])),
        })
        scored.append(entry)

    scored.sort(key=lambda r: r["combined_pct"] if companion_condition else r["match_pct"], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    # Worked example matching the JS demo's "Hans" scenario
    dosha, confidence = predict_dosha(52, "M", "Light/disturbed sleep", "Variable appetite",
                                        "Sensitive to cold", "Restless under stress")
    print(f"Predicted dosha: {dosha} ({confidence}% confidence)\n")

    results = match_centers("Arthritis", dosha, "Mid", top_n=3, path="ayurveda")
    for i, r in enumerate(results, 1):
        print(f"#{i} {r['name']} - {r['match_pct']}% match")
        print(f"   Verified: {r['verified']} | District: {r['district']}")
        if r["risk_flags"]:
            print(f"   RISK FLAGS: {len(r['risk_flags'])} flagged review(s)")
        d = get_duration_info(r["queried_condition"])
        o = get_outcome_info(r["queried_condition"])
        print(f"   Duration: {d['range']} | Outcome: ~{o['pct']}%" if o else f"   Duration: {d['range']}")
        cost = get_cost_estimate(r["queried_condition"], r["price_tier"])
        if cost:
            print(f"   Est. cost: ${cost['min_cost']}-${cost['max_cost']} ({cost['travelers']} traveler)")
        print()


# ---------------------------------------------------------------
# 9. Admin: persistence, analytics, review moderation
# ---------------------------------------------------------------
def save_pool():
    """Writes the current in-memory POOL back to disk so admin edits persist."""
    with open(os.path.join(DATA_DIR, "full_candidate_pool.json"), "w", encoding="utf-8") as f:
        json.dump(POOL, f, indent=2)


def get_analytics():
    category_counts = {}
    dosha_counts = {}
    tier_counts = {}
    quality_scores = []
    for c in POOL:
        category_counts[c["category"]] = category_counts.get(c["category"], 0) + 1
        dosha_counts[c["dosha_focus"]] = dosha_counts.get(c["dosha_focus"], 0) + 1
        tier_counts[c["price_tier"]] = tier_counts.get(c["price_tier"], 0) + 1
        quality_scores.append(c["nlp_quality"])

    total_flagged_reviews = sum(len(detect_risk_flags(c.get("reviews", []))) for c in POOL)
    centers_with_flags = sum(1 for c in POOL if detect_risk_flags(c.get("reviews", [])))

    # Real evaluation study results, computed during model development (Steps 4 + ablation study)
    model_comparison = None
    ablation = None
    try:
        import csv
        with open(os.path.join(DATA_DIR, "model_comparison_results.csv")) as f:
            model_comparison = list(csv.DictReader(f))
    except FileNotFoundError:
        pass
    try:
        with open(os.path.join(DATA_DIR, "ablation_results.json")) as f:
            ablation = json.load(f)
    except FileNotFoundError:
        pass

    return {
        "total_centers": len(POOL),
        "category_counts": category_counts,
        "dosha_counts": dosha_counts,
        "price_tier_counts": tier_counts,
        "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else None,
        "total_flagged_reviews": total_flagged_reviews,
        "centers_with_flags": centers_with_flags,
        "model_comparison": model_comparison,
        "ablation_study": ablation,
    }


def get_flagged_centers():
    results = []
    for c in POOL:
        flags = detect_risk_flags(c.get("reviews", []))
        if flags:
            results.append({
                "name": c["name"], "category": c["category"], "district": c.get("district"),
                "flagged_reviews": flags, "total_reviews": len(c.get("reviews", []))
            })
    return results
