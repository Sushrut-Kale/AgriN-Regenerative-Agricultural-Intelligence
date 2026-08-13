# -*- coding: utf-8 -*-
"""
FarmFriend AI — Production Prediction Utility
==============================================

Provides inference functions used by FastAPI service:
  - predict_top_crops(inputs) -> list of (crop, ml_score)
  - predict_single_crop(crop, inputs) -> ml_probability
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "crop_model_v1.joblib")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v1.joblib")
ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder_v1.joblib")
META_PATH = os.path.join(MODELS_DIR, "model_metadata.json")

# 15 canonical features matching training schema
FEATURE_NAMES = [
    "N", "P", "K", "S", "Zn", "Fe", "Cu", "Mn", "B",
    "ph", "EC", "OC", "temperature", "humidity", "rainfall"
]

# Training distribution medians used ONLY as fallback for unsupplied optional inputs
DEFAULT_MEDIANS = {
    "N": 90.0, "P": 50.0, "K": 180.0, "S": 16.0, "Zn": 0.9, "Fe": 8.0,
    "Cu": 0.5, "Mn": 5.2, "B": 0.7, "ph": 6.8, "EC": 0.5, "OC": 0.65,
    "temperature": 26.0, "humidity": 68.0, "rainfall": 800.0
}


class CropPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.metadata = None
        self.uses_scaler = False
        self._loaded = False

    def load(self):
        if self._loaded:
            return

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run python ml/train.py")

        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.label_encoder = joblib.load(ENCODER_PATH)

        if os.path.exists(META_PATH):
            with open(META_PATH) as f:
                self.metadata = json.load(f)
            self.uses_scaler = self.metadata.get("uses_scaler", False)

        self._loaded = True

    def _prepare_features(self, inputs: dict) -> pd.DataFrame:
        row = {}
        for feat in FEATURE_NAMES:
            val = inputs.get(feat)
            if val is None:
                val = DEFAULT_MEDIANS[feat]
            row[feat] = float(val)
        df_row = pd.DataFrame([row], columns=FEATURE_NAMES)
        if self.uses_scaler and self.scaler is not None:
            return pd.DataFrame(self.scaler.transform(df_row), columns=FEATURE_NAMES)
        return df_row

    def predict_top_crops(self, inputs: dict, top_n: int = 25) -> list:
        if not self._loaded:
            self.load()

        X = self._prepare_features(inputs)
        proba = self.model.predict_proba(X)[0]
        class_names = self.label_encoder.classes_

        ranked = sorted(
            zip(class_names, proba),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return [
            {
                "crop": crop,
                "ml_probability": float(prob),
                "ml_score_100": round(float(prob) * 100, 1)
            }
            for crop, prob in ranked
        ]

    def predict_single_crop(self, crop_name: str, inputs: dict) -> Optional[float]:
        if not self._loaded:
            self.load()

        class_names = list(self.label_encoder.classes_)
        if crop_name not in class_names:
            return None

        X = self._prepare_features(inputs)
        proba = self.model.predict_proba(X)[0]
        idx = class_names.index(crop_name)
        return float(proba[idx])

    def get_feature_importance(self) -> list:
        if not self._loaded:
            self.load()
        if hasattr(self.model, "feature_importances_"):
            fi = self.model.feature_importances_
            return [
                {"feature": name, "importance": round(float(val), 4)}
                for name, val in sorted(zip(FEATURE_NAMES, fi), key=lambda x: x[1], reverse=True)
            ]
        return []

    def get_model_info(self) -> dict:
        if not self._loaded:
            self.load()
        if self.metadata:
            return {
                "model_version": self.metadata.get("model_version"),
                "model_type": self.metadata.get("model_type"),
                "training_date": self.metadata.get("training_date"),
                "metrics": self.metadata.get("metrics", {}),
                "n_classes": self.metadata.get("n_classes"),
                "all_models": self.metadata.get("all_models", [])
            }
        return {}


predictor = CropPredictor()
