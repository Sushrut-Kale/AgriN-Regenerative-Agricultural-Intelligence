"""
FarmFriend AI / AgriN — What-If Simulation Service
===================================================
Recalculates comprehensive agricultural metrics when the farmer perturbs input values.

PHASE 3 ENHANCEMENT:
Compares CURRENT vs SCENARIO across:
- Crop suitability
- Soil compatibility
- Water requirement
- Agricultural risk
- Farm resilience
- Data confidence

IMPORTANT:
- Original input values are NEVER modified.
- Simulation is explicitly labeled: "Scenario simulation — Not a prediction of actual future yield".
- Impossible/extreme values are validated.
"""

import sys
import os
import copy
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

from ml.predict import predictor
from backend.app.services.suitability_scorer import compute_suitability_score, compute_detailed_suitability
from backend.app.services.validation import (
    validate_whatif_inputs, count_missing_soil_fields
)
from backend.app.services.nlg_explainer import explain_whatif
from backend.app.services.agricultural_risk_engine import assess_agricultural_risks
from backend.app.services.farm_resilience import calculate_farm_resilience
from backend.app.services.confidence_engine import compute_confidence
from backend.app.services.soil_intelligence import assess_soil_health


def _extract_ml_inputs(soil_dict: dict, env_dict: dict) -> dict:
    return {
        "N": soil_dict.get("N"), "P": soil_dict.get("P"), "K": soil_dict.get("K"),
        "S": soil_dict.get("S"), "Zn": soil_dict.get("Zn"), "Fe": soil_dict.get("Fe"),
        "Cu": soil_dict.get("Cu"), "Mn": soil_dict.get("Mn"), "B": soil_dict.get("B"),
        "ph": soil_dict.get("ph") or soil_dict.get("pH"),
        "EC": soil_dict.get("EC"), "OC": soil_dict.get("OC"),
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

    target_crop = simulated_changes.get("crop") or simulated_changes.get("crop_name") or crop_name

    # ── BEFORE (Original Inputs Pristine) ──────────────────────────────────
    ml_inputs_before = _extract_ml_inputs(original_soil, original_env)
    ml_prob_before = predictor.predict_single_crop(crop_name, ml_inputs_before) or 0.0
    n_missing_b, missing_b = count_missing_soil_fields(original_soil)
    before_result = compute_suitability_score(
        crop_name, ml_prob_before, original_soil, original_env, farm_data, missing_b
    )
    detailed_before = compute_detailed_suitability(crop_name, farm_data, original_soil, original_env)
    soil_profile_before = assess_soil_health(original_soil, farm_data.get("soil_type"))
    resilience_before = calculate_farm_resilience(farm_data, soil_profile_before, before_result["final_score"])
    confidence_before = compute_confidence(
        {**farm_data, **original_soil, **original_env},
        geographic_resolution="DISTRICT",
        model_probability=before_result["final_score"] / 100.0
    )
    risks_before = assess_agricultural_risks(
        {**farm_data, **original_env, "crop": crop_name},
        soil_profile_before,
        original_env,
        [{"crop": crop_name, "final_score": before_result["final_score"]}]
    )

    # ── AFTER (Deep Copy Inputs for Simulation) ────────────────────────────
    sim_soil = copy.deepcopy(original_soil)
    sim_env = copy.deepcopy(original_env)
    sim_farm = copy.deepcopy(farm_data)
    changed_params = {}

    for field, new_val in simulated_changes.items():
        if field in sim_soil or field.lower() in ["ph", "oc", "ec"]:
            k = "ph" if field.lower() == "ph" else ("OC" if field.upper() == "OC" else ("EC" if field.upper() == "EC" else field))
            old_val = sim_soil.get(k)
            sim_soil[k] = new_val
            changed_params[field] = {"before": old_val, "after": new_val}
        elif field in sim_env:
            old_val = sim_env.get(field)
            sim_env[field] = new_val
            changed_params[field] = {"before": old_val, "after": new_val}
        elif field in sim_farm or field in ["irrigation_available", "soil_type", "water_source", "drainage"]:
            old_val = sim_farm.get(field)
            sim_farm[field] = new_val
            changed_params[field] = {"before": old_val, "after": new_val}

    ml_inputs_after = _extract_ml_inputs(sim_soil, sim_env)
    ml_prob_after = predictor.predict_single_crop(target_crop, ml_inputs_after) or 0.0
    n_missing_a, missing_a = count_missing_soil_fields(sim_soil)
    after_result = compute_suitability_score(
        target_crop, ml_prob_after, sim_soil, sim_env, sim_farm, missing_a
    )
    detailed_after = compute_detailed_suitability(target_crop, sim_farm, sim_soil, sim_env)
    soil_profile_after = assess_soil_health(sim_soil, sim_farm.get("soil_type"))
    resilience_after = calculate_farm_resilience(sim_farm, soil_profile_after, after_result["final_score"])
    confidence_after = compute_confidence(
        {**sim_farm, **sim_soil, **sim_env},
        geographic_resolution="DISTRICT",
        model_probability=after_result["final_score"] / 100.0
    )
    risks_after = assess_agricultural_risks(
        {**sim_farm, **sim_env, "crop": target_crop},
        soil_profile_after,
        sim_env,
        [{"crop": target_crop, "final_score": after_result["final_score"]}]
    )

    score_change = round(after_result["final_score"] - before_result["final_score"], 1)

    explanation = explain_whatif(
        crop_name=target_crop,
        before_score=before_result["final_score"],
        after_score=after_result["final_score"],
        changed_params=changed_params,
        before_result=before_result,
        after_result=after_result
    )

    # Comprehensive CURRENT vs SCENARIO Comparison (Step 6)
    scenario_comparison = {
        "crop_suitability": {
            "current": round(before_result["final_score"], 1),
            "scenario": round(after_result["final_score"], 1),
            "delta": score_change
        },
        "soil_compatibility": {
            "current": detailed_before.get("soil_compatibility", 70.0),
            "scenario": detailed_after.get("soil_compatibility", 70.0),
            "delta": round(detailed_after.get("soil_compatibility", 70.0) - detailed_before.get("soil_compatibility", 70.0), 1)
        },
        "water_requirement": {
            "current_water_fit": detailed_before.get("water_compatibility", 70.0),
            "scenario_water_fit": detailed_after.get("water_compatibility", 70.0),
            "irrigation_status_before": farm_data.get("irrigation_available", "no"),
            "irrigation_status_after": sim_farm.get("irrigation_available", "no")
        },
        "risk_profile": {
            "current_risk_count": len(risks_before),
            "scenario_risk_count": len(risks_after),
            "current_critical_risks": [r["risk"] for r in risks_before if r.get("severity") == "CRITICAL"],
            "scenario_critical_risks": [r["risk"] for r in risks_after if r.get("severity") == "CRITICAL"]
        },
        "farm_resilience": {
            "current_score": resilience_before.get("score", 65.0),
            "scenario_score": resilience_after.get("score", 65.0),
            "current_tier": resilience_before.get("resilience_tier"),
            "scenario_tier": resilience_after.get("resilience_tier")
        },
        "data_confidence": {
            "current_level": confidence_before.get("confidence_level"),
            "scenario_level": confidence_after.get("confidence_level")
        }
    }

    return {
        "is_simulation": True,
        "simulation_label": "Scenario simulation — Not a prediction of actual future yield",
        "crop": target_crop,
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
        "scenario_comparison": scenario_comparison,
        "disclaimer": (
            "⚠️ Scenario simulation: Simulated results reflect agronomic model sensitivity and do not guarantee "
            "actual future crop yield or field outcomes."
        )
    }
