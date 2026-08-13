"""
FarmFriend AI — What-If Simulation Service
============================================

Recalculates suitability when the farmer changes input values.

IMPORTANT:
- Original input values are NEVER modified
- Simulation clearly labeled as simulated
- Impossible values are rejected
- Before/after comparison is always shown
"""

import sys
import os
import copy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.predict import predictor
from backend.app.services.suitability_scorer import compute_suitability_score
from backend.app.services.validation import (
    validate_whatif_inputs, count_missing_soil_fields
)
from backend.app.services.nlg_explainer import explain_whatif


def _extract_ml_inputs(soil_dict: dict, env_dict: dict) -> dict:
    return {
        "N": soil_dict.get("N"), "P": soil_dict.get("P"), "K": soil_dict.get("K"),
        "S": soil_dict.get("S"), "Zn": soil_dict.get("Zn"), "Fe": soil_dict.get("Fe"),
        "Cu": soil_dict.get("Cu"), "Mn": soil_dict.get("Mn"), "B": soil_dict.get("B"),
        "ph": soil_dict.get("ph"), "EC": soil_dict.get("EC"), "OC": soil_dict.get("OC"),
        "temperature": env_dict.get("temperature"),
        "humidity": env_dict.get("humidity"),
        "rainfall": env_dict.get("rainfall"),
    }


def run_whatif(
    crop_name: str,
    original_soil: dict,
    original_env: dict,
    farm_data: dict,
    simulated_changes: dict
) -> dict:
    predictor.load()

    validation = validate_whatif_inputs(simulated_changes)
    if not validation.is_valid:
        return {
            "error": True,
            "validation_errors": validation.to_dict(),
            "message": "Simulated values contain invalid entries."
        }

    # ── BEFORE (Original Inputs Pristine) ──────────────────────────────────
    ml_inputs_before = _extract_ml_inputs(original_soil, original_env)
    ml_prob_before = predictor.predict_single_crop(crop_name, ml_inputs_before) or 0.0
    n_missing_b, missing_b = count_missing_soil_fields(original_soil)
    before_result = compute_suitability_score(
        crop_name, ml_prob_before, original_soil, original_env, farm_data, missing_b
    )

    # ── AFTER (Deep Copy Inputs for Simulation) ────────────────────────────
    sim_soil = copy.deepcopy(original_soil)
    sim_env = copy.deepcopy(original_env)
    changed_params = {}

    for field, new_val in simulated_changes.items():
        if field in sim_soil:
            old_val = sim_soil.get(field)
            sim_soil[field] = new_val
            changed_params[field] = {"before": old_val, "after": new_val}
        elif field in sim_env:
            old_val = sim_env.get(field)
            sim_env[field] = new_val
            changed_params[field] = {"before": old_val, "after": new_val}

    ml_inputs_after = _extract_ml_inputs(sim_soil, sim_env)
    ml_prob_after = predictor.predict_single_crop(crop_name, ml_inputs_after) or 0.0
    n_missing_a, missing_a = count_missing_soil_fields(sim_soil)
    after_result = compute_suitability_score(
        crop_name, ml_prob_after, sim_soil, sim_env, farm_data, missing_a
    )

    score_change = round(after_result["final_score"] - before_result["final_score"], 1)

    explanation = explain_whatif(
        crop_name=crop_name,
        before_score=before_result["final_score"],
        after_score=after_result["final_score"],
        changed_params=changed_params,
        before_result=before_result,
        after_result=after_result
    )

    return {
        "is_simulation": True,
        "crop": crop_name,
        "before": {
            "score": before_result["final_score"],
            "classification": before_result["classification"],
            "classification_color": before_result["classification_color"],
            "supporting_factors": before_result["supporting_factors"],
            "limiting_factors": before_result["limiting_factors"],
        },
        "after": {
            "score": after_result["final_score"],
            "classification": after_result["classification"],
            "classification_color": after_result["classification_color"],
            "supporting_factors": after_result["supporting_factors"],
            "limiting_factors": after_result["limiting_factors"],
        },
        "changed_params": changed_params,
        "score_change": score_change,
        "score_change_direction": "increase" if score_change > 0 else ("decrease" if score_change < 0 else "no_change"),
        "explanation": explanation,
        "disclaimer": (
            "⚠️ This is a SIMULATED scenario. Simulated results do not guarantee "
            "the same outcome in real farming conditions."
        )
    }
