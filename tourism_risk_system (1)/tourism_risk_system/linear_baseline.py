import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, balanced_accuracy_score, classification_report

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
X_train, y_train_score = train_df[NUMERIC_FEATURES+CATEGORICAL_FEATURES], train_df["crowd_score_normalized"]
X_test, y_test_score = test_df[NUMERIC_FEATURES+CATEGORICAL_FEATURES], test_df["crowd_score_normalized"]
y_train_risk, y_test_risk = train_df["risk_level"], test_df["risk_level"]

pre = ColumnTransformer([
    ('num', StandardScaler(), NUMERIC_FEATURES),
    ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
])

# Linear Regression baseline (crowd_score)
lr_pipe = Pipeline([('pre', pre), ('model', LinearRegression())])
lr_pipe.fit(X_train, y_train_score)
y_pred_score = lr_pipe.predict(X_test)
print("=== Linear Regression (site-holdout) ===")
print(f"MAE={mean_absolute_error(y_test_score, y_pred_score):.4f}  R2={r2_score(y_test_score, y_pred_score):.4f}")

# Logistic Regression baseline (risk_level)
log_pipe = Pipeline([('pre', pre), ('model', LogisticRegression(max_iter=1000, class_weight='balanced'))])
log_pipe.fit(X_train, y_train_risk)
y_pred_risk = log_pipe.predict(X_test)
print("\n=== Logistic Regression (site-holdout) ===")
print(f"accuracy={accuracy_score(y_test_risk, y_pred_risk):.4f}  balanced_accuracy={balanced_accuracy_score(y_test_risk, y_pred_risk):.4f}")
print(classification_report(y_test_risk, y_pred_risk))
