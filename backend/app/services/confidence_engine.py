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
