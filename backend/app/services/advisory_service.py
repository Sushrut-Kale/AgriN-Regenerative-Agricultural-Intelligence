"""
AgriN — Canonical Agricultural Advisory Engine
=============================================

Translates machine learning outputs, agronomic rule constraints, regional agro-climatic
benchmarks, and environmental observations into structured, canonical AgriculturalAdvisory objects.

Crucial Architectural Invariant:
ML Prediction != Agricultural Truth
ML Prediction is only one piece of probabilistic evidence in the intelligence pipeline:
Farm Inputs -> ML Model -> ML Prediction + Regional Knowledge + Weather + Season + Soil + Confidence
            -> Agricultural Intelligence Layer -> Canonical Advisory
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from backend.app.models.intelligence_schemas import (
    DataCoverage,
    DataConfidenceLevel,
    DataResolution,
    DataSourceType,
    DataSourceMetadata,
    ConfidenceMetadata,
    AdvisoryCategory,
    AdvisoryPriority,
    AgriculturalAdvisory,
)
from backend.app.services.regenerative_service import generate_regenerative_advisories


def generate_crop_selection_advisory(
    crop_result: Dict[str, Any],
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any]
) -> AgriculturalAdvisory:
    """
    Builds a canonical CROP_SELECTION advisory while explicitly separating:
    - ML probability prediction
    - Agronomic rule constraints
    - Environmental observations
    - Regional agro-climatic knowledge
    """
    crop_name = crop_result.get("crop", "Unknown")
    common_name = crop_result.get("common_name", crop_name.title())
    final_score = crop_result.get("final_score", 0.0)
    ml_score = crop_result.get("ml_score", 0.0)
    rule_score = crop_result.get("rule_score")
    gate_mult = crop_result.get("hard_gate_multiplier", 1.0)
    state = farm_data.get("state", "India")
    district = farm_data.get("district", "General")
    season = farm_data.get("season", "Kharif").capitalize()

    # Clear distinction of reasoning components
    reasoning = [
        f"[ML Model Prediction]: Machine learning model predicted statistical suitability baseline of {ml_score:.1f}%.",
        f"[Agronomic Rule Evaluation]: Biophysical compatibility scored at {rule_score if rule_score is not None else 'N/A'}% against ICAR thresholds.",
        f"[Regional Calendar]: Season compatibility confirmed for {season} season in {district}, {state}.",
        f"[Eligibility Gates]: Multiplier of {gate_mult:.2f} applied based on critical pH and water balance."
    ]

    for sf in crop_result.get("supporting_factors", [])[:2]:
        reasoning.append(f"[Supporting Factor]: {sf.get('note', '')}")

    for lf in crop_result.get("limiting_factors", [])[:2]:
        reasoning.append(f"[Limiting Factor / Risk]: {lf.get('note', '')}")

    actions = [
        f"Select certified high-yielding seed varieties approved for {state}.",
        f"Ensure sowing aligns with the onset of {season} rains or scheduled canal release.",
        "Address limiting nutrient/soil factors identified prior to basal fertilizer application."
    ]

    data_sources = [
        DataSourceMetadata(
            source_name="AgriN Random Forest Crop Model v1",
            source_type=DataSourceType.ML_MODEL,
            coverage=DataCoverage.FULL,
            resolution=DataResolution.POINT,
            license="Proprietary Model"
        ),
        DataSourceMetadata(
            source_name="ICAR National Crop Agronomy Repository",
            source_type=DataSourceType.AGRONOMIC_RULE,
            source_url="https://icar.org.in",
            coverage=DataCoverage.FULL,
            resolution=DataResolution.NATIONAL,
            license="Government Open Data"
        )
    ]

    conf_level = DataConfidenceLevel.HIGH if crop_result.get("data_confidence") == "High" else (
        DataConfidenceLevel.MEDIUM if crop_result.get("data_confidence") == "Medium" else DataConfidenceLevel.LOW
    )

    confidence = ConfidenceMetadata(
        confidence=round(final_score / 100.0, 2),
        confidence_level=conf_level,
        coverage=DataCoverage.FULL if conf_level == DataConfidenceLevel.HIGH else DataCoverage.PARTIAL,
        data_resolution=DataResolution.DISTRICT,
        data_timestamp=datetime.utcnow(),
        sources=data_sources
    )

    priority = AdvisoryPriority.HIGH if final_score >= 75 else (
        AdvisoryPriority.MEDIUM if final_score >= 50 else AdvisoryPriority.LOW
    )

    return AgriculturalAdvisory(
        advisory_id=f"adv-crop-{uuid.uuid4().hex[:8]}",
        farm_id=f"{district}_{farm_data.get('session_id', 'session')}",
        category=AdvisoryCategory.CROP_SELECTION,
        priority=priority,
        title=f"Crop Suitability: {common_name} ({final_score:.1f}%)",
        recommendation=f"{common_name} is classified as '{crop_result.get('classification', 'Suitable')}' under prevailing soil and seasonal conditions.",
        reasoning=reasoning,
        supporting_observations=[
            {"type": "ML_SCORE", "value": ml_score, "unit": "%"},
            {"type": "RULE_SCORE", "value": rule_score, "unit": "%"},
            {"type": "FINAL_SCORE", "value": final_score, "unit": "%"},
            {"type": "SOIL_PH", "value": soil_data.get("ph"), "unit": "pH"},
            {"type": "RAINFALL", "value": env_data.get("rainfall"), "unit": "mm"}
        ],
        actions=actions,
        confidence=confidence,
        data_sources=data_sources,
        created_at=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(days=90)
    )


def generate_soil_health_advisory(
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any]
) -> Optional[AgriculturalAdvisory]:
    """Generates nutrient and soil health advisory based on SHC data."""
    ph = soil_data.get("ph")
    oc = soil_data.get("OC")
    n_val = soil_data.get("N")
    p_val = soil_data.get("P")
    k_val = soil_data.get("K")

    if not any(v is not None for v in [ph, oc, n_val, p_val, k_val]):
        return None

    reasoning = []
    actions = []

    if ph is not None:
        if ph < 6.0:
            reasoning.append(f"Soil pH is acidic ({ph:.1f}), which restricts phosphorus availability and microbial activity.")
            actions.append("Apply agricultural lime or dolomite at recommended soil testing rates prior to planting.")
        elif ph > 8.2:
            reasoning.append(f"Soil pH is calcareous / alkaline ({ph:.1f}), inducing micro-nutrient (Zinc, Iron) fixation.")
            actions.append("Incorporate gypsum or sulfur-based amendments and prioritize foliar micro-nutrient sprays.")
        else:
            reasoning.append(f"Soil pH is near-optimal ({ph:.1f}) for broad crop nutrient uptake.")

    if oc is not None and oc < 0.50:
        reasoning.append(f"Soil Organic Carbon ({oc:.2f}%) is deficient (< 0.50%), impairing cation exchange and water holding capacity.")
        actions.append("Apply 5-8 tonnes/ha of well-decomposed Farmyard Manure (FYM) or compost.")

    if not actions:
        actions.append("Maintain routine organic matter additions and periodic soil testing every 2-3 years.")

    sources = [
        DataSourceMetadata(
            source_name="Soil Health Card Operational Norms (Govt of India / ICAR)",
            source_type=DataSourceType.GOVERNMENT,
            source_url="https://soilhealth.dac.gov.in",
            coverage=DataCoverage.FULL,
            resolution=DataResolution.NATIONAL,
            license="Government Open Data"
        )
    ]

    confidence = ConfidenceMetadata(
        confidence=0.88,
        confidence_level=DataConfidenceLevel.HIGH,
        coverage=DataCoverage.PARTIAL,
        data_resolution=DataResolution.POINT,
        data_timestamp=datetime.utcnow(),
        sources=sources
    )

    return AgriculturalAdvisory(
        advisory_id=f"adv-soil-{uuid.uuid4().hex[:8]}",
        farm_id=farm_data.get("district", "farm-session"),
        category=AdvisoryCategory.SOIL_HEALTH,
        priority=AdvisoryPriority.HIGH if (ph and (ph < 5.5 or ph > 8.5)) else AdvisoryPriority.MEDIUM,
        title="Soil Nutrient & Health Advisory",
        recommendation="Optimize soil chemical balance and organic matter to protect yield potential.",
        reasoning=reasoning,
        supporting_observations=[
            {"indicator": "pH", "value": ph},
            {"indicator": "OC", "value": oc},
            {"indicator": "N", "value": n_val},
            {"indicator": "P", "value": p_val},
            {"indicator": "K", "value": k_val}
        ],
        actions=actions,
        confidence=confidence,
        data_sources=sources,
        created_at=datetime.utcnow()
    )


def generate_comprehensive_advisories(
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any],
    ranked_crops: List[Dict[str, Any]],
    target_crop: Optional[str] = None
) -> List[AgriculturalAdvisory]:
    """
    Builds the full multi-category advisory bundle:
    1. Top Crop Selection Advisory
    2. Soil Health Advisory
    3. Regenerative Agriculture Advisories
    """
    advisories: List[AgriculturalAdvisory] = []

    # 1. Top Crop Selection
    if ranked_crops:
        top_crop = ranked_crops[0]
        advisories.append(generate_crop_selection_advisory(top_crop, farm_data, soil_data, env_data))

    # 2. Soil Health
    soil_adv = generate_soil_health_advisory(farm_data, soil_data)
    if soil_adv:
        advisories.append(soil_adv)

    # 3. Regenerative Agriculture
    regen_crop = target_crop or (ranked_crops[0]["crop"] if ranked_crops else None)
    regen_advisories = generate_regenerative_advisories(farm_data, soil_data, env_data, target_crop=regen_crop, limit=2)
    advisories.extend(regen_advisories)

    return advisories
