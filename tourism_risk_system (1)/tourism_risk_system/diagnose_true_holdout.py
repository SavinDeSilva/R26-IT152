import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("data/master_dataset.csv")
holdout_names = ["Bentota Beach", "Bundala National Park", "Colombo Lotus Tower",
                  "Kalpitiya Beach", "Kande Viharaya", "Kandy Lake",
                  "Minneriya National Park", "Pasikuda Beach", "Tangalle Beach",
                  "Wilpattu National Park"]

NUMERIC_FEATURES = ['day_of_week', 'month', 'is_weekend', 'is_public_holiday', 'is_festival_period',
    'avg_temperature_c', 'avg_rainfall_mm', 'daily_flights_at_cmb', 'hotel_occupancy_rate',
    'capacity_per_day', 'is_eco_friendly', 'is_unesco', 'entrance_fee_lkr']
CATEGORICAL_FEATURES = ['category', 'season', 'district']

is_holdout = df["site_name"].isin(holdout_names)
train_df = df[~is_holdout]
test_df = df[is_holdout]

pre = ColumnTransformer([('num', 'passthrough', NUMERIC_FEATURES),
                          ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)])
clf = Pipeline([('pre', pre), ('model', RandomForestClassifier(
    n_estimators=100, max_depth=12, min_samples_split=7, random_state=42))])

X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y_train = train_df["risk_level"]
X_test = test_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
y_test = test_df["risk_level"]

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("Classification report on TRUE site-holdout (fit on 87 sites, eval on 10):")
print(classification_report(y_test, y_pred))
print("Confusion matrix, labels order:", sorted(y_test.unique()))
print(confusion_matrix(y_test, y_pred, labels=sorted(y_test.unique())))

print("\nPer-site accuracy:")
for name in holdout_names:
    mask = test_df["site_name"] == name
    site_true = y_test[mask]
    site_pred = pd.Series(y_pred, index=test_df.index)[mask]
    acc = (site_true == site_pred).mean()
    print(f"  {name}: {acc:.3f}  (n={mask.sum()})")
