import pickle
import pandas as pd
import matplotlib.pyplot as plt

with open("models/rf_regressor.pkl", "rb") as f:
    rf_regressor = pickle.load(f)

FEATURES = [
    'day_of_week', 'month', 'is_weekend', 'is_public_holiday',
    'is_festival_period', 'avg_temperature_c', 'avg_rainfall_mm',
    'daily_flights_at_cmb', 'capacity_per_day', 'category_encoded',
    'season_encoded', 'district_encoded', 'is_eco_friendly',
    'is_unesco', 'entrance_fee_lkr'
]

importance_df = pd.DataFrame({
    'feature': FEATURES,
    'importance': rf_regressor.feature_importances_
}).sort_values('importance', ascending=True)

colors = ['#3b82f6' if f == 'daily_flights_at_cmb' else '#6366f1'
          for f in importance_df['feature']]

fig, ax = plt.subplots(figsize=(7, 6))
bars = ax.barh(importance_df['feature'], importance_df['importance'], color=colors)
ax.set_xlabel('Feature Importance Score (Gini)', fontsize=13)
ax.set_title('Random Forest Feature Importance', fontsize=14)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=11)

for bar, val in zip(bars, importance_df['importance']):
    ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
             f'{val:.3f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig("outputs/feature_importance_ieee.png", dpi=300, bbox_inches='tight')
print("Saved outputs/feature_importance_ieee.png")