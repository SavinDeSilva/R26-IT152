import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report, balanced_accuracy_score, accuracy_score

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
X_train, y_train = train_df[NUMERIC_FEATURES+CATEGORICAL_FEATURES], train_df["risk_level"]
X_test, y_test = test_df[NUMERIC_FEATURES+CATEGORICAL_FEATURES], test_df["risk_level"]

pre = ColumnTransformer([('num', 'passthrough', NUMERIC_FEATURES),
                          ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)])

for weight_mode in [None, 'balanced', 'balanced_subsample']:
    clf = Pipeline([('pre', pre), ('model', RandomForestClassifier(
        n_estimators=100, max_depth=12, min_samples_split=7,
        random_state=42, class_weight=weight_mode))])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print(f"\n=== class_weight={weight_mode} ===")
    print(f"accuracy={accuracy_score(y_test,y_pred):.4f}  balanced_accuracy={balanced_accuracy_score(y_test,y_pred):.4f}")
    print(classification_report(y_test, y_pred))
