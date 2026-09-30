"""
AgriN Intelligence Master Orchestrator
Coordinates multi-layer agricultural analysis across clean service boundaries:

                     AGRIN INTELLIGENCE
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
    LOCATION              SOIL                WEATHER
   (geo_service)   (soil_intelligence)    (weather_service)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                      CROP CONTEXT
                            ▼
                  AGRICULTURAL ANALYSIS
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
CROP SUITABILITY       SOIL HEALTH          CROP HEALTH
(ML + Rule Gates)   (Nutrients & Limits)  (Diagnostic State)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                   REGENERATIVE ADVISOR
                            ▼
                     FARM RESILIENCE
                            ▼
                      FARM ADVISORY
             (Canonical Multi-Category JSON)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from backend.app.services.geo_service import (
        find_district_by_name,
        find_nearest_district,
        get_crop_seasons_for_region,
        get_agro_climatic_zone_info
    )
    from backend.app.services.soil_intelligence import assess_soil_health
    from backend.app.services.weather_service import get_weather_forecast, get_weather_data
    from backend.app.services.crop_prediction import get_ranked_crops
    from backend.app.services.regenerative_advisor import advise_regenerative_practices
    from backend.app.services.farm_resilience import calculate_farm_resilience
    from backend.app.services.confidence_engine import compute_confidence
    from backend.app.models.intelligence_schemas import AgriculturalAdvisory, AdvisoryCategory, AdvisoryPriority, DataSourceMeta
except ImportError:
    from app.services.geo_service import (
        find_district_by_name,
        find_nearest_district,
        get_crop_seasons_for_region,
        get_agro_climatic_zone_info
    )
    from app.services.soil_intelligence import assess_soil_health
    from app.services.weather_service import get_weather_forecast, get_weather_data
    from app.services.crop_prediction import get_ranked_crops
    from app.services.regenerative_advisor import advise_regenerative_practices
    from app.services.farm_resilience import calculate_farm_resilience
    from app.services.confidence_engine import compute_confidence
    from app.models.intelligence_schemas import AgriculturalAdvisory, AdvisoryCategory, AdvisoryPriority, DataSourceMeta




def run_full_agricultural_intelligence(
    farm_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes the modular end-to-end AgriN Agricultural Intelligence pipeline.
    Preserves clean separation between:
    - Statistical Model Predictions
    - Grounded Agronomic Rules
    - Environmental Observations
    - Regenerative Advisories
    """
    timestamp_now = datetime.now(timezone.utc)

    # 1. Location Layer Resolution
    state = farm_data.get("state", "Maharashtra")
    district = farm_data.get("district", "Parbhani")
    lat = farm_data.get("latitude")
    lon = farm_data.get("longitude")
    sub_district = farm_data.get("sub_district")
    village = farm_data.get("village")

    # If coordinates are provided, resolve nearest district and ACZ
    geo_meta = {}
    if lat is not None and lon is not None:
        try:
            nearest = find_nearest_district(float(lat), float(lon))
            if nearest:
                if isinstance(nearest, tuple):
                    d_info, s_name = nearest
                    geo_meta = d_info
                    if not district:
                        district = d_info.get("name", "")
                    if not state:
                        state = s_name
                elif isinstance(nearest, dict):
                    geo_meta = nearest
                    if not district:
                        district = nearest.get("district", nearest.get("name", ""))
                    if not state:
                        state = nearest.get("state", "")
        except Exception:
            pass

    if not geo_meta and district:
        d_info = find_district_by_name(district, state)
        if d_info:
            geo_meta = d_info


    acz_code = geo_meta.get("agro_climatic_zone") or farm_data.get("agro_climatic_zone", "IN_ACZ_07")
    acz_info = get_agro_climatic_zone_info(acz_code) if acz_code else None

    # 2. Weather Layer Resolution
    weather_info = {}
    try:
        weather_info = get_weather_data(district=district, state=state, lat=lat, lon=lon)
    except Exception:
        # Fallback to forecast helper
        weather_info = get_weather_forecast(district, state)

    # Blend weather into working parameters if not explicitly provided
    resolved_inputs = dict(farm_data)
    if "temperature" not in resolved_inputs or resolved_inputs["temperature"] is None:
        if "temperature" in weather_info:
            resolved_inputs["temperature"] = weather_info["temperature"]
    if "humidity" not in resolved_inputs or resolved_inputs["humidity"] is None:
        if "humidity" in weather_info:
            resolved_inputs["humidity"] = weather_info["humidity"]
    if "rainfall" not in resolved_inputs or resolved_inputs["rainfall"] is None:
        if "rainfall" in weather_info:
            resolved_inputs["rainfall"] = weather_info["rainfall"]

    resolved_inputs["state"] = state
    resolved_inputs["district"] = district

    # 3. Soil Intelligence Layer
    soil_profile = assess_soil_health(
        soil_data=resolved_inputs,
        soil_type=resolved_inputs.get("soil_type")
    )

    # 4. Crop Suitability Analysis (Decoupled ML + Agronomic Rule Gates)
    suitability_analysis = {}
    top_crop_score = 70.0
    top_crop_name = None
    try:
        s_dict = {
            "N": resolved_inputs.get("N"),
            "P": resolved_inputs.get("P"),
            "K": resolved_inputs.get("K"),
            "S": resolved_inputs.get("S"),
            "Zn": resolved_inputs.get("Zn"),
            "Fe": resolved_inputs.get("Fe"),
            "Cu": resolved_inputs.get("Cu"),
            "Mn": resolved_inputs.get("Mn"),
            "B": resolved_inputs.get("B"),
            "ph": resolved_inputs.get("pH") if resolved_inputs.get("pH") is not None else resolved_inputs.get("ph"),
            "EC": resolved_inputs.get("EC"),
            "OC": resolved_inputs.get("OC"),
        }
        e_dict = {
            "temperature": resolved_inputs.get("temperature"),
            "humidity": resolved_inputs.get("humidity"),
            "rainfall": resolved_inputs.get("rainfall"),
        }
        f_dict = {
            "state": state,
            "district": district,
            "season": resolved_inputs.get("season", "Kharif"),
            "irrigation_available": resolved_inputs.get("irrigation_available", "no"),
            "soil_type": resolved_inputs.get("soil_type", "black"),
            "drainage": resolved_inputs.get("drainage", "good")
        }
        crop_res = get_ranked_crops(s_dict, e_dict, f_dict, top_n=5)
        crop_recs = crop_res.get("ranked_crops", [])
        suitability_analysis = {
            "top_crops": crop_recs,
            "engine": "Decoupled Hybrid (60% Random Forest ML + 40% ICAR Agronomic Rules)",
            "total_evaluated": len(crop_recs)
        }
        if crop_recs:
            top_crop_score = crop_recs[0].get("final_score") or crop_recs[0].get("suitability_score", 70.0)
            top_crop_name = crop_recs[0].get("crop")
    except Exception as e:
        suitability_analysis = {
            "error": str(e),
            "top_crops": []
        }


    # 5. Crop Health / Diagnostic Status (Honest Guardrail)
    crop_health_status = {
        "status": "NOT_ASSESSED",
        "message": "Real-time crop disease vision diagnostic model not deployed in current session.",
        "leaf_pathology_risk": "UNASSESSED",
        "confidence": 0.0
    }

    # 6. Regenerative Agriculture Advisor
    regenerative_plan = advise_regenerative_practices(
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        current_crop=top_crop_name or resolved_inputs.get("crop")
    )

    # 7. Farm Resilience Index — prototype
    resilience_assessment = calculate_farm_resilience(
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        crop_suitability_score=top_crop_score
    )

    # 8. Data Confidence Assessment
    confidence_assessment = compute_confidence(
        provided_fields=resolved_inputs,
        geographic_resolution="PARCEL" if (lat and lon) else "DISTRICT",
        model_probability=top_crop_score / 100.0
    )

    # 9. Synthesize Canonical Agricultural Advisories across 6 Categories
    advisories = _generate_structured_advisories(
        farm_id=farm_data.get("farm_id", "farm-session-001"),
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        suitability_analysis=suitability_analysis,
        regenerative_plan=regenerative_plan,
        resilience=resilience_assessment,
        confidence=confidence_assessment
    )

    return {
        "status": "success",
        "platform": "AgriN: Regenerative Agricultural Intelligence",
        "version": "2.5.0",
        "evaluated_at": timestamp_now.isoformat(),
        "geographic_context": {
            "country": "India",
            "state": state,
            "district": district,
            "sub_district": sub_district,
            "village": village,
            "latitude": lat,
            "longitude": lon,
            "agro_climatic_zone": acz_info
        },
        "environmental_context": {
            "temperature": resolved_inputs.get("temperature"),
            "humidity": resolved_inputs.get("humidity"),
            "rainfall": resolved_inputs.get("rainfall"),
            "source": weather_info.get("source", "Open-Meteo REST API")
        },
        "soil_health_profile": soil_profile,
        "crop_suitability": suitability_analysis,
        "crop_health": crop_health_status,
        "regenerative_intelligence": regenerative_plan,
        "farm_resilience_index": resilience_assessment,
        "data_confidence": confidence_assessment,
        "canonical_advisories": advisories
    }


def _generate_structured_advisories(
    farm_id: str,
    farm_data: Dict[str, Any],
    soil_profile: Dict[str, Any],
    suitability_analysis: Dict[str, Any],
    regenerative_plan: Dict[str, Any],
    resilience: Dict[str, Any],
    confidence: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates structured, explainable advisories answering:
    WHAT, WHY, BASED ON, CONFIDENCE, LIMITATIONS.
    """
    advisories = []
    top_crops = suitability_analysis.get("top_crops", [])

    # ADVISORY 1: CROP SELECTION
    if top_crops:
        top1 = top_crops[0]
        crop_name = top1.get("crop", "Target Crop").capitalize()
        score = top1.get("suitability_score", 0.0)

        supporting = top1.get("factors", {}).get("supporting", [])
        limiting = top1.get("factors", {}).get("limiting", [])

        advisories.append({
            "advisory_id": f"adv-crop-{farm_id[:8]}",
            "category": "CROP_SELECTION",
            "priority": "HIGH" if score >= 75.0 else "MEDIUM",
            "title": f"Crop Selection Recommendation: {crop_name} ({score:.1f}% Match)",
            "recommendation": f"Cultivate {crop_name} for the current season based on favorable soil chemistry and regional agro-climatic alignment.",
            "explainability": {
                "what": f"Recommended primary planting: {crop_name}",
                "why": supporting if supporting else ["Optimal physiological fit with current ambient temperature and season."],
                "based_on": ["Machine learning biophysical suitability (60%)", "ICAR regional season calendar gate (40%)", "Soil Health Card test vectors"],
                "confidence": f"{confidence.get('confidence_score', 0.8) * 100:.0f}% ({confidence.get('confidence_level', 'MEDIUM')})",
                "limitations": confidence.get("metadata", {}).get("missing_core_fields", [])
            },
            "actions": [
                f"Prepare seedbed according to {crop_name} regional ICAR package of practices.",
                "Procure certified high-yielding or drought-tolerant seed variety from official state seed corporation.",
                f"Address limiting factors prior to vegetative growth: {', '.join(limiting) if limiting else 'None critical'}"
            ],
            "valid_until": "End of Current Sowing Season"
        })

    # ADVISORY 2: SOIL IMPROVEMENT
    constraints = soil_profile.get("soil_constraints", [])
    if constraints:
        top_constraint = constraints[0]
        advisories.append({
            "advisory_id": f"adv-soil-{farm_id[:8]}",
            "category": "SOIL_HEALTH",
            "priority": "HIGH" if top_constraint.get("severity") in ["CRITICAL", "HIGH"] else "MEDIUM",
            "title": f"Soil Health Intervention: Alleviate {top_constraint.get('name')}",
            "recommendation": top_constraint.get("remediation"),
            "explainability": {
                "what": f"Remediate {top_constraint.get('name')}",
                "why": [top_constraint.get("impact", "Restores nutrient balance and soil physical structure.")],
                "based_on": [f"Observed value: {top_constraint.get('value')}", "Official DAC&FW critical agronomic thresholds"],
                "confidence": f"{soil_profile.get('confidence', 0.8) * 100:.0f}%",
                "limitations": ["Soil test represents plot average; micro-variations may exist across furrows."]
            },
            "actions": soil_profile.get("recommended_improvement_areas", [])[:3],
            "valid_until": "Prior to Next Basal Fertilizer Application"
        })

    # ADVISORY 3: WATER AWARENESS & CONSERVATION
    water_desc = resilience.get("water_assessment", "")
    advisories.append({
        "advisory_id": f"adv-water-{farm_id[:8]}",
        "category": "WATER_MANAGEMENT",
        "priority": "MEDIUM",
        "title": "Water Budgeting & In-Situ Moisture Conservation",
        "recommendation": "Adopt conservation tillage and broad bed furrow (BBF) to detain seasonal rainfall and prolong rootzone moisture.",
        "explainability": {
            "what": "In-situ moisture detention and water table buffering.",
            "why": [water_desc],
            "based_on": ["Irrigation source status", "Seasonal rainfall observations via Open-Meteo REST API"],
            "confidence": "85% (MEDIUM-HIGH)",
            "limitations": ["Live subsoil moisture sensor data not directly connected."]
        },
        "actions": [
            "Construct compartmental bunds or broad bed furrows across the field slope.",
            "Apply straw or crop residue mulch to suppress evaporative moisture loss by 25-35%.",
            "Schedule life-saving supplemental irrigation during critical flowering / grain filling stages."
        ],
        "valid_until": "Throughout Growth Cycle"
    })

    # ADVISORY 4: REGENERATIVE DIVERSITY & ROTATION
    recs = regenerative_plan.get("recommendations", [])
    if recs:
        reg_item = recs[0]
        advisories.append({
            "advisory_id": f"adv-reg-{farm_id[:8]}",
            "category": "REGENERATIVE",
            "priority": "MEDIUM",
            "title": f"Regenerative Practice: {reg_item.get('title')}",
            "recommendation": reg_item.get("rationale"),
            "explainability": {
                "what": reg_item.get("title"),
                "why": [reg_item.get("expected_benefits", "Enhances long-term soil health.")],
                "based_on": ["ICAR/CRIDA codified regenerative practice rules", "Soil Organic Carbon status"],
                "confidence": "90%",
                "limitations": ["Implementation depends on farmer machinery availability."]
            },
            "actions": reg_item.get("actions", []),
            "valid_until": "Next Crop Planning Cycle"
        })

    return advisories
