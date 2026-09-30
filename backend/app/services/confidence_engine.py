"""
AgriN Data Confidence Engine
Computes transparent, multi-dimensional confidence scores across:
1. Data Completeness (0.30)
2. Data Freshness (0.20)
3. Geographic Precision (0.20)
4. Model Confidence (0.15)
5. Rule Coverage (0.15)

Categorical Levels: HIGH, MEDIUM, LOW, INSUFFICIENT
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def compute_confidence(
    provided_fields: Dict[str, Any],
    geographic_resolution: str = "DISTRICT",
    data_timestamp: Optional[datetime] = None,
    model_probability: Optional[float] = None,
    rules_evaluated_count: int = 4,
    rules_applicable_count: int = 4
) -> Dict[str, Any]:
    """
    Computes a deterministic, documented confidence assessment.
    
    Parameters:
        provided_fields: Dict of raw field inputs (soil, weather, farm)
        geographic_resolution: 'PARCEL', 'VILLAGE', 'SUB_DISTRICT', 'DISTRICT', 'STATE', 'NATIONAL'
        data_timestamp: Timestamp when observations were measured or retrieved
        model_probability: Top class probability from statistical ML model (0.0 - 1.0)
        rules_evaluated_count: Number of agronomic rules evaluated
        rules_applicable_count: Total number of rules applicable
    """
    # 1. Completeness Score (0.30 weight)
    core_keys = [
        "N", "P", "K", "pH", "EC", "OC",
        "temperature", "humidity", "rainfall",
        "season", "state", "district"
    ]
    present_count = 0
    missing_keys: List[str] = []
    for k in core_keys:
        val = provided_fields.get(k)
        if val is not None and val != "" and val != "unknown":
            present_count += 1
        else:
            missing_keys.append(k)

    completeness_score = present_count / len(core_keys)

    # 2. Freshness Score (0.20 weight)
    if data_timestamp is None:
        freshness_score = 0.70  # Standard session assumption
        freshness_label = "SESSION_ASSUMED"
    else:
        now = datetime.now(timezone.utc)
        if data_timestamp.tzinfo is None:
            data_timestamp = data_timestamp.replace(tzinfo=timezone.utc)
        age_days = (now - data_timestamp).total_seconds() / 86400.0

        if age_days <= 1.0:
            freshness_score = 1.0
            freshness_label = "REAL_TIME_TODAY"
        elif age_days <= 30.0:
            freshness_score = 0.90
            freshness_label = "RECENT_MONTH"
        elif age_days <= 180.0:
            freshness_score = 0.75
            freshness_label = "CURRENT_SEASON"
        elif age_days <= 365.0:
            freshness_score = 0.60
            freshness_label = "ANNUAL_PAST"
        else:
            freshness_score = 0.40
            freshness_label = "HISTORICAL_STALE"

    # 3. Geographic Precision (0.20 weight)
    geo_map = {
        "PARCEL": 1.0,
        "GPS": 1.0,
        "VILLAGE": 0.90,
        "SUB_DISTRICT": 0.80,
        "DISTRICT": 0.70,
        "STATE": 0.45,
        "NATIONAL": 0.30
    }
    resolution_upper = str(geographic_resolution).upper()
    geo_score = geo_map.get(resolution_upper, 0.65)

    # 4. Model Confidence (0.15 weight)
    if model_probability is not None:
        model_score = max(0.0, min(1.0, float(model_probability)))
    else:
        model_score = 0.50  # Neutral baseline when ML model not invoked

    # 5. Rule Coverage (0.15 weight)
    if rules_applicable_count > 0:
        rule_score = min(1.0, max(0.0, rules_evaluated_count / rules_applicable_count))
    else:
        rule_score = 0.50

    # Composite Weighted Calculation
    composite = (
        0.30 * completeness_score +
        0.20 * freshness_score +
        0.20 * geo_score +
        0.15 * model_score +
        0.15 * rule_score
    )
    composite = round(max(0.05, min(0.99, composite)), 2)

    # Categorical Mapping
    if composite >= 0.75:
        category = "HIGH"
    elif composite >= 0.50:
        category = "MEDIUM"
    elif composite >= 0.30:
        category = "LOW"
    else:
        category = "INSUFFICIENT"

    return {
        "confidence_score": composite,
        "confidence_level": category,
        "factors": {
            "completeness": round(completeness_score, 2),
            "freshness": round(freshness_score, 2),
            "geographic_precision": round(geo_score, 2),
            "model_confidence": round(model_score, 2),
            "rule_coverage": round(rule_score, 2)
        },
        "metadata": {
            "resolution": resolution_upper,
            "freshness_label": freshness_label,
            "missing_core_fields": missing_keys,
            "formula": "0.30*Completeness + 0.20*Freshness + 0.20*GeoPrecision + 0.15*ModelConf + 0.15*RuleCoverage"
        }
    }


def get_missing_data_guidance(provided_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates what parameters are known vs missing and generates actionable guidance.
    """
    known_inputs = []
    missing_inputs = []
    
    # pH
    ph_val = provided_fields.get("pH") if provided_fields.get("pH") is not None else provided_fields.get("ph")
    if ph_val is not None:
        known_inputs.append("pH")
    else:
        missing_inputs.append("Soil Reaction (pH): Essential for evaluating nutrient availability and acidity/alkalinity hazards.")

    # OC
    oc_val = provided_fields.get("OC") if provided_fields.get("OC") is not None else provided_fields.get("organic_carbon")
    if oc_val is not None:
        known_inputs.append("Soil organic carbon")
    else:
        missing_inputs.append("Soil organic carbon: Critical for determining biological soil health and manure requirements.")

    # NPK
    n_val = provided_fields.get("N") if provided_fields.get("N") is not None else provided_fields.get("nitrogen")
    p_val = provided_fields.get("P") if provided_fields.get("P") is not None else provided_fields.get("phosphorus")
    k_val = provided_fields.get("K") if provided_fields.get("K") is not None else provided_fields.get("potassium")

    if n_val is not None:
        known_inputs.append("Nitrogen (N)")
    else:
        missing_inputs.append("Nitrogen (N): Essential for vegetative growth and balanced basal fertilization.")

    if p_val is not None:
        known_inputs.append("Phosphorus (P)")
    else:
        missing_inputs.append("Phosphorus (P): Required for root development and energy transfer.")

    if k_val is not None:
        known_inputs.append("Potassium (K)")
    else:
        missing_inputs.append("Potassium (K): Necessary for drought stress tolerance and disease resistance.")

    # EC
    ec_val = provided_fields.get("EC") if provided_fields.get("EC") is not None else provided_fields.get("ec")
    if ec_val is not None:
        known_inputs.append("Electrical Conductivity (EC)")
    else:
        missing_inputs.append("Electrical Conductivity (EC): Required to detect rootzone salinity constraints.")

    # Irrigation
    irrig_val = provided_fields.get("irrigation_available")
    if irrig_val is not None and irrig_val != "unknown":
        known_inputs.append("Irrigation source")
    else:
        missing_inputs.append("Irrigation source: Critical for gating high-water-demand crops.")

    impact_statement = (
        "Providing missing laboratory soil test readings (especially Organic Carbon and NPK) will unlock calibrated fertilizer recommendations "
        "and improve crop suitability confidence from preliminary agro-climatic baseline to field-specific precision."
        if missing_inputs else
        "All critical parameters are present. AgriN can provide maximum-confidence advisory."
    )

    actionable_guidance = (
        "Complete missing soil parameters by conducting a standard 12-parameter Soil Health Card (SHC) test "
        "at your nearest Krishi Vigyan Kendra (KVK) or district agricultural laboratory to upgrade advisory precision to HIGH."
        if missing_inputs else "All core agronomic parameters provided; advisory precision is maximized for this agro-climatic zone."
    )

    return {
        "known_parameters": known_inputs,
        "missing_parameters": missing_inputs,
        "impact_statement": impact_statement,
        "actionable_guidance": actionable_guidance
    }


def assess_data_quality(
    provided_fields: Dict[str, Any],
    weather_info: Optional[Dict[str, Any]] = None,
    geographic_resolution: Any = "DISTRICT"
) -> Dict[str, Any]:
    """
    Evaluates independent Data Quality (distinct from Agricultural Resilience and Model Confidence).
    Assesses:
    - Completeness
    - Freshness
    - Geographic precision
    - Source reliability
    - Measurement quality
    """
    reasons = []
    
    # Check if geographic_resolution is a coordinate dict
    if isinstance(geographic_resolution, dict):
        has_coords = ("lat" in geographic_resolution or "latitude" in geographic_resolution) and ("lon" in geographic_resolution or "longitude" in geographic_resolution)
        res_key = "PARCEL" if has_coords else "DISTRICT"
    else:
        res_key = str(geographic_resolution).upper()

    # 1. Completeness Evaluation
    soil_keys = [
        ("N", "nitrogen"),
        ("P", "phosphorus"),
        ("K", "potassium"),
        ("pH", "ph"),
        ("EC", "ec"),
        ("OC", "organic_carbon")
    ]
    present_soil = sum(
        1 for k1, k2 in soil_keys 
        if (provided_fields.get(k1) is not None and provided_fields.get(k1) != "") or 
           (provided_fields.get(k2) is not None and provided_fields.get(k2) != "")
    )
    
    weather_keys = ["temperature", "humidity", "rainfall"]
    present_weather = sum(1 for k in weather_keys if provided_fields.get(k) is not None or (weather_info and weather_info.get(k) is not None))
    
    farm_keys = ["state", "district", "season", "irrigation_available", "soil_type"]
    present_farm = sum(1 for k in farm_keys if provided_fields.get(k) is not None and provided_fields.get(k) != "")
    
    comp_score = (present_soil / len(soil_keys)) * 0.50 + (present_weather / len(weather_keys)) * 0.30 + (present_farm / max(1, len(farm_keys))) * 0.20
    comp_score = min(1.0, comp_score)
    completeness_pct = round(comp_score * 100.0, 1)

    if comp_score >= 0.75:
        reasons.append("Comprehensive soil, meteorological, and farm parameters supplied.")
    elif comp_score >= 0.50:
        reasons.append("Core agronomic fields provided; secondary micronutrients or specific irrigation details omitted.")
    else:
        reasons.append("Sparse input vector; critical soil chemistry parameters missing.")

    # 2. Freshness Evaluation
    is_live_weather = weather_info.get("is_live_data", True) if weather_info else True
    freshness_score = 0.90 if is_live_weather else 0.55
    if is_live_weather:
        reasons.append("Real-time meteorological observations fetched from live NWP weather service.")
    else:
        reasons.append("Live weather service unreachable; regional agro-climatic monthly climatology applied.")

    # 3. Geographic Precision
    geo_map = {
        "PARCEL": (1.0, "High-precision parcel GPS coordinates provided."),
        "VILLAGE": (0.85, "Village-level cadastral location provided."),
        "SUB_DISTRICT": (0.75, "Sub-district (Taluka/Tehsil) administrative boundary resolution."),
        "DISTRICT": (0.60, "District-level spatial resolution; soil and weather normalized to district centroid."),
        "STATE": (0.35, "Coarse state-level resolution.")
    }
    geo_score, geo_note = geo_map.get(res_key, (0.60, "Standard district centroid resolution."))
    reasons.append(geo_note)

    # 4. Source Reliability
    has_lab_soil = any(
        (provided_fields.get(k1) is not None or provided_fields.get(k2) is not None)
        for k1, k2 in soil_keys
    )
    source_score = 0.85 if has_lab_soil else 0.50
    if has_lab_soil:
        reasons.append("Farmer-supplied laboratory soil test readings utilized for nutrient diagnosis.")
    else:
        reasons.append("No laboratory soil test provided; baseline agro-climatic soil benchmarks utilized.")

    # 5. Composite Data Quality Index
    overall_quality_num = (0.35 * comp_score + 0.25 * freshness_score + 0.20 * geo_score + 0.20 * source_score)
    overall_quality_num = round(overall_quality_num, 2)

    if overall_quality_num >= 0.70:
        quality_level = "HIGH"
    elif overall_quality_num >= 0.45:
        quality_level = "MEDIUM"
    else:
        quality_level = "LOW"

    # Missing Data Guidance
    guidance = get_missing_data_guidance(provided_fields)

    return {
        "data_quality_level": quality_level,
        "data_quality_rating": quality_level,
        "score": overall_quality_num,
        "completeness_pct": completeness_pct,
        "metrics": {
            "completeness": round(comp_score, 2),
            "freshness": round(freshness_score, 2),
            "geographic_precision": round(geo_score, 2),
            "source_reliability": round(source_score, 2)
        },
        "reasons": reasons,
        "missing_data_guidance": guidance
    }

