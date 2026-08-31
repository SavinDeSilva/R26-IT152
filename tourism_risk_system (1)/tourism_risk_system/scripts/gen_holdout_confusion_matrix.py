import pandas as pd
import pickle
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, balanced_accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load data ---
df = pd.read_csv('data/master_dataset_fixed.csv')
print(f"Full dataset: {len(df)} rows, {df['site_name'].nunique()} sites")

HOLDOUT_SITE_NAMES = [
    "Bentota Beach", "Bundala National Park", "Colombo Lotus Tower",
    "Kalpitiya Beach", "Kande Viharaya", "Kandy Lake",
    "Minneriya National Park", "Pasikuda Beach", "Tangalle Beach",
    "Wilpattu National Park"
]

missing = [s for s in HOLDOUT_SITE_NAMES if s not in df["site_name"].unique()]
if missing:
    print(f"WARNING - these holdout names not found in site_name column: {missing}")
    print("Actual site_name values (sample):", df["site_name"].unique()[:10])
    raise SystemExit("Fix the name list before continuing - don't guess past this.")

holdout_df = df[df["site_name"].isin(HOLDOUT_SITE_NAMES)].copy()
print(f"Holdout set: {len(holdout_df)} rows across {holdout_df['site_name'].nunique()} sites")

with open("models/risk_pipeline.pkl", "rb") as f:
    risk_pipeline = pickle.load(f)
print(f"risk_pipeline type: {type(risk_pipeline)}")

if hasattr(risk_pipeline, "feature_names_in_"):
    expected_features = list(risk_pipeline.feature_names_in_)
    print(f"Pipeline expects {len(expected_features)} features: {expected_features}")
else:
    print("Pipeline has no feature_names_in_ - inspect manually before proceeding.")
    expected_features = None

y_true_raw = holdout_df["risk_level"]
print(f"y_true_raw sample values: {y_true_raw.unique()}")

for enc_path in ["models/risk_label_encoder.pkl", "models/risk_encoder.pkl"]:
    try:
        with open(enc_path, "rb") as f:
            enc = pickle.load(f)
        print(f"{enc_path} classes_: {getattr(enc, 'classes_', 'no classes_ attr')}")
    except Exception as e:
        print(f"{enc_path}: failed to load - {e}")

with open("models/risk_label_encoder.pkl", "rb") as f:
    le_risk = pickle.load(f)
if not set(le_risk.classes_) >= set(y_true_raw.unique()):
    print("risk_label_encoder.pkl classes don't cover actual values - trying risk_encoder.pkl instead")
    with open("models/risk_encoder.pkl", "rb") as f:
        le_risk = pickle.load(f)

if expected_features is not None:
    X_holdout = holdout_df[expected_features]
else:
    raise SystemExit("Can't safely build X without confirmed feature list - inspect train_model.py's "
                      "feature-building step and hardcode the column list here instead of guessing.")

y_pred_encoded = risk_pipeline.predict(X_holdout)
y_true_encoded = le_risk.transform(y_true_raw)

acc = accuracy_score(y_true_encoded, y_pred_encoded)
bal_acc = balanced_accuracy_score(y_true_encoded, y_pred_encoded)
print(f"\nSite-holdout accuracy: {acc:.4f}")
print(f"Site-holdout balanced accuracy: {bal_acc:.4f}")
print("Compare against logged values: acc=0.7731, balanced_acc=0.5754")
if abs(acc - 0.7731) > 0.01 or abs(bal_acc - 0.5754) > 0.01:
    print("!! MISMATCH with logged numbers - do not use this output until you know why !!")
else:
    print("Matches logged numbers within tolerance - safe to proceed.")

labels_encoded = sorted(set(y_true_encoded.tolist() + y_pred_encoded.tolist()))
label_names = le_risk.inverse_transform(labels_encoded)

cm = confusion_matrix(y_true_encoded, y_pred_encoded, labels=labels_encoded)
print(f"\nConfusion matrix (order {list(label_names)}):\n{cm}")
print(f"Total: {cm.sum()} (should equal len(holdout_df) = {len(holdout_df)})")

plt.figure(figsize=(9, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=label_names, yticklabels=label_names,
            annot_kws={"weight": "bold"})
plt.title("Confusion Matrix - Risk Level Classification (site-holdout)\nTourism Risk & Context Intelligence System")
plt.xlabel("Predicted Risk Level")
plt.ylabel("Actual Risk Level")
plt.tight_layout()
plt.savefig("outputs/confusion_matrix_site_holdout.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/confusion_matrix_site_holdout.png")