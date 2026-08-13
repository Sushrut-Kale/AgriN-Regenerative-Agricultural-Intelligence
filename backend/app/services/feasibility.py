"""
FarmFriend AI — Feasibility Service
======================================

Handles "I Want to Grow This" — farmer-selected crop analysis.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.predict import predictor
from backend.app.services.suitability_scorer import compute_suitability_score
from backend.app.services.validation import count_missing_soil_fields
from backend.app.services.nlg_explainer import explain_feasibility, generate_summary_card


def analyze_farmer_chosen_crop(
    chosen_crop: str,
    soil_data: dict,
    env_data: dict,
    farm_data: dict
) -> dict:
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

    ml_prob = predictor.predict_single_crop(chosen_crop, ml_inputs) or 0.0
    n_missing, missing_fields = count_missing_soil_fields(soil_data)

    result = compute_suitability_score(
        crop_name=chosen_crop,
        ml_probability=ml_prob,
        soil_data=soil_data,
        env_data=env_data,
        farm_data=farm_data,
        missing_fields=missing_fields
    )

    result["feasibility_explanation"] = explain_feasibility(result, chosen_crop)
    result["summary_card"] = generate_summary_card(result)

    score = result["final_score"]
    if score >= 75:
        result["feasibility_outcome"] = "feasible"
        result["feasibility_label"] = "Feasible"
        result["feasibility_color"] = "green"
    elif score >= 55:
        result["feasibility_outcome"] = "moderate"
        result["feasibility_label"] = "Potentially Feasible"
        result["feasibility_color"] = "yellow"
    elif score >= 35:
        result["feasibility_outcome"] = "low"
        result["feasibility_label"] = "Low Suitability"
        result["feasibility_color"] = "orange"
    else:
        result["feasibility_outcome"] = "not_suitable"
        result["feasibility_label"] = "Not Suitable"
        result["feasibility_color"] = "red"

    return result
