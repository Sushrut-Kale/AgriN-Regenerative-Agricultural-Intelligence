"""
FarmFriend AI — Crop Prediction Service
=========================================

Orchestrates the full prediction pipeline:
  1. Run ML model prediction (15 features)
  2. Apply rule/knowledge layer scoring with Hard Eligibility Gates
  3. Filter and compose ranked list based on Farmer Intent (Seasonal Field Crops vs Perennial Horticulture)
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.predict import predictor
from backend.app.services.suitability_scorer import compute_suitability_score
from backend.app.services.validation import count_missing_soil_fields


def get_ranked_crops(
    soil_data: dict,
    env_data: dict,
    farm_data: dict,
    top_n: int = 10
) -> dict:
    """Run full prediction pipeline across all crops."""
    predictor.load()

    ml_inputs = {
        "N": soil_data.get("N"),
        "P": soil_data.get("P"),
        "K": soil_data.get("K"),
        "S": soil_data.get("S"),
        "Zn": soil_data.get("Zn"),
        "Fe": soil_data.get("Fe"),
        "Cu": soil_data.get("Cu"),
        "Mn": soil_data.get("Mn"),
        "B": soil_data.get("B"),
        "ph": soil_data.get("ph"),
        "EC": soil_data.get("EC"),
        "OC": soil_data.get("OC"),
        "temperature": env_data.get("temperature"),
        "humidity": env_data.get("humidity"),
        "rainfall": env_data.get("rainfall"),
    }

    ml_results = predictor.predict_top_crops(ml_inputs, top_n=25)
    n_missing, missing_fields = count_missing_soil_fields(soil_data)

    all_scored = []
    for ml_result in ml_results:
        crop_name = ml_result["crop"]
        ml_prob = ml_result["ml_probability"]

        score_result = compute_suitability_score(
            crop_name=crop_name,
            ml_probability=ml_prob,
            soil_data=soil_data,
            env_data=env_data,
            farm_data=farm_data,
            missing_fields=missing_fields
        )
        all_scored.append(score_result)

    intent = str(farm_data.get("intent", "seasonal_field_crop")).lower()

    if intent == "perennial_horticulture":
        primary_crops = [c for c in all_scored if c.get("category_type") == "perennial_horticulture"]
        secondary_crops = [c for c in all_scored if c.get("category_type") != "perennial_horticulture"]
    elif intent == "all":
        primary_crops = all_scored
        secondary_crops = []
    else:  # default: seasonal_field_crop
        primary_crops = [c for c in all_scored if c.get("category_type") == "seasonal_field_crop"]
        secondary_crops = [c for c in all_scored if c.get("category_type") == "perennial_horticulture"]

    primary_crops.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(primary_crops, 1):
        r["rank"] = i

    secondary_crops.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(secondary_crops, 1):
        r["secondary_rank"] = i

    return {
        "ranked_crops": primary_crops[:top_n],
        "perennial_horticulture_crops": secondary_crops[:5],
        "farmer_intent": intent,
        "model_info": predictor.get_model_info(),
        "feature_importance": predictor.get_feature_importance(),
        "data_completeness": {
            "n_missing_soil": n_missing,
            "missing_fields": missing_fields,
            "total_soil_fields": 12
        }
    }
