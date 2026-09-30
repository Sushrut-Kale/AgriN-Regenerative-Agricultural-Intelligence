"""
AgriN — Regenerative Agriculture Intelligence Service
=====================================================

Evaluates scientifically grounded regenerative practices against a farm's
specific biophysical profile (soil test, water regime, local climate, crop system).

Adheres strictly to Track 4 principles:
- Transparent suitability scoring
- Clear trade-offs and complexity ratings
- Component-level readiness indicators without arbitrary fabricated composite scores
- Decoupled from pure crop selection (answers "What regenerative practice fits this farm?")
"""

import os
import json
import uuid
from datetime import datetime
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
PRACTICES_PATH = os.path.join(BASE_DIR, "knowledge", "regenerative", "practices.json")

_PRACTICES_CACHE = None


def load_practices() -> List[Dict[str, Any]]:
    """Load all regenerative practices from knowledge repository."""
    global _PRACTICES_CACHE
    if _PRACTICES_CACHE is None:
        if os.path.exists(PRACTICES_PATH):
            with open(PRACTICES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _PRACTICES_CACHE = data.get("practices", [])
        else:
            _PRACTICES_CACHE = []
    return _PRACTICES_CACHE


def evaluate_practice_suitability(
    practice: Dict[str, Any],
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any],
    target_crop: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate how well a specific regenerative practice fits a farm.
    Returns match score (0-100), suitability status, specific rationale, and caveats.
    """
    match_score = 70.0  # Baseline viability
    reasons = []
    limiting_factors = []

    state = farm_data.get("state", "Maharashtra")
    soil_type = (farm_data.get("soil_type") or "").lower()
    irrigation = farm_data.get("irrigation_available", "no")
    oc = soil_data.get("OC")
    n_val = soil_data.get("N")
    rainfall = env_data.get("rainfall") or 750.0

    # 1. Geographic Applicability
    regions = practice.get("applicability_regions", [])
    if "All States and Union Territories" in regions or any(r.lower() in state.lower() for r in regions):
        match_score += 10.0
        reasons.append(f"Well-adapted to regional agro-ecology of {state}")
    else:
        match_score -= 20.0
        limiting_factors.append(f"Not prioritized for primary trials in {state}")

    # 2. Crop Compatibility
    compat_crops = [c.lower() for c in practice.get("compatible_crops", [])]
    if "all" in compat_crops:
        match_score += 5.0
        reasons.append("Universal compatibility across cropping systems")
    elif target_crop and target_crop.lower() in compat_crops:
        match_score += 15.0
        reasons.append(f"High synergy with planned crop: {target_crop.title()}")
    elif target_crop:
        match_score -= 10.0
        limiting_factors.append(f"Less typical pairing with planned crop: {target_crop.title()}")

    # 3. Soil Organic Carbon & Nutrient Trigger
    target_soil = practice.get("target_soil_conditions", {})
    oc_max = target_soil.get("organic_carbon_percent_max")
    if oc is not None and oc_max is not None:
        if oc < oc_max:
            # Low organic carbon strongly benefits from carbon-building practices
            match_score += 15.0
            reasons.append(f"Directly addresses low soil organic carbon ({oc:.2f}%)")
        else:
            reasons.append(f"Adequate organic carbon ({oc:.2f}%); practice serves maintenance role")
    elif oc is None:
        reasons.append("Soil Organic Carbon data unrecorded — practice recommended conservatively")

    if n_val is not None and n_val < 280 and practice["practice_id"] in ["PRACTICE_CROP_ROTATION", "PRACTICE_COVER_CROPS", "PRACTICE_INM"]:
        match_score += 10.0
        reasons.append(f"Compensates for soil Nitrogen deficit ({n_val:.0f} kg/ha) biologically")

    # 4. Water Regime
    water_req = practice.get("water_requirement", "LOW")
    if irrigation == "no" and water_req in ["MODERATE", "HIGH"]:
        if rainfall < 600:
            match_score -= 15.0
            limiting_factors.append("Requires careful soil moisture timing in rainfed semi-arid zones")
    elif irrigation == "yes" and practice["practice_id"] == "PRACTICE_WATER_CONSERVATION":
        match_score += 10.0
        reasons.append("High return on investment for existing irrigated setup")

    # Final score bound
    final_score = round(max(10.0, min(100.0, match_score)), 1)

    if final_score >= 80:
        recommendation_tier = "Highly Recommended"
    elif final_score >= 60:
        recommendation_tier = "Recommended"
    elif final_score >= 40:
        recommendation_tier = "Conditionally Applicable"
    else:
        recommendation_tier = "Low Priority"

    return {
        "practice_id": practice["practice_id"],
        "name": practice["name"],
        "description": practice["description"],
        "match_score": final_score,
        "recommendation_tier": recommendation_tier,
        "implementation_complexity": practice.get("implementation_complexity", "MEDIUM"),
        "expected_benefits": practice.get("expected_benefits", []),
        "potential_tradeoffs": practice.get("potential_tradeoffs", []),
        "reasons": reasons,
        "limiting_factors": limiting_factors,
        "evidence_level": practice.get("evidence_level", "FIELD_VALIDATED"),
        "source_reference": practice.get("source_reference", "ICAR Agronomy Directives")
    }


def compute_regenerative_indicators(
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute component-level regenerative readiness indicators.
    DO NOT fabricate an arbitrary 0-100 composite score without ground truth.
    Explicitly report indicators where data exists, and mark missing dimensions as UNAVAILABLE.
    """
    oc = soil_data.get("OC")
    if oc is not None:
        if oc >= 0.75:
            soc_status = "Good (Sufficient)"
        elif oc >= 0.50:
            soc_status = "Moderate (Depleted)"
        else:
            soc_status = "Critical (Severely Deficient)"
    else:
        soc_status = "UNAVAILABLE (Requires Soil Lab Test)"

    prev_crop = farm_data.get("previous_crop")
    if prev_crop:
        diversity_status = "Active Multi-Season Tracking"
    else:
        diversity_status = "Monoculture Risk / History Unrecorded"

    water_source = farm_data.get("water_source")
    irrigation = farm_data.get("irrigation_available", "no")
    if irrigation == "yes" and water_source in ["drip", "sprinkler"]:
        water_conservation = "High (Micro-Irrigation Deployed)"
    elif irrigation == "yes":
        water_conservation = "Moderate (Conventional Irrigation)"
    else:
        water_conservation = "Rainfed Dependent (Conserving In-Situ Moisture Critical)"

    return {
        "methodology": "Component-Level Regenerative Indicators (ICAR Soil Quality Framework)",
        "soil_organic_matter": {
            "status": soc_status,
            "measured_oc_percent": oc,
            "target_benchmark": ">= 0.75% for tropical semi-arid soils"
        },
        "crop_diversity": {
            "status": diversity_status,
            "previous_crop": prev_crop or "Unspecified"
        },
        "water_conservation": {
            "status": water_conservation,
            "irrigation": irrigation,
            "water_source": water_source or "Not specified"
        },
        "tillage_intensity": {
            "status": "UNAVAILABLE",
            "note": "Requires on-field observation or farmer management log"
        },
        "residue_management": {
            "status": "UNAVAILABLE",
            "note": "Requires post-harvest farm record or high-res satellite residue index"
        },
        "biodiversity_enhancement": {
            "status": "UNAVAILABLE",
            "note": "Requires farm perimeter tree/hedge inventory"
        }
    }


def generate_regenerative_advisories(
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any],
    target_crop: Optional[str] = None,
    limit: int = 3
) -> List[AgriculturalAdvisory]:
    """
    Generate canonical AgriculturalAdvisory objects for the top regenerative practices.
    """
    practices = load_practices()
    evaluations = [
        evaluate_practice_suitability(p, farm_data, soil_data, env_data, target_crop)
        for p in practices
    ]
    evaluations.sort(key=lambda x: x["match_score"], reverse=True)
    top_practices = evaluations[:limit]

    advisories = []
    for ep in top_practices:
        sources = [
            DataSourceMetadata(
                source_name=ep.get("source_reference", "ICAR Agronomy Guidelines"),
                source_type=DataSourceType.AGRONOMIC_RULE,
                source_url="https://icar.org.in",
                retrieved_at=datetime.utcnow(),
                coverage=DataCoverage.FULL,
                resolution=DataResolution.STATE,
                license="Government Open Data"
            )
        ]
        confidence = ConfidenceMetadata(
            confidence=round(ep["match_score"] / 100.0, 2),
            confidence_level=DataConfidenceLevel.HIGH if ep["match_score"] >= 75 else DataConfidenceLevel.MEDIUM,
            coverage=DataCoverage.PARTIAL,
            data_resolution=DataResolution.DISTRICT,
            data_timestamp=datetime.utcnow(),
            sources=sources
        )

        actions = [
            f"Review implementation plan for {ep['name']} before sowing season.",
            f"Assess trade-off: {ep['potential_tradeoffs'][0]}" if ep["potential_tradeoffs"] else "Consult local KVK extension officer.",
            f"Expected benefit: {ep['expected_benefits'][0]}" if ep["expected_benefits"] else "Improves soil health."
        ]

        adv = AgriculturalAdvisory(
            advisory_id=f"adv-regen-{uuid.uuid4().hex[:8]}",
            farm_id=farm_data.get("district", "farm-session"),
            category=AdvisoryCategory.REGENERATIVE,
            priority=AdvisoryPriority.HIGH if ep["match_score"] >= 80 else AdvisoryPriority.MEDIUM,
            title=f"Regenerative Practice: {ep['name']}",
            recommendation=ep["description"],
            reasoning=ep["reasons"] + [f"Complexity: {ep['implementation_complexity']}", f"Evidence Level: {ep['evidence_level']}"],
            supporting_observations=[
                {"indicator": "Organic Carbon", "value": soil_data.get("OC")},
                {"indicator": "Nitrogen", "value": soil_data.get("N")},
                {"indicator": "Annual Rainfall", "value": env_data.get("rainfall")}
            ],
            actions=actions,
            confidence=confidence,
            data_sources=sources,
            created_at=datetime.utcnow()
        )
        advisories.append(adv)

    return advisories
