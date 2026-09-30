"""
FarmFriend AI — Suitability Scorer & Agricultural Rule Engine
===============================================================

Computes final crop suitability score by combining:
  1. ML model probability evidence (50%)
  2. Agronomic requirement compatibility & Hard Eligibility Gates (50%)

Enforces Hard Eligibility Gates:
  - Season Gate (Rabi crop in Kharif request -> Hard penalty multiplier 0.1x)
  - Water Gate (High-water crop in Rainfed farm -> Hard penalty multiplier 0.25x)
  - pH Gate (Soil pH outside critical tolerable range -> Hard penalty multiplier 0.2x)
  - Category Demarcation (Perennial orchards vs Seasonal field crops)

Score Range: 0–100 (Scientifically grounded, transparent trace)
"""

import os
import json
import math
from typing import Optional, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

with open(os.path.join(KNOWLEDGE_DIR, "crop_requirements.json")) as f:
    CROP_REQUIREMENTS = json.load(f)["crops"]

with open(os.path.join(KNOWLEDGE_DIR, "shc_thresholds.json")) as f:
    SHC_DATA = json.load(f)

SHC_PARAMS = SHC_DATA["parameters"]

ML_WEIGHT = 0.50
RULE_WEIGHT = 0.50

RULE_COMPONENT_WEIGHTS = {
    "ph":       0.20,
    "npk":      0.25,
    "micronut": 0.15,
    "temp":     0.15,
    "rainfall": 0.15,
    "context":  0.10,
}


def classify_score(score: float) -> Tuple[str, str]:
    if score >= 75:
        return ("Highly Suitable", "green")
    elif score >= 55:
        return ("Suitable", "green")
    elif score >= 35:
        return ("Moderately Suitable", "yellow")
    elif score >= 20:
        return ("Low Suitability", "orange")
    else:
        return ("Poor Suitability", "red")


def _check_ph(crop_req: dict, ph_value: Optional[float]) -> Tuple[float, str, str, float]:
    if ph_value is None:
        return (0.6, "uncertain", "Soil pH not provided — parameter marked as uncertain", 1.0)

    ph_data = crop_req.get("ph", {})
    opt_min = ph_data.get("optimal_min", 5.5)
    opt_max = ph_data.get("optimal_max", 7.5)
    crit_min = ph_data.get("critical_min", 4.5)
    crit_max = ph_data.get("critical_max", 9.0)

    if opt_min <= ph_value <= opt_max:
        return (1.0, "suitable", f"pH {ph_value:.1f} is within reference range ({opt_min}–{opt_max})", 1.0)
    elif crit_min <= ph_value <= crit_max:
        if ph_value < opt_min:
            dist = opt_min - ph_value
            span = max(opt_min - crit_min, 0.1)
        else:
            dist = ph_value - opt_max
            span = max(crit_max - opt_max, 0.1)
        score = max(0.15, round(1.0 - (dist / span) * 0.8, 2))
        return (score, "limiting", f"pH {ph_value:.1f} is outside preferred range ({opt_min}–{opt_max})", 1.0)
    else:
        # Severe pH Hard Gate Penalty
        return (0.05, "limiting", f"pH {ph_value:.1f} violates critical pH bounds ({crit_min}–{crit_max})", 0.2)


def _interpret_npk(N_val, P_val, K_val, crop_req: dict) -> Tuple[float, List[dict]]:
    factors = []
    scores = []
    npk_data = crop_req.get("nutrients", {})

    for nutrient, value in [("N", N_val), ("P", P_val), ("K", K_val)]:
        nut_req = npk_data.get(nutrient, {})
        requirement = nut_req.get("requirement", "medium")

        shc_interp = SHC_PARAMS[nutrient]["interpretation"]
        low_max = shc_interp["low"]["max"]
        med_max = shc_interp["medium"]["max"]

        if value is None:
            scores.append(0.6)
            factors.append({
                "factor": nutrient, "status": "uncertain",
                "note": f"{nutrient} not provided — parameter marked as uncertain",
                "score": 60.0
            })
            continue

        if value < low_max:
            soil_status = "low"
        elif value <= med_max:
            soil_status = "medium"
        else:
            soil_status = "high"

        if requirement == "low":
            if soil_status in ("low", "medium"):
                score, status = 1.0, "suitable"
                note = f"Adequate {nutrient} ({value:.0f} kg/ha) within reference range for low-requirement crop"
            else:
                score, status = 0.85, "suitable"
                note = f"{nutrient} is elevated ({value:.0f} kg/ha) — crop has low requirement"
        elif requirement == "medium":
            if soil_status == "medium":
                score, status = 1.0, "suitable"
                note = f"{nutrient} ({value:.0f} kg/ha) is within reference range for crop requirement"
            elif soil_status == "high":
                score, status = 0.9, "suitable"
                note = f"{nutrient} level ({value:.0f} kg/ha) is compatible with crop growth"
            else:
                score, status = 0.45, "limiting"
                note = f"{nutrient} is low ({value:.0f} kg/ha) — crop prefers medium level"
        else:
            if soil_status == "high":
                score, status = 1.0, "suitable"
                note = f"{nutrient} ({value:.0f} kg/ha) is within reference range for high-requirement crop"
            elif soil_status == "medium":
                score, status = 0.75, "moderate"
                note = f"{nutrient} is moderate ({value:.0f} kg/ha) — crop prefers higher nutrient level"
            else:
                score, status = 0.3, "limiting"
                note = f"{nutrient} is low ({value:.0f} kg/ha) — crop needs medium-to-high level"

        scores.append(score)
        factors.append({"factor": nutrient, "status": status, "note": note, "score": round(score * 100, 1)})

    avg_score = sum(scores) / len(scores) if scores else 0.5
    return avg_score, factors


def _interpret_micronutrients(S, Zn, Fe, Cu, Mn, B) -> Tuple[float, List[dict]]:
    factors = []
    scores = []
    checks = [
        ("S", S, SHC_PARAMS["S"], "Sulphur"),
        ("Zn", Zn, SHC_PARAMS["Zn"], "Zinc"),
        ("Fe", Fe, SHC_PARAMS["Fe"], "Iron"),
        ("Cu", Cu, SHC_PARAMS["Cu"], "Copper"),
        ("Mn", Mn, SHC_PARAMS["Mn"], "Manganese"),
        ("B", B, SHC_PARAMS["B"], "Boron"),
    ]

    for field, value, param_data, label in checks:
        critical = param_data.get("critical_level", 0)
        interp = param_data["interpretation"]

        if value is None:
            scores.append(0.6)
            factors.append({"factor": field, "status": "uncertain", "note": f"{label} not provided"})
            continue

        def_max = interp.get("deficient", {}).get("max", critical)
        if value < def_max:
            scores.append(0.4)
            factors.append({
                "factor": field, "status": "limiting",
                "note": f"{label} is deficient ({value} ppm; critical threshold: {critical} ppm)"
            })
        else:
            scores.append(1.0)
            factors.append({
                "factor": field, "status": "suitable",
                "note": f"{label} is sufficient ({value} ppm)"
            })

    avg = sum(scores) / len(scores) if scores else 0.6
    return avg, factors


def _check_temperature(crop_req: dict, temp_val: Optional[float]) -> Tuple[float, str, str]:
    if temp_val is None:
        return (0.7, "uncertain", "Temperature not provided — parameter marked as uncertain")

    t = crop_req.get("temperature", {})
    opt_min = t.get("optimal_min", 15)
    opt_max = t.get("optimal_max", 35)
    crit_min = t.get("critical_min", 5)
    crit_max = t.get("critical_max", 45)

    if opt_min <= temp_val <= opt_max:
        return (1.0, "suitable", f"Temperature {temp_val:.1f}°C is within reference range ({opt_min}–{opt_max}°C)")
    elif crit_min <= temp_val <= crit_max:
        return (0.6, "moderate", f"Temperature {temp_val:.1f}°C is outside preferred range ({opt_min}–{opt_max}°C) but tolerable")
    else:
        return (0.1, "limiting", f"Temperature {temp_val:.1f}°C violates critical temperature bounds ({crit_min}–{crit_max}°C)")


def _check_rainfall(crop_name: str, crop_req: dict, rainfall_val: Optional[float], farm_data: dict) -> Tuple[float, str, str, float]:
    if rainfall_val is None:
        return (0.7, "uncertain", "Rainfall not provided — parameter marked as uncertain", 1.0)

    r = crop_req.get("rainfall", {})
    opt_min = r.get("optimal_min", 400)
    opt_max = r.get("optimal_max", 1200)
    crit_min = r.get("critical_min", opt_min * 0.7)

    irr_str = str(farm_data.get("irrigation_available", "")).lower()
    irr_available = irr_str in ("yes", "true", "drip", "canal", "borewell")

    water_gate = 1.0
    if opt_min <= rainfall_val <= opt_max:
        return (1.0, "suitable", f"Seasonal rainfall of {rainfall_val:.0f}mm is within reference range ({opt_min}–{opt_max}mm)", 1.0)
    elif rainfall_val < opt_min:
        if irr_available:
            return (0.85, "suitable", f"Rainfall {rainfall_val:.0f}mm is below preferred range ({opt_min}mm), but available irrigation supplements water needs", 1.0)
        elif rainfall_val < crit_min:
            # Water Hard Gate Penalty for rainfed high-water crops
            if crop_name in ("rice", "banana", "jute", "sugarcane"):
                water_gate = 0.25
            return (0.2, "limiting", f"Rainfall {rainfall_val:.0f}mm is critically low for rainfed {crop_name.title()} (requires {opt_min}mm+)", water_gate)
        else:
            score = max(0.35, round(0.4 + 0.4 * (rainfall_val - crit_min) / (opt_min - crit_min + 1e-5), 2))
            return (score, "moderate", f"Rainfall {rainfall_val:.0f}mm is below preferred range ({opt_min}mm); supplemental irrigation recommended", 1.0)
    else:
        if crop_name in ("rice", "jute", "coconut"):
            return (0.95, "suitable", f"Rainfall {rainfall_val:.0f}mm is abundant and compatible with water-tolerant {crop_name.title()}", 1.0)
        drainage = str(farm_data.get("drainage", "good")).lower()
        if drainage in ("good", "excellent"):
            return (0.8, "suitable", f"Rainfall {rainfall_val:.0f}mm exceeds reference range ({opt_max}mm), but good soil drainage mitigates waterlogging risk", 1.0)
        else:
            return (0.45, "moderate", f"Rainfall {rainfall_val:.0f}mm exceeds reference range ({opt_max}mm); adequate field drainage essential", 1.0)


def _check_context(crop_req: dict, farm_data: dict, crop_name: str) -> Tuple[float, List[dict], float]:
    factors = []
    scores = []
    season_gate = 1.0

    season = farm_data.get("season")
    state = farm_data.get("state", "Maharashtra")
    from backend.app.services.geo_service import get_crop_seasons_for_region
    crop_seasons = get_crop_seasons_for_region(crop_name, state)
    category_type = crop_req.get("category_type", "seasonal_field_crop")

    if category_type == "perennial_horticulture":
        scores.append(0.7)
        factors.append({
            "factor": "system_type", "status": "moderate",
            "note": f"Perennial horticultural crop — evaluated separately from seasonal field crops"
        })
    elif season and crop_seasons:
        if season.lower() in [s.lower() for s in crop_seasons]:
            scores.append(1.0)
            factors.append({"factor": "season", "status": "suitable", "note": f"Season ({season.title()}) is compatible with crop calendar"})
        else:
            # Season Hard Gate Penalty for strictly off-season seasonal field crops
            season_gate = 0.15
            scores.append(0.1)
            factors.append({"factor": "season", "status": "limiting", "note": f"Ineligible Season: {crop_name.title()} is grown in {'/'.join(crop_seasons).title()}, not {season.title()}"})
    else:
        scores.append(0.7)

    soil_type = farm_data.get("soil_type")
    preferred_soils = crop_req.get("soil", {}).get("preferred_types", [])
    if soil_type and preferred_soils:
        if any(p.lower() in soil_type.lower() or soil_type.lower() in p.lower() for p in preferred_soils):
            scores.append(1.0)
            factors.append({"factor": "soil_type", "status": "suitable", "note": f"Soil type ({soil_type}) is compatible with crop growth"})
        else:
            scores.append(0.6)
            factors.append({"factor": "soil_type", "status": "moderate", "note": f"Crop prefers {', '.join(preferred_soils[:3])} soils"})
    else:
        scores.append(0.7)

    avg = sum(scores) / len(scores) if scores else 0.7
    return avg, factors, season_gate


def compute_suitability_score(
    crop_name: str,
    ml_probability: float,
    soil_data: dict,
    env_data: dict,
    farm_data: dict,
    missing_fields: List[str]
) -> dict:
    if crop_name not in CROP_REQUIREMENTS:
        return _no_knowledge_fallback(crop_name, ml_probability)

    crop_req = CROP_REQUIREMENTS[crop_name]

    ph_score, ph_status, ph_note, ph_gate = _check_ph(crop_req, soil_data.get("ph"))
    npk_score, npk_factors = _interpret_npk(soil_data.get("N"), soil_data.get("P"), soil_data.get("K"), crop_req)
    micro_score, micro_factors = _interpret_micronutrients(
        soil_data.get("S"), soil_data.get("Zn"), soil_data.get("Fe"),
        soil_data.get("Cu"), soil_data.get("Mn"), soil_data.get("B")
    )
    temp_score, temp_status, temp_note = _check_temperature(crop_req, env_data.get("temperature"))
    rain_score, rain_status, rain_note, water_gate = _check_rainfall(crop_name, crop_req, env_data.get("rainfall"), farm_data)
    ctx_score, ctx_factors, season_gate = _check_context(crop_req, farm_data, crop_name)

    rule_raw = (
        ph_score    * RULE_COMPONENT_WEIGHTS["ph"] +
        npk_score   * RULE_COMPONENT_WEIGHTS["npk"] +
        micro_score * RULE_COMPONENT_WEIGHTS["micronut"] +
        temp_score  * RULE_COMPONENT_WEIGHTS["temp"] +
        rain_score  * RULE_COMPONENT_WEIGHTS["rainfall"] +
        ctx_score   * RULE_COMPONENT_WEIGHTS["context"]
    )

    ml_score_raw = ml_probability
    missing_penalty = max(0.0, 1.0 - (len(missing_fields) * 0.03))

    # Master Hard Gate Multiplier
    hard_gate_multiplier = season_gate * water_gate * ph_gate

    combined_raw = (ml_score_raw * ML_WEIGHT + rule_raw * RULE_WEIGHT) * missing_penalty * hard_gate_multiplier
    final_score = round(max(0.0, min(100.0, combined_raw * 100)), 1)

    classification, color = classify_score(final_score)

    all_factors = []
    all_factors.append({"factor": "pH", "status": ph_status, "note": ph_note, "score": round(ph_score * 100, 1)})
    all_factors.extend(npk_factors)
    all_factors.extend(micro_factors)
    all_factors.append({"factor": "Temperature", "status": temp_status, "note": temp_note, "score": round(temp_score * 100, 1)})
    all_factors.append({"factor": "Rainfall", "status": rain_status, "note": rain_note, "score": round(rain_score * 100, 1)})
    all_factors.extend(ctx_factors)

    supporting = [f for f in all_factors if f["status"] == "suitable"]
    limiting   = [f for f in all_factors if f["status"] == "limiting"]
    moderate   = [f for f in all_factors if f["status"] == "moderate"]
    uncertain  = [f for f in all_factors if f["status"] == "uncertain"]

    # Source Traceability
    source_info = {
        "source_name": crop_req.get("source_name", "Government of India Soil Health Card"),
        "source_url": crop_req.get("source_url", "https://soilhealth.dac.gov.in/"),
        "last_verified": crop_req.get("last_verified", "2026-08-13")
    }

    # Prediction Trace
    prediction_trace = {
        "crop_name": crop_name,
        "input_soil": soil_data,
        "input_env": env_data,
        "input_farm": farm_data,
        "ml_probability": ml_probability,
        "component_scores": {
            "ph": round(ph_score, 3),
            "npk": round(npk_score, 3),
            "micronutrients": round(micro_score, 3),
            "temperature": round(temp_score, 3),
            "rainfall": round(rain_score, 3),
            "context": round(ctx_score, 3),
            "rule_weighted_raw": round(rule_raw, 3)
        },
        "eligibility_gates": {
            "season_gate": season_gate,
            "water_gate": water_gate,
            "ph_gate": ph_gate,
            "combined_gate_multiplier": hard_gate_multiplier
        },
        "missing_fields_penalty": missing_penalty,
        "final_score": final_score
    }

    # Data confidence classification
    if len(missing_fields) <= 1 and hard_gate_multiplier > 0.8:
        data_confidence = "High"
    elif len(missing_fields) <= 4 and hard_gate_multiplier > 0.4:
        data_confidence = "Medium"
    else:
        data_confidence = "Low"

    return {
        "crop": crop_name,
        "common_name": crop_req.get("common_name", crop_name.title()),
        "local_name": crop_req.get("local_name", ""),
        "scientific_name": crop_req.get("scientific_name", ""),
        "category": crop_req.get("category", ""),
        "category_type": crop_req.get("category_type", "seasonal_field_crop"),
        "final_score": final_score,
        "ml_score": round(ml_score_raw * 100, 1),
        "rule_score": round(rule_raw * 100, 1),
        "data_confidence": data_confidence,
        "classification": classification,
        "classification_color": color,
        "ml_probability": ml_probability,
        "ml_score_component": round(ml_score_raw * 100, 1),
        "rule_score_component": round(rule_raw * 100, 1),
        "hard_gate_multiplier": hard_gate_multiplier,
        "supporting_factors": supporting,
        "limiting_factors": limiting,
        "moderate_factors": moderate,
        "uncertain_factors": uncertain,
        "missing_factors": [f for f in all_factors if f["status"] == "missing"],
        "source_info": source_info,
        "prediction_trace": prediction_trace,
        "disclaimer": (
            "This suitability score is a data-driven estimate based on soil parameters, "
            "seasonal climate benchmarks, and agricultural rule constraints. "
            "Always consult your local Krishi Vigyan Kendra (KVK) officer before planting."
        )
    }


def _no_knowledge_fallback(crop_name: str, ml_probability: float) -> dict:
    score = round(ml_probability * 100, 1)
    classification, color = classify_score(score)
    return {
        "crop": crop_name,
        "common_name": crop_name.title(),
        "final_score": score,
        "ml_score": score,
        "rule_score": None,
        "data_confidence": "Low",
        "classification": classification,
        "classification_color": color,
        "ml_probability": ml_probability,
        "ml_score_component": score,
        "rule_score_component": None,
        "hard_gate_multiplier": 1.0,
        "supporting_factors": [],
        "limiting_factors": [],
        "moderate_factors": [],
        "uncertain_factors": [],
        "missing_factors": [],
        "source_info": {"source_name": "ML Model Only", "source_url": "", "last_verified": "2026-08-13"},
        "prediction_trace": {"crop_name": crop_name, "note": "No rule profile available"},
        "disclaimer": "ML probability score only; no knowledge profile available for this crop."
    }
