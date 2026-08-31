import pandas as pd
import pickle
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("data/master_dataset.csv")
holdout_names = ["Bentota Beach", "Bundala National Park", "Colombo Lotus Tower",
                  "Kalpitiya Beach", "Kande Viharaya", "Kandy Lake",
                  "Minneriya National Park", "Pasikuda Beach", "Tangalle Beach",
                  "Wilpattu National Park"]
holdout_df = df[df["site_name"].isin(holdout_names)]

with open("models/risk_pipeline.pkl", "rb") as f:
    pipeline = pickle.load(f)
with open("models/risk_label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

NUMERIC_FEATURES = ['day_of_week', 'month', 'is_weekend', 'is_public_holiday', 'is_festival_period',
    'avg_temperature_c', 'avg_rainfall_mm', 'daily_flights_at_cmb', 'hotel_occupancy_rate',
    'capacity_per_day', 'is_eco_friendly', 'is_unesco', 'entrance_fee_lkr']
CATEGORICAL_FEATURES = ['category', 'season', 'district']
X_holdout = holdout_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y_true = holdout_df["risk_level"]

y_pred_encoded = pipeline.predict(X_holdout)
y_pred = le.inverse_transform(y_pred_encoded) if y_pred_encoded.dtype != object else y_pred_encoded

print("Classification report on SITE-HOLDOUT set:")
print(classification_report(y_true, y_pred))
print("\nConfusion matrix (rows=true, cols=pred), labels order:", sorted(y_true.unique()))
print(confusion_matrix(y_true, y_pred, labels=sorted(y_true.unique())))

print("\nPer-site accuracy:")
for name in holdout_names:
    mask = holdout_df["site_name"] == name
    site_true = y_true[mask]
    site_pred = pd.Series(y_pred, index=holdout_df.index)[mask]
    acc = (site_true == site_pred).mean()
    print(f"  {name}: {acc:.3f}  (n={mask.sum()})")
