# -*- coding: utf-8 -*-
"""
FarmFriend AI — Production ML Training & Benchmarking Pipeline
===============================================================

Trains and compares multi-crop recommendation models on the unified dataset.

Models evaluated:
  1. Logistic Regression (Baseline)
  2. Decision Tree
  3. Random Forest (Ensemble)
  4. HistGradientBoostingClassifier (Gradient Boosted Ensemble)

Evaluates:
  - Accuracy
  - Macro F1 & Weighted F1
  - Precision & Recall
  - Stratified 5-Fold Cross Validation

Output Artifacts:
  models/crop_model_v1.joblib
  models/scaler_v1.joblib
  models/label_encoder_v1.joblib
  models/model_metadata.json
  models/classification_report.json
  models/registry.json
"""

import os
import sys
import json
import joblib
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "unified_crop_soil_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

SEED = 42
TEST_SIZE = 0.2


def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        # Fallback to building training dataset
        from data.scripts.build_training_dataset import build_dataset
        build_dataset()
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} records, {df['label'].nunique()} crops")
    print(f"Features ({len(df.columns)-1}): {[c for c in df.columns if c != 'label']}")
    return df


def preprocess(df: pd.DataFrame):
    """Fit preprocessing ONLY on training data to prevent leakage."""
    X = df.drop("label", axis=1)
    y = df["label"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=TEST_SIZE, random_state=SEED, stratify=y_encoded
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    return (X_train, X_test, X_train_scaled, X_test_scaled,
            y_train, y_test, scaler, le, X.columns.tolist())


def train_and_evaluate(name, model, X_train, X_test, y_train, y_test):
    """Train model and compute metrics."""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    prec_m = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec_m = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_m = f1_score(y_test, y_pred, average="macro", zero_division=0)

    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")

    print(f"\n{'='*60}")
    print(f"Model: {name}")
    print(f"  Accuracy       : {acc:.4f}")
    print(f"  Weighted F1    : {f1_w:.4f}")
    print(f"  Macro F1       : {f1_m:.4f}")
    print(f"  CV Accuracy    : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

    return {
        "model": model,
        "name": name,
        "accuracy": float(acc),
        "precision_weighted": float(prec_w),
        "recall_weighted": float(rec_w),
        "f1_weighted": float(f1_w),
        "precision_macro": float(prec_m),
        "recall_macro": float(rec_m),
        "f1_macro": float(f1_m),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
        "y_pred": y_pred
    }


def plot_confusion_matrix(y_test, y_pred, le, model_name: str):
    """Save confusion matrix plot."""
    cm = confusion_matrix(y_test, y_pred)
    class_names = le.classes_

    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Greens",
        xticklabels=class_names, yticklabels=class_names, ax=ax
    )
    ax.set_xlabel("Predicted", fontsize=11)
    ax.set_ylabel("Actual", fontsize=11)
    ax.set_title(f"Confusion Matrix — {model_name}", fontsize=13)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    path = os.path.join(MODELS_DIR, "confusion_matrix.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    print("=" * 60)
    print("FarmFriend AI — Production ML Training Pipeline")
    print("=" * 60)

    df = load_data()
    (X_train, X_test, X_train_sc, X_test_sc,
     y_train, y_test, scaler, le, feature_names) = preprocess(df)

    models_config = [
        ("Logistic Regression", LogisticRegression(
            max_iter=2000, random_state=SEED, multi_class="multinomial",
            solver="lbfgs", C=1.0
        ), True),
        ("Decision Tree", DecisionTreeClassifier(
            max_depth=15, random_state=SEED, min_samples_split=5
        ), False),
        ("Random Forest", RandomForestClassifier(
            n_estimators=200, max_depth=20, random_state=SEED,
            n_jobs=-1, min_samples_split=4, min_samples_leaf=2
        ), False),
        ("HistGradientBoosting", HistGradientBoostingClassifier(
            max_iter=150, random_state=SEED, min_samples_leaf=5
        ), False),
    ]

    results = []
    print("\nTraining candidate models...")

    for name, model, use_scaled in models_config:
        X_tr = X_train_sc if use_scaled else X_train
        X_te = X_test_sc if use_scaled else X_test
        res = train_and_evaluate(name, model, X_tr, X_te, y_train, y_test)
        results.append(res)

    print(f"\n{'='*70}")
    print("MODEL COMPARISON BENCHMARK TABLE")
    print(f"{'='*70}")
    header = f"{'Model':<24} {'Accuracy':>9} {'W-F1':>8} {'M-F1':>8} {'CV Acc':>14}"
    print(header)
    print("-" * 70)
    for r in results:
        row = (f"{r['name']:<24} {r['accuracy']:>9.4f} {r['f1_weighted']:>8.4f} "
               f"{r['f1_macro']:>8.4f} {r['cv_mean']:>8.4f}+/-{r['cv_std']:.4f}")
        print(row)

    # Select best model based on Macro F1
    best = max(results, key=lambda r: r["f1_macro"])
    print(f"\n{'='*70}")
    print(f"SELECTED PRODUCTION MODEL: {best['name']} (Macro F1: {best['f1_macro']:.4f})")
    print(f"{'='*70}")

    best_model = best["model"]
    uses_scaled = best["name"] == "Logistic Regression"
    X_tr_final = X_train_sc if uses_scaled else X_train
    X_te_final = X_test_sc if uses_scaled else X_test

    best_model.fit(X_tr_final, y_train)

    # Save artifacts
    joblib.dump(best_model, os.path.join(MODELS_DIR, "crop_model_v1.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler_v1.joblib"))
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder_v1.joblib"))

    # Classification report
    y_pred_best = best_model.predict(X_te_final)
    report = classification_report(y_test, y_pred_best, target_names=le.classes_, output_dict=True)
    with open(os.path.join(MODELS_DIR, "classification_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    plot_confusion_matrix(y_test, y_pred_best, le, best["name"])

    # Feature Importance (Random Forest or Decision Tree)
    fi_data = []
    rf_res = next((r for r in results if "Random Forest" in r["name"]), None)
    if rf_res and hasattr(rf_res["model"], "feature_importances_"):
        fi = rf_res["model"].feature_importances_
        fi_data = [
            {"feature": f_name, "importance": round(float(v), 4)}
            for f_name, v in sorted(zip(feature_names, fi), key=lambda x: x[1], reverse=True)
        ]
        with open(os.path.join(MODELS_DIR, "feature_importance.json"), "w") as f:
            json.dump(fi_data, f, indent=2)

    model_metadata = {
        "model_version": f"{best['name'].lower().replace(' ', '_')}_v2",
        "model_type": best["name"],
        "training_date": datetime.now().isoformat(),
        "dataset": "unified_crop_soil_dataset.csv",
        "dataset_nature": "VERIFIED_MULTI_SOURCE_OPEN_DATA",
        "seed": SEED,
        "test_size": TEST_SIZE,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "feature_names": feature_names,
        "n_classes": int(len(le.classes_)),
        "class_names": le.classes_.tolist(),
        "metrics": {
            "accuracy": best["accuracy"],
            "precision_weighted": best["precision_weighted"],
            "recall_weighted": best["recall_weighted"],
            "f1_weighted": best["f1_weighted"],
            "precision_macro": best["precision_macro"],
            "recall_macro": best["recall_macro"],
            "f1_macro": best["f1_macro"],
            "cv_accuracy_mean": best["cv_mean"],
            "cv_accuracy_std": best["cv_std"]
        },
        "all_models": [
            {
                "name": r["name"],
                "accuracy": r["accuracy"],
                "precision_weighted": r["precision_weighted"],
                "recall_weighted": r["recall_weighted"],
                "f1_weighted": r["f1_weighted"],
                "f1_macro": r["f1_macro"],
                "cv_mean": r["cv_mean"]
            }
            for r in results
        ],
        "feature_importance": fi_data,
        "uses_scaler": uses_scaled,
        "disclaimer": "Model trained on verified multi-source open agricultural data. Decision support estimate only."
    }

    with open(os.path.join(MODELS_DIR, "model_metadata.json"), "w") as f:
        json.dump(model_metadata, f, indent=2)

    registry_data = {
        "active_model_version": model_metadata["model_version"],
        "updated_at": datetime.now().isoformat(),
        "versions": {
            "logistic_regression_v1": {"status": "retired", "note": "Trained on legacy synthetic dataset"},
            model_metadata["model_version"]: {
                "status": "production",
                "model_type": best["name"],
                "f1_macro": best["f1_macro"],
                "accuracy": best["accuracy"]
            }
        }
    }
    with open(os.path.join(MODELS_DIR, "registry.json"), "w") as f:
        json.dump(registry_data, f, indent=2)

    print("\nModel training & registration complete.")


if __name__ == "__main__":
    main()
