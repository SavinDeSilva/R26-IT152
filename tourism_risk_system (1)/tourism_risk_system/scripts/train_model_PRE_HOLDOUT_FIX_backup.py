import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (mean_absolute_error, r2_score, accuracy_score,
                              balanced_accuracy_score, classification_report, confusion_matrix)
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap
import pickle
import json
import os
import sys
import platform
import sklearn
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Feature groups
# Numeric features are passed through unchanged.
# Categorical features go through OneHotEncoder(handle_unknown="ignore") instead
# of LabelEncoder. Two reasons this matters (both verified empirically on this
# dataset, not just theoretical):
#   1. LabelEncoder assigns an arbitrary integer order to nominal categories
#      (category, season, district). A tree-based model's splits are threshold
#      comparisons ("<= 1.5"), so that arbitrary order changes which subsets of
#      categories a shallow tree can separate in a few splits. On this exact
#      dataset, re-fitting LabelEncoder with a different (but equally valid)
#      alphabetical ordering moved the site-holdout R^2 from 0.68 to 0.91 with
#      NO other change -- that's encoding-order noise, not real model skill.
#      OneHotEncoder removes that ordering artifact and gives a stable ~0.89.
#   2. An unseen category/district at inference time silently becomes "0" with
#      LabelEncoder (i.e. whatever category happened to be assigned label 0),
#      which is a real bug for a live tourism app that may see place data it
#      wasn't trained on. handle_unknown="ignore" instead encodes it as an
#      all-zero row, which is honest and doesn't fabricate a category.
NUMERIC_FEATURES = [
    'day_of_week', 'month', 'is_weekend', 'is_public_holiday', 'is_festival_period',
    'avg_temperature_c', 'avg_rainfall_mm', 'daily_flights_at_cmb', 'hotel_occupancy_rate',
    'capacity_per_day', 'is_eco_friendly', 'is_unesco', 'entrance_fee_lkr'
]
CATEGORICAL_FEATURES = ['category', 'season', 'district']
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

DATA_PATH = r"C:\Users\ASUS\OneDrive - Sri Lanka Institute of Information Technology\Desktop\tourism_risk_system\data\master_dataset.csv"

# Anchor all outputs to the project root regardless of the current working
# directory the script is launched from (e.g. `python train_model.py` run
# from inside scripts\ vs from the project root). This script lives in
# scripts\, so the project root is one directory up.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")


def make_preprocessor():
    return ColumnTransformer([
        ('num', 'passthrough', NUMERIC_FEATURES),
        ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
    ])


def train_model():
    print("=" * 60)
    print("TOURISM RISK SYSTEM - MODEL TRAINING REPORT (v2, pipeline-based)")
    print("=" * 60)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    # STEP 1: LOAD DATA
    print("\n[STEP 1] Loading master dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Total records: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")

    # STEP 2: TARGET ENCODING (target only - features use OneHotEncoder below)
    print("\n[STEP 2] Encoding target label...")
    le_risk = LabelEncoder()
    df['risk_encoded'] = le_risk.fit_transform(df['risk_level'])
    print(f"  Risk classes: {list(le_risk.classes_)}")

    X = df[ALL_FEATURES]
    y_score = df['crowd_score_normalized']
    y_risk = df['risk_encoded']
    print(f"  Feature matrix shape: {X.shape}  ({len(NUMERIC_FEATURES)} numeric + {len(CATEGORICAL_FEATURES)} categorical)")

    # STEP 3: RANDOM 80/20 SPLIT (secondary metric - see note below)
    print("\n[STEP 3] Random 80/20 split (secondary metric)...")
    X_train, X_test, y_score_train, y_score_test = train_test_split(X, y_score, test_size=0.2, random_state=42)
    _, _, y_risk_train, y_risk_test = train_test_split(X, y_risk, test_size=0.2, random_state=42)
    print(f"  Training set: {len(X_train)} records")
    print(f"  Test set:     {len(X_test)} records")

    # STEP 3b: SITE-HOLDOUT SPLIT (PRIMARY metric - see docstring above)
    # crowd_score_normalized is generated in simulate_crowd_data.py as a formula
    # of (annual_visitors, capacity_per_day, season, is_weekend, is_public_holiday)
    # + noise. Several of those exact ingredients are also model features, so a
    # random row split lets the model partly recover the generating formula and
    # memorize each site's own multiplier pattern rather than proving it
    # generalizes. Holding out entire destinations is the only split that tests
    # generalization to a site the model has never seen.
    print("\n[STEP 3b] Site-holdout split (PRIMARY metric - unseen destinations)...")
    all_site_ids = df['site_id'].unique()
    rng = np.random.RandomState(42)
    rng.shuffle(all_site_ids)
    n_holdout = max(1, int(len(all_site_ids) * 0.2))
    holdout_sites = set(all_site_ids[:n_holdout])
    site_train_mask = ~df['site_id'].isin(holdout_sites)
    site_test_mask = df['site_id'].isin(holdout_sites)

    X_site_train, y_score_site_train = X[site_train_mask], y_score[site_train_mask]
    X_site_test, y_score_site_test = X[site_test_mask], y_score[site_test_mask]
    y_risk_site_train, y_risk_site_test = y_risk[site_train_mask], y_risk[site_test_mask]

    print(f"  Train sites: {df.loc[site_train_mask, 'site_id'].nunique()} ({site_train_mask.sum()} rows)")
    print(f"  Held-out (unseen) sites: {df.loc[site_test_mask, 'site_id'].nunique()} ({site_test_mask.sum()} rows)")
    print(f"  Held-out site names: {sorted(df.loc[site_test_mask, 'site_name'].unique())}")

    # STEP 4: BASELINE MODEL
    print("\n[STEP 4] Baseline (mean predictor)...")
    baseline_pred = np.full(len(y_score_test), y_score_train.mean())
    baseline_mae = mean_absolute_error(y_score_test, baseline_pred)
    baseline_r2 = r2_score(y_score_test, baseline_pred)
    print(f"  Baseline MAE: {baseline_mae:.4f}  R2: {baseline_r2:.4f}")

    # STEP 5: GRID SEARCH (on random-split training data, pipeline-aware)
    print("\n[STEP 5] Hyperparameter tuning with Grid Search (pipeline)...")
    param_grid = {
        'model__n_estimators': [50, 100, 150],
        'model__max_depth': [8, 10, 12],
        'model__min_samples_split': [3, 5, 7]
    }
    reg_pipeline = Pipeline([
        ('pre', make_preprocessor()),
        ('model', RandomForestRegressor(random_state=42, n_jobs=-1))
    ])
    grid_search = GridSearchCV(reg_pipeline, param_grid, cv=3,
                                scoring='neg_mean_absolute_error', n_jobs=-1, verbose=0)
    grid_search.fit(X_train, y_score_train)
    best_params = {k.replace('model__', ''): v for k, v in grid_search.best_params_.items()}
    print(f"  Best hyperparameters: {best_params}")
    print(f"  Best CV MAE (random split): {-grid_search.best_score_:.4f}")

    def make_regressor():
        return RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)

    def make_classifier():
        return RandomForestClassifier(**best_params, random_state=42, n_jobs=-1)

    # STEP 6: FIT FINAL PIPELINES on random-split training data (deployment models)
    print("\n[STEP 6] Fitting deployment pipelines on random-split training data...")
    crowd_pipeline = Pipeline([('pre', make_preprocessor()), ('model', make_regressor())])
    crowd_pipeline.fit(X_train, y_score_train)
    y_pred_score = crowd_pipeline.predict(X_test)
    mae = mean_absolute_error(y_score_test, y_pred_score)
    r2 = r2_score(y_score_test, y_pred_score)

    y_pred_score_train = crowd_pipeline.predict(X_train)
    train_mae = mean_absolute_error(y_score_train, y_pred_score_train)
    train_r2 = r2_score(y_score_train, y_pred_score_train)
    print(f"  Random-split test  MAE={mae:.4f} R2={r2:.4f}")
    print(f"  Random-split train MAE={train_mae:.4f} R2={train_r2:.4f}")

    risk_pipeline = Pipeline([('pre', make_preprocessor()), ('model', make_classifier())])
    risk_pipeline.fit(X_train, y_risk_train)
    y_pred_risk = risk_pipeline.predict(X_test)
    y_pred_risk_train = risk_pipeline.predict(X_train)
    train_accuracy = accuracy_score(y_risk_train, y_pred_risk_train)
    test_accuracy = accuracy_score(y_risk_test, y_pred_risk)
    test_balanced_accuracy = balanced_accuracy_score(y_risk_test, y_pred_risk)
    print(f"  Random-split classification: train_acc={train_accuracy:.4f} test_acc={test_accuracy:.4f} balanced_acc={test_balanced_accuracy:.4f}")
    print("\n" + classification_report(y_risk_test, y_pred_risk, target_names=le_risk.classes_))

    # STEP 7: 5-FOLD CROSS VALIDATION (pipeline-aware, no leakage across folds)
    print("\n[STEP 7] 5-fold cross-validation (pipeline refit per fold)...")
    cv_pipeline = Pipeline([('pre', make_preprocessor()), ('model', make_regressor())])
    cv_mae_scores = cross_val_score(cv_pipeline, X, y_score, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
    cv_r2_scores = cross_val_score(cv_pipeline, X, y_score, cv=5, scoring='r2', n_jobs=-1)
    cv_mae, cv_mae_std = -cv_mae_scores.mean(), cv_mae_scores.std()
    cv_r2, cv_r2_std = cv_r2_scores.mean(), cv_r2_scores.std()
    print(f"  CV MAE: {cv_mae:.4f} (+/- {cv_mae_std:.4f})")
    print(f"  CV R2:  {cv_r2:.4f} (+/- {cv_r2_std:.4f})")

    # STEP 8: SITE-HOLDOUT EVALUATION (PRIMARY metric, same hyperparameters)
    print("\n[STEP 8] Site-holdout evaluation (PRIMARY metric)...")
    site_reg_pipeline = Pipeline([('pre', make_preprocessor()), ('model', make_regressor())])
    site_reg_pipeline.fit(X_site_train, y_score_site_train)
    y_pred_site = site_reg_pipeline.predict(X_site_test)
    site_holdout_mae = mean_absolute_error(y_score_site_test, y_pred_site)
    site_holdout_r2 = r2_score(y_score_site_test, y_pred_site)
    site_holdout_baseline_mae = mean_absolute_error(y_score_site_test, np.full(len(y_score_site_test), y_score_site_train.mean()))

    site_clf_pipeline = Pipeline([('pre', make_preprocessor()), ('model', make_classifier())])
    site_clf_pipeline.fit(X_site_train, y_risk_site_train)
    y_pred_risk_site = site_clf_pipeline.predict(X_site_test)
    site_holdout_accuracy = accuracy_score(y_risk_site_test, y_pred_risk_site)
    site_holdout_balanced_accuracy = balanced_accuracy_score(y_risk_site_test, y_pred_risk_site)

    print(f"  Site-holdout MAE: {site_holdout_mae:.4f}   (baseline MAE {site_holdout_baseline_mae:.4f})")
    print(f"  Site-holdout R2:  {site_holdout_r2:.4f}")
    print(f"  Site-holdout classification accuracy: {site_holdout_accuracy:.4f}  balanced: {site_holdout_balanced_accuracy:.4f}")
    print(f"  >>> THIS is the honest generalization number for unseen destinations. <<<")

    # STEP 9: CONFUSION MATRIX
    print("\n[STEP 9] Confusion matrix...")
    cm = confusion_matrix(y_risk_test, y_pred_risk)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, cmap='Blues')
    classes = le_risk.classes_
    ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, fontsize=12); ax.set_yticklabels(classes, fontsize=12)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=14, fontweight='bold',
                     color='white' if cm[i, j] > cm.max() / 2 else 'black')
    ax.set_xlabel('Predicted Risk Level'); ax.set_ylabel('Actual Risk Level')
    ax.set_title('Confusion Matrix - Risk Level Classification (random split)\nTourism Risk & Context Intelligence System')
    plt.colorbar(im); plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, "confusion_matrix.png"), dpi=150, bbox_inches='tight'); plt.close()
    print("  Saved: outputs/confusion_matrix.png")

    # STEP 10: ACTUAL VS PREDICTED PLOT
    print("\n[STEP 10] Actual vs predicted plot...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sample_size = min(500, len(y_score_test))
    idx = np.random.RandomState(0).choice(len(y_score_test), sample_size, replace=False)
    actual_sample = y_score_test.iloc[idx]
    predicted_sample = np.asarray(y_pred_score)[idx]
    axes[0].scatter(actual_sample, predicted_sample, alpha=0.4, color='#3b82f6', s=20)
    axes[0].plot([0, 1], [0, 1], 'r--', linewidth=2, label='Perfect prediction')
    axes[0].set_xlabel('Actual Crowd Score'); axes[0].set_ylabel('Predicted Crowd Score')
    axes[0].set_title(f'Actual vs Predicted (random split)\nMAE={mae:.4f}, R2={r2:.4f}')
    axes[0].legend(); axes[0].grid(True, alpha=0.3)

    models_ = ['Baseline\n(Mean)', 'RF - random\nsplit', 'RF - site\nholdout']
    mae_scores = [baseline_mae, mae, site_holdout_mae]
    r2_scores = [baseline_r2, r2, site_holdout_r2]
    x = np.arange(3); width = 0.35
    bars1 = axes[1].bar(x - width/2, mae_scores, width, label='MAE (lower=better)', color=['#ef4444', '#22c55e', '#f97316'])
    bars2 = axes[1].bar(x + width/2, r2_scores, width, label='R2 (higher=better)', color=['#f59e0b', '#3b82f6', '#a855f7'])
    axes[1].set_xticks(x); axes[1].set_xticklabels(models_, fontsize=10)
    axes[1].set_title('Baseline vs Random-split vs Site-holdout')
    axes[1].legend(); axes[1].grid(True, alpha=0.3, axis='y')
    for bar in list(bars1) + list(bars2):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                      f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, "actual_vs_predicted.png"), dpi=150, bbox_inches='tight'); plt.close()
    print("  Saved: outputs/actual_vs_predicted.png")

    # STEP 11: FEATURE IMPORTANCE (transformed/one-hot feature names)
    print("\n[STEP 11] Feature importance (post-encoding names)...")
    fitted_pre = crowd_pipeline.named_steps['pre']
    fitted_model = crowd_pipeline.named_steps['model']
    feature_names_out = list(fitted_pre.get_feature_names_out())
    importance_df = pd.DataFrame({
        'feature': feature_names_out,
        'importance': fitted_model.feature_importances_
    }).sort_values('importance', ascending=True).tail(25)

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(importance_df['feature'], importance_df['importance'], color='#6366f1')
    ax.set_xlabel('Feature Importance Score (Gini)')
    ax.set_title('Random Forest Feature Importance (top 25, post-OneHot)\nTourism Risk & Context Intelligence System')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS_DIR, "feature_importance.png"), dpi=150, bbox_inches='tight'); plt.close()
    print("  Saved: outputs/feature_importance.png")

    # STEP 12: SHAP (adapted for pipeline - transform first, explain final RF step)
    print("\n[STEP 12] SHAP analysis (pipeline-adapted)...")
    try:
        X_test_transformed = fitted_pre.transform(X_test.iloc[:200])
        if hasattr(X_test_transformed, "toarray"):
            X_test_transformed = X_test_transformed.toarray()
        explainer = shap.TreeExplainer(fitted_model)
        shap_values = explainer.shap_values(X_test_transformed)

        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names_out, show=False)
        plt.title("SHAP Feature Importance\nTourism Risk & Context Intelligence System")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUTS_DIR, "shap_summary_plot.png"), dpi=150, bbox_inches='tight'); plt.close()

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names_out, plot_type="bar", show=False)
        plt.title("SHAP Mean Feature Impact\nTourism Risk & Context Intelligence System")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUTS_DIR, "shap_bar_plot.png"), dpi=150, bbox_inches='tight'); plt.close()
        print("  Saved: outputs/shap_summary_plot.png, outputs/shap_bar_plot.png")
    except Exception as e:
        print(f"  WARNING: SHAP step failed ({e}); skipping SHAP outputs, everything else is unaffected.")

    # STEP 13: SAVE PIPELINES + METADATA
    print("\n[STEP 13] Saving pipelines and metadata...")
    with open(os.path.join(MODELS_DIR, "crowd_pipeline.pkl"), "wb") as f:
        pickle.dump(crowd_pipeline, f)
    with open(os.path.join(MODELS_DIR, "risk_pipeline.pkl"), "wb") as f:
        pickle.dump(risk_pipeline, f)
    with open(os.path.join(MODELS_DIR, "risk_label_encoder.pkl"), "wb") as f:
        pickle.dump(le_risk, f)

    metadata = {
        "model_version": "v3.0-pipeline",
        "training_timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "sklearn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "source_dataset": os.path.basename(DATA_PATH),
        "source_dataset_records": len(df),
        "feature_list_raw": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features_onehot": CATEGORICAL_FEATURES,
        "transformed_feature_count": len(feature_names_out),
        "target_definition": {
            "crowd_score_normalized": "SYNTHETIC. Formula: (annual_visitors/365 * season_mult * weekend_mult * holiday_mult * noise) / capacity_per_day, clipped to [0,1]. See simulate_crowd_data.py. Not an observed real-world value.",
            "risk_level": "Threshold of crowd_score_normalized (>=0.75 High, >=0.45 Medium, else Low)."
        },
        "target_leakage_note": (
            "is_weekend, is_public_holiday, season, and capacity_per_day are direct "
            "ingredients of the crowd_score_normalized generating formula and are also "
            "model features. hotel_occupancy_rate and daily_flights_at_cmb are independently "
            "generated from the same season_mult/is_weekend/is_holiday drivers with small "
            "added noise and act as secondary leakage channels. Random-split metrics below "
            "are inflated by this; site_holdout_evaluation is the metric that should be reported."
        ),
        "encoding_note": (
            "Switched from LabelEncoder to OneHotEncoder(handle_unknown='ignore') for "
            "category/season/district. Verified on this data that LabelEncoder's arbitrary "
            "integer ordering caused site-holdout R2 to swing between 0.68 and 0.91 for "
            "otherwise-identical models; OneHotEncoder gives a stable ~0.87-0.89 regardless "
            "of category ordering, and safely handles an unseen category/district at "
            "inference instead of silently mapping it to 0."
        ),
        "best_hyperparameters": best_params,
        "primary_reported_metric": "site_holdout",
        "site_holdout_evaluation": {
            "description": "Entire sites held out of training. Tests generalization to unseen destinations.",
            "train_sites": int(df.loc[site_train_mask, 'site_id'].nunique()),
            "test_sites": int(df.loc[site_test_mask, 'site_id'].nunique()),
            "held_out_site_names": sorted(df.loc[site_test_mask, 'site_name'].unique().tolist()),
            "train_records": int(site_train_mask.sum()),
            "test_records": int(site_test_mask.sum()),
            "regression_mae": round(site_holdout_mae, 4),
            "regression_r2": round(site_holdout_r2, 4),
            "regression_baseline_mae": round(site_holdout_baseline_mae, 4),
            "classification_accuracy": round(site_holdout_accuracy, 4),
            "classification_balanced_accuracy": round(site_holdout_balanced_accuracy, 4)
        },
        "random_split_evaluation": {
            "description": "Random 80/20 row split. Same sites appear in train and test - inflated by site-level memorization AND target-formula leakage. Do not report as primary metric.",
            "train_records": len(X_train),
            "test_records": len(X_test),
            "regression_mae": round(mae, 4),
            "regression_r2": round(r2, 4),
            "regression_train_mae": round(train_mae, 4),
            "regression_train_r2": round(train_r2, 4),
            "classification_train_accuracy": round(train_accuracy, 4),
            "classification_test_accuracy": round(test_accuracy, 4),
            "classification_test_balanced_accuracy": round(test_balanced_accuracy, 4),
            "baseline_mae": round(baseline_mae, 4),
            "baseline_r2": round(baseline_r2, 4),
            "cv_mae": round(cv_mae, 4),
            "cv_mae_std": round(cv_mae_std, 4),
            "cv_r2": round(cv_r2, 4),
            "cv_r2_std": round(cv_r2_std, 4)
        },
        "risk_classes": list(le_risk.classes_)
    }
    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    with open(os.path.join(MODELS_DIR, "model_metrics.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("  Saved: models/crowd_pipeline.pkl, models/risk_pipeline.pkl,")
    print("         models/risk_label_encoder.pkl, models/model_metadata.json (+ model_metrics.json alias)")

    # FINAL SUMMARY
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"  PRIMARY (site-holdout, unseen destinations): MAE={site_holdout_mae:.4f} R2={site_holdout_r2:.4f} acc={site_holdout_accuracy:.4f}")
    print(f"  Secondary (random split, inflated):           MAE={mae:.4f} R2={r2:.4f} acc={test_accuracy:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    train_model()
