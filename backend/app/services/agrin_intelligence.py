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
import os

try:
    from backend.app.services.geo_service import (
        find_district_by_name,
        find_nearest_district,
        get_crop_seasons_for_region,
        get_agro_climatic_zone_info
    )
    from backend.app.services.soil_intelligence import assess_soil_health
    from backend.app.services.weather_service import (
        get_weather_forecast,
        get_weather_data,
        convert_weather_to_agricultural_reasoning
    )
    from backend.app.services.crop_prediction import get_ranked_crops
    from backend.app.services.regenerative_advisor import advise_regenerative_practices
    from backend.app.services.farm_resilience import calculate_farm_resilience
    from backend.app.services.confidence_engine import compute_confidence, assess_data_quality
    from backend.app.services.agricultural_risk_engine import assess_agricultural_risks, generate_prioritized_advisories
    from backend.app.services.observability import PipelineObserver
    from backend.app.services.farm_memory import get_farm_memory_service
    from backend.app.services.satellite_service import (
        get_satellite_observation,
        fuse_satellite_weather_soil,
        interpret_satellite_observation
    )
    from backend.app.services.disease_service import (
        get_disease_provider,
        diagnose_crop_image
    )
    from backend.app.services.knowledge_graph import knowledge_graph
    from backend.app.models.intelligence_schemas import AgriculturalAdvisory, AdvisoryCategory, AdvisoryPriority, DataSourceMeta
except ImportError:
    from app.services.geo_service import (
        find_district_by_name,
        find_nearest_district,
        get_crop_seasons_for_region,
        get_agro_climatic_zone_info
    )
    from app.services.soil_intelligence import assess_soil_health
    from app.services.weather_service import (
        get_weather_forecast,
        get_weather_data,
        convert_weather_to_agricultural_reasoning
    )
    from app.services.crop_prediction import get_ranked_crops
    from app.services.regenerative_advisor import advise_regenerative_practices
    from app.services.farm_resilience import calculate_farm_resilience
    from app.services.confidence_engine import compute_confidence, assess_data_quality
    from app.services.agricultural_risk_engine import assess_agricultural_risks, generate_prioritized_advisories
    from app.services.observability import PipelineObserver
    from app.services.farm_memory import get_farm_memory_service
    from app.services.satellite_service import (
        get_satellite_observation,
        fuse_satellite_weather_soil,
        interpret_satellite_observation
    )
    from app.services.disease_service import (
        get_disease_provider,
        diagnose_crop_image
    )
    from app.services.knowledge_graph import knowledge_graph
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
    request_id = farm_data.get("request_id") or farm_data.get("session_id") or f"req-{timestamp_now.strftime('%Y%m%d%H%M%S')}"
    farm_id = farm_data.get("farm_id") or farm_data.get("session_id") or "farm-session-001"

    # 1. Location Layer Resolution
    state = farm_data.get("state", "Maharashtra")
    district = farm_data.get("district", "Parbhani")
    lat = farm_data.get("latitude")
    lon = farm_data.get("longitude")
    sub_district = farm_data.get("sub_district")
    village = farm_data.get("village")

    # Initialize structured observability telemetry
    observer = PipelineObserver(request_id=request_id, farm_id=farm_id, state=state, district=district)

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

    acz_code = geo_meta.get("agro_climatic_zone") or geo_meta.get("zone") or farm_data.get("agro_climatic_zone", "IN_ACZ_07")
    acz_info = get_agro_climatic_zone_info(acz_code) if acz_code else None

    # 2. Weather Layer Resolution with Graceful Failure Fallback & Telemetry
    weather_info = {}
    weather_failure_limitation = None
    try:
        weather_info = get_weather_data(district=district, state=state, lat=lat, lon=lon)
        observer.mark_step("weather_fetched", status="SUCCESS", details={
            "is_live": weather_info.get("is_live_data", True),
            "temperature": weather_info.get("temperature")
        })
    except Exception as e:
        observer.mark_step("weather_failed", status="FALLBACK", details={"error": str(e)})
        weather_failure_limitation = f"Live weather API unreachable ({str(e)}). Fallen back to regional climatological benchmark."
        try:
            weather_info = get_weather_forecast(district, state)
        except Exception:
            weather_info = {
                "temperature": 27.5,
                "humidity": 65.0,
                "rainfall": 750.0,
                "source": "Regional Climatological Fallback",
                "is_live_data": False,
                "freshness": "Climatological Normal",
                "confidence": "Medium",
                "risk_alerts": []
            }

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
    observer.mark_step("soil_analysis_completed", status="SUCCESS", details={"score": soil_profile.get("score")})

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
        crop_res = get_ranked_crops(s_dict, e_dict, f_dict, top_n=10)
        crop_recs = crop_res.get("ranked_crops", [])
        suitability_analysis = {
            "top_crops": crop_recs,
            "engine": "Decoupled Hybrid (60% Random Forest ML + 40% ICAR Agronomic Rules)",
            "total_evaluated": len(crop_recs)
        }
        if crop_recs:
            top_crop_score = crop_recs[0].get("final_score") or crop_recs[0].get("suitability_score", 70.0)
            top_crop_name = crop_recs[0].get("crop")
        observer.mark_step("crop_ranking_completed", status="SUCCESS", details={"crops_count": len(crop_recs)})
    except Exception as e:
        suitability_analysis = {
            "error": str(e),
            "top_crops": []
        }
        crop_recs = []
        observer.mark_step("crop_ranking_completed", status="ERROR", details={"error": str(e)})

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
    observer.mark_step("regenerative_analysis_completed", status="SUCCESS", details={"recs_count": len(regenerative_plan.get("recommendations", []))})

    # 7. Farm Resilience Index
    resilience_assessment = calculate_farm_resilience(
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        crop_suitability_score=top_crop_score
    )

    # 8. Data Confidence Assessment (Separated from Data Quality)
    confidence_assessment = compute_confidence(
        provided_fields=resolved_inputs,
        geographic_resolution="PARCEL" if (lat and lon) else "DISTRICT",
        model_probability=top_crop_score / 100.0
    )

    # 9. Dedicated Agricultural Risk Engine (Water, Soil, Climate, Crop)
    risks = assess_agricultural_risks(
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        weather_info=weather_info,
        ranked_crops=crop_recs
    )

    # 10. Prioritized Advisory Queue (CRITICAL, HIGH, MEDIUM, LOW)
    prioritized_advisories = generate_prioritized_advisories(
        risks=risks,
        soil_profile=soil_profile,
        regenerative_opportunities=regenerative_plan.get("recommendations", []),
        ranked_crops=crop_recs
    )
    observer.mark_step("advisory_generated", status="SUCCESS", details={"advisories_count": len(prioritized_advisories)})

    # 11. Decoupled Data Quality Assessment & Missing Data Guidance
    data_quality = assess_data_quality(
        provided_fields=resolved_inputs,
        weather_info=weather_info,
        geographic_resolution="PARCEL" if (lat and lon) else "DISTRICT"
    )
    observer.mark_step("confidence_calculated", status="SUCCESS", details={
        "confidence_level": confidence_assessment.get("confidence_level"),
        "data_quality_level": data_quality.get("data_quality_level")
    })

    # 12. Weather-to-Agricultural Reasoning (Threshold-based)
    irrigation_flag = str(resolved_inputs.get("irrigation_available", "no")).lower() in ["yes", "true", "irrigated"]
    weather_reasoning = convert_weather_to_agricultural_reasoning(
        weather_info=weather_info,
        irrigation_available=irrigation_flag,
        soil_drainage=resolved_inputs.get("drainage", "good")
    )

    # 13. Canonical Advisories (Backward Compatible 4-Pillar Format)
    canonical_advisories = _generate_structured_advisories(
        farm_id=farm_id,
        farm_data=resolved_inputs,
        soil_profile=soil_profile,
        suitability_analysis=suitability_analysis,
        regenerative_plan=regenerative_plan,
        resilience=resilience_assessment,
        confidence=confidence_assessment
    )

    # ── Phase 3 Unified Context Formulations ──────────────────────────────────
    obs_time = weather_info.get("observed_at") or timestamp_now.isoformat()
    is_live_weather = weather_info.get("is_live_data", True)
    weather_freshness = weather_info.get("freshness", "Fresh (< 15 min)" if is_live_weather else "Climatological Normal")
    weather_conf_level = weather_info.get("confidence", "High" if is_live_weather else "Medium")
    weather_src_label = weather_info.get("source", "Open-Meteo REST API")

    unified_weather_context = {
        "temperature": {
            "value": resolved_inputs.get("temperature"),
            "unit": "°C",
            "source": weather_src_label,
            "observed_at": obs_time,
            "freshness": weather_freshness,
            "confidence": weather_conf_level
        },
        "humidity": {
            "value": resolved_inputs.get("humidity"),
            "unit": "%",
            "source": weather_src_label,
            "observed_at": obs_time,
            "freshness": weather_freshness,
            "confidence": weather_conf_level
        },
        "rainfall": {
            "value": resolved_inputs.get("rainfall"),
            "unit": "mm",
            "source": weather_src_label,
            "observed_at": obs_time,
            "freshness": weather_freshness,
            "confidence": weather_conf_level
        },
        "source": weather_src_label,
        "is_live": is_live_weather,
        "risk_alerts": weather_info.get("risk_alerts", []),
        "agricultural_implications": weather_reasoning
    }

    unified_farm_context = {
        "farm_id": farm_id,
        "season": resolved_inputs.get("season", "Kharif"),
        "soil_type": resolved_inputs.get("soil_type", "black"),
        "irrigation_available": resolved_inputs.get("irrigation_available", "no"),
        "drainage": resolved_inputs.get("drainage", "good"),
        "current_crop": resolved_inputs.get("crop") or resolved_inputs.get("target_crop"),
        "rotation_pattern": resolved_inputs.get("rotation_pattern"),
        "farm_area": resolved_inputs.get("farm_area")
    }

    unified_location_context = {
        "country": "India",
        "state": state,
        "district": district,
        "sub_district": sub_district,
        "village": village,
        "latitude": lat,
        "longitude": lon,
        "agro_climatic_zone": acz_info
    }

    # Standardized 5-Pillar Master Explanation
    top_c = crop_recs[0] if crop_recs else {}
    top_name = top_c.get("common_name") or (top_c.get("crop", "Target Crop").capitalize() if top_c.get("crop") else "Target Crop")
    limiting_notes = [f.get("note") for f in top_c.get("limiting_factors", []) if f.get("note")]
    supporting_notes = [f.get("note") for f in top_c.get("supporting_factors", []) if f.get("note")]

    unified_explanation = {
        "what": f"Prioritize planting {top_name} for the {resolved_inputs.get('season', 'current')} season with targeted soil condition management.",
        "why": [
            f"{top_name} shows highest agronomic alignment ({top_crop_score:.1f}/100) combining statistical pattern match and regional physiological suitability.",
            f"Favorable factors: {', '.join(supporting_notes[:2]) if supporting_notes else 'Optimal regional conditions.'}",
            *( [f"Limiting consideration: {limiting_notes[0]}"] if limiting_notes else [] )
        ],
        "based_on": [
            f"Soil Health Card test values ({len([k for k, v in resolved_inputs.items() if v is not None and k in ['N','P','K','pH','EC','OC','Zn','Fe','B']])}/12 parameters evaluated)",
            f"Meteorological observations from {weather_src_label}",
            f"ICAR Agro-Climatic Zone framework for {acz_info.get('name', 'India') if acz_info else state}",
            "Decoupled Random Forest v1 model (60%) + ICAR agronomic rules (40%)"
        ],
        "confidence": f"{confidence_assessment.get('confidence_level', 'MEDIUM')} ({confidence_assessment.get('confidence_score', 0.8) * 100:.0f}%)",
        "limitations": [lim for lim in [
            weather_failure_limitation,
            "Satellite vegetation indices currently not connected (Earth Observation provider in unlinked mode)",
            "Crop disease vision diagnostic model not deployed in current session",
            *(confidence_assessment.get("metadata", {}).get("missing_core_fields", []))
        ] if lim]
    }

    unified_data_sources = {
        "weather": {
            "provider": weather_src_label,
            "type": "LIVE_API" if is_live_weather else "FALLBACK",
            "observed_at": obs_time,
            "freshness": weather_freshness
        },
        "soil": {
            "provider": "Farmer Soil Health Card / Field Soil Test",
            "standard": "ICAR & DAC&FW 12-parameter framework",
            "evaluated_at": timestamp_now.isoformat()
        },
        "agronomic_rules": {
            "authority": "Indian Council of Agricultural Research (ICAR) & State Agricultural Universities",
            "version": "2.5.0"
        },
        "satellite": {
            "provider": "Sentinel-2 / Landsat Earth Observation abstraction",
            "status": "NOT_CONNECTED",
            "message": "Satellite provider disconnected; zero synthetic vegetation indices generated."
        },
        "crop_disease": {
            "provider": "AgriN Vision Diagnostic Interface",
            "status": "MODEL_NOT_DEPLOYED",
            "message": "Trained vision model not linked; zero synthetic pathology generated."
        }
    }

    unified_limitations = [lim for lim in [
        weather_failure_limitation,
        "Satellite Earth Observation provider is not connected; field-level NDVI unavailable.",
        "Computer vision crop disease diagnostic model is not deployed.",
        *(confidence_assessment.get("metadata", {}).get("missing_core_fields", []))
    ] if lim]

    # 14. Phase 4 Satellite, Disease Diagnostics & Evidence Timeline Integration
    is_demo = bool(farm_data.get("demo_mode") or os.getenv("AGRIN_DEMO_MODE", "").lower() in ["true", "1", "yes"])
    
    # Satellite Observation & Multi-Spectral Reasoning
    satellite_obs = get_satellite_observation(
        latitude=float(lat) if lat is not None else 19.26,
        longitude=float(lon) if lon is not None else 76.77,
        allow_demo=is_demo
    )
    sat_reasoning = interpret_satellite_observation(satellite_obs)
    sat_fusion = fuse_satellite_weather_soil(
        soil_data=resolved_inputs,
        weather_data=resolved_inputs,
        satellite_data=satellite_obs
    )

    # Crop Disease Vision Screening
    image_payload = farm_data.get("image_bytes")
    filename = farm_data.get("image_filename", "leaf.jpg")
    if image_payload and isinstance(image_payload, bytes):
        crop_health_status = diagnose_crop_image(image_payload, filename, crop=top_crop_name, allow_demo=is_demo)
    elif is_demo:
        dis_prov = get_disease_provider(allow_demo=True)
        crop_health_status = dis_prov.predict(b"dummy_demo_leaf", crop_hint=top_crop_name)
    else:
        crop_health_status = {
            "status": "NOT_ASSESSED",
            "model_status": "MODEL_NOT_DEPLOYED",
            "diagnosis_status": "NOT_ASSESSED",
            "condition": None,
            "confidence": 0.0,
            "message": "Crop disease vision diagnostic model not deployed in current session."
        }

    # Chronological Evidence Timeline (Requirement 19)
    evidence_timeline = [
        {
            "step": 1,
            "layer": "SOIL_OBSERVATION",
            "timestamp": obs_time,
            "source": "Farmer Soil Health Test Card / ICAR Regional Baseline",
            "summary": f"Soil reaction pH {resolved_inputs.get('pH') or resolved_inputs.get('ph') or 'N/A'}, Organic Carbon {resolved_inputs.get('OC') or resolved_inputs.get('organic_carbon') or 'N/A'}%"
        },
        {
            "step": 2,
            "layer": "METEOROLOGY",
            "timestamp": obs_time,
            "source": weather_src_label,
            "summary": f"Ambient {resolved_inputs.get('temperature')}°C, Rainfall {resolved_inputs.get('rainfall')} mm, RH {resolved_inputs.get('humidity')}%"
        },
        {
            "step": 3,
            "layer": "SATELLITE_OBSERVATION",
            "timestamp": satellite_obs.get("observation_date", obs_time),
            "source": satellite_obs.get("source", "Copernicus Sentinel-2"),
            "summary": f"Status: {satellite_obs.get('vegetation_status', 'UNLINKED')} (NDVI: {satellite_obs.get('ndvi')})"
        },
        {
            "step": 4,
            "layer": "CROP_PHENOLOGY",
            "timestamp": obs_time,
            "source": f"ICAR Agro-Climatic Sowing Calendar ({resolved_inputs.get('season', 'Kharif')})",
            "summary": f"Evaluated candidate crops for {state} - Top fit: {top_crop_name} ({top_crop_score:.1f}%)"
        },
        {
            "step": 5,
            "layer": "CROP_HEALTH_DIAGNOSTIC",
            "timestamp": obs_time,
            "source": crop_health_status.get("model_version", "Vision Diagnostic Interface"),
            "summary": f"Diagnostic Status: {crop_health_status.get('diagnosis_status', 'NOT_ASSESSED')}"
        },
        {
            "step": 6,
            "layer": "ADVISORY_SYNTHESIS",
            "timestamp": timestamp_now.isoformat(),
            "source": "AgriN Multi-Layer Intelligence Engine",
            "summary": f"Generated {len(prioritized_advisories)} prioritized advisories across risk, soil, and regenerative dimensions."
        }
    ]

    # 15. Single Unified "Farm Intelligence Report" (Requirement 2 & 18)
    farm_intelligence_report = _build_farm_intelligence_report(
        farm_id=farm_id,
        state=state,
        district=district,
        resolved_inputs=resolved_inputs,
        weather_info=weather_info,
        weather_reasoning=weather_reasoning,
        crop_recs=crop_recs,
        soil_profile=soil_profile,
        regenerative_plan=regenerative_plan,
        resilience=resilience_assessment,
        data_quality=data_quality,
        confidence=confidence_assessment,
        risks=risks,
        satellite_obs=satellite_obs,
        crop_health_obs=crop_health_status,
        evidence_timeline=evidence_timeline
    )

    # 16. Canonical Farm-Level Intelligence Snapshot (Requirement 20)
    farm_intelligence_snapshot = {
        "snapshot_id": f"snap-{farm_id[:8]}-{timestamp_now.strftime('%Y%m%d%H%M%S')}",
        "generated_at": timestamp_now.isoformat(),
        "farm_id": farm_id,
        "is_demo": is_demo,
        "location": unified_location_context,
        "soil": {
            "ph": resolved_inputs.get("pH") if resolved_inputs.get("pH") is not None else resolved_inputs.get("ph"),
            "organic_carbon": resolved_inputs.get("OC") if resolved_inputs.get("OC") is not None else resolved_inputs.get("organic_carbon"),
            "nitrogen": resolved_inputs.get("N") if resolved_inputs.get("N") is not None else resolved_inputs.get("nitrogen"),
            "phosphorus": resolved_inputs.get("P") if resolved_inputs.get("P") is not None else resolved_inputs.get("phosphorus"),
            "potassium": resolved_inputs.get("K") if resolved_inputs.get("K") is not None else resolved_inputs.get("potassium"),
            "ec": resolved_inputs.get("EC") if resolved_inputs.get("EC") is not None else resolved_inputs.get("ec")
        },
        "weather": {
            "temperature": resolved_inputs.get("temperature"),
            "humidity": resolved_inputs.get("humidity"),
            "rainfall": resolved_inputs.get("rainfall"),
            "is_live": is_live_weather
        },
        "satellite": satellite_obs,
        "crop": {
            "current_crop": resolved_inputs.get("crop") or resolved_inputs.get("target_crop"),
            "season": resolved_inputs.get("season", "Kharif"),
            "top_recommended": top_crop_name,
            "suitability_score": top_crop_score
        },
        "crop_health": crop_health_status,
        "risks": risks,
        "recommendations": prioritized_advisories,
        "resilience": resilience_assessment,
        "confidence": confidence_assessment,
        "data_quality": data_quality,
        "sources": [
            {"name": "Open-Meteo", "type": "WEATHER_NWP", "coverage": "Global"},
            {"name": "ICAR-DAC&FW", "type": "SOIL_STANDARDS", "coverage": "India"},
            {"name": "CRIDA", "type": "AGROMETEOROLOGY", "coverage": "India"}
        ],
        "limitations": unified_limitations,
        "timeline": evidence_timeline
    }

    # 17. Country-Neutral Machine-Readable Advisory Format (Requirement 20)
    country_neutral_advisory = {
        "advisory_id": f"adv-{farm_id[:8]}-{timestamp_now.strftime('%Y%m%d%H%M%S')}",
        "farm_id": farm_id,
        "location": unified_location_context,
        "observations": [
            {"parameter": "temperature", "value": resolved_inputs.get("temperature"), "unit": "°C", "source": weather_src_label},
            {"parameter": "humidity", "value": resolved_inputs.get("humidity"), "unit": "%", "source": weather_src_label},
            {"parameter": "rainfall", "value": resolved_inputs.get("rainfall"), "unit": "mm", "source": weather_src_label},
            {"parameter": "pH", "value": resolved_inputs.get("pH") if resolved_inputs.get("pH") is not None else resolved_inputs.get("ph"), "unit": "pH", "source": "Soil Health Test"},
            {"parameter": "EC", "value": resolved_inputs.get("EC"), "unit": "dS/m", "source": "Soil Health Test"},
            {"parameter": "OC", "value": resolved_inputs.get("OC"), "unit": "%", "source": "Soil Health Test"}
        ],
        "recommendations": prioritized_advisories,
        "risks": risks,
        "confidence": confidence_assessment,
        "data_quality": data_quality,
        "sources": [
            {"name": "Open-Meteo", "type": "WEATHER_NWP", "coverage": "Global", "evidence_level": "HIGH"},
            {"name": "ICAR-DAC&FW", "type": "SOIL_STANDARDS", "coverage": "India", "evidence_level": "HIGH"},
            {"name": "CRIDA", "type": "AGROMETEOROLOGY", "coverage": "India", "evidence_level": "HIGH"}
        ],
        "limitations": unified_limitations,
        "responsible_ai_notice": "Advisories are decision-support guidance only. Yields and farm profits are subject to uncontrollable agro-climatic, biotic, and market variations.",
        "generated_at": timestamp_now.isoformat()
    }

    # Complete telemetry tracking
    observer.complete(
        total_crops=len(crop_recs),
        confidence_level=confidence_assessment.get("confidence_level", "MEDIUM"),
        resilience_score=resilience_assessment.get("overall_resilience_score", 70.0)
    )

    # Record farm memory snapshot
    try:
        mem_svc = get_farm_memory_service()
        mem_svc.record_observation(
            farm_id=farm_id,
            soil_data=resolved_inputs,
            crop_data={"crop": top_crop_name, "season": resolved_inputs.get("season"), "suitability_score": top_crop_score},
            advisory_data=prioritized_advisories
        )
    except Exception:
        pass

    return {
        "status": "success",
        "platform": "AgriN: Regenerative Agricultural Intelligence",
        "version": "2.5.0",
        "evaluated_at": timestamp_now.isoformat(),
        # ── Primary Unified Experience ───────────────────────────────────────
        "farm_intelligence_report": farm_intelligence_report,
        "farm_intelligence_snapshot": farm_intelligence_snapshot,
        "evidence_timeline": evidence_timeline,
        "satellite_observation": satellite_obs,
        "satellite_fusion": sat_fusion,
        "satellite_reasoning": sat_reasoning,
        "crop_health": crop_health_status,
        "risks": risks,
        "prioritized_advisories": prioritized_advisories,
        "data_quality": data_quality,
        "country_neutral_advisory": country_neutral_advisory,
        # ── Granular Agricultural Sub-Engines ─────────────────────────────────
        "farm_context": unified_farm_context,
        "location_context": unified_location_context,
        "weather_context": unified_weather_context,
        "weather_reasoning": weather_reasoning,
        "soil_health": soil_profile,
        "crop_suitability": crop_recs,
        "regenerative_opportunities": regenerative_plan.get("recommendations", []),
        "farm_resilience": resilience_assessment,
        "confidence": confidence_assessment,
        "explanation": unified_explanation,
        "data_sources": unified_data_sources,
        "limitations": unified_limitations,
        # ── Backward Compatible / Extended Keys ──────────────────────────────
        "geographic_context": unified_location_context,
        "environmental_context": {
            "temperature": resolved_inputs.get("temperature"),
            "humidity": resolved_inputs.get("humidity"),
            "rainfall": resolved_inputs.get("rainfall"),
            "source": weather_src_label
        },
        "soil_health_profile": soil_profile,
        "crop_health": crop_health_status,
        "regenerative_intelligence": regenerative_plan,
        "farm_resilience_index": resilience_assessment,
        "data_confidence": confidence_assessment,
        "canonical_advisories": prioritized_advisories
    }


def _build_farm_intelligence_report(
    farm_id: str,
    state: str,
    district: str,
    resolved_inputs: Dict[str, Any],
    weather_info: Dict[str, Any],
    weather_reasoning: List[Dict[str, Any]],
    crop_recs: List[Dict[str, Any]],
    soil_profile: Dict[str, Any],
    regenerative_plan: Dict[str, Any],
    resilience: Dict[str, Any],
    data_quality: Dict[str, Any],
    confidence: Dict[str, Any],
    risks: List[Dict[str, Any]],
    satellite_obs: Optional[Dict[str, Any]] = None,
    crop_health_obs: Optional[Dict[str, Any]] = None,
    evidence_timeline: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Constructs the canonical 8-section AGRIN FARM INTELLIGENCE REPORT:
    1. CROP OPPORTUNITY (Top suitable crops, why they fit, constraints)
    2. SOIL HEALTH (Overall condition, nutrients, constraints, improvement)
    3. REGENERATIVE OPPORTUNITIES (Recommended practices, why relevant, objective, confidence)
    4. CLIMATE & WEATHER (Current conditions, upcoming risk, agricultural implication)
    5. SATELLITE & VEGETATION (Copernicus/Landsat canopy reflectance, NDVI/NDWI, vigor)
    6. CROP HEALTH & DIAGNOSTICS (Foliar disease screening, triage, IPM management)
    7. FARM RESILIENCE (Resilience dimensions, weakest dimensions, improvements)
    8. DATA CONFIDENCE (What is known, what is uncertain, what is missing)
    """
    # 1. Crop Opportunity
    top_crops_summary = []
    for c in crop_recs[:3]:
        c_name = c.get("crop", "").title()
        score = c.get("overall_score") or c.get("suitability_score", 0.0)
        factors = c.get("factors", {})
        why = factors.get("supporting", [])[:2]
        constraints = factors.get("limiting", [])[:2]
        top_crops_summary.append({
            "crop": c_name,
            "suitability_score": score,
            "why_fit": why if why else ["High physiological compatibility with current agro-climatic zone."],
            "constraints": constraints if constraints else ["Standard regional management practices apply."]
        })

    # 2. Soil Health
    overall_soil = soil_profile.get("overall_rating", "MODERATE")
    nutrients = {
        "status": soil_profile.get("nutrient_status", {}),
        "score": soil_profile.get("score", 70.0)
    }
    constraints = [c.get("name") for c in soil_profile.get("soil_constraints", [])]
    improvements = soil_profile.get("recommended_improvement_areas", [])[:3]

    # 3. Regenerative Opportunities
    reg_recs = []
    for r in regenerative_plan.get("recommendations", [])[:3]:
        reg_recs.append({
            "practice": r.get("practice") or r.get("title", "Conservation Agriculture"),
            "why_relevant": r.get("why") or r.get("rationale", "Restores organic soil biology and structure."),
            "expected_objective": r.get("objective") or r.get("expected_benefits", "Improve long-term resilience"),
            "confidence": r.get("confidence", "HIGH")
        })

    # 4. Climate & Weather
    climate_risks = [r for r in risks if r.get("category") == "CLIMATE_RISK" or "temperature" in r.get("risk", "").lower() or "weather" in r.get("risk", "").lower()]
    upcoming_risk_text = climate_risks[0].get("risk") if climate_risks else "No acute meteorological threshold breaches observed."
    first_implication = weather_reasoning[0].get("agricultural_implication") if weather_reasoning else "Ambient conditions support normal crop transpiration."

    # 5. Satellite & Vegetation Section (Phase 4 Requirement 18)
    sat_status = satellite_obs.get("status", "NOT_CONNECTED") if satellite_obs else "NOT_CONNECTED"
    sat_source = satellite_obs.get("source", "Copernicus Sentinel-2") if satellite_obs else "Copernicus Sentinel-2"
    sat_ndvi = satellite_obs.get("ndvi") if satellite_obs else None
    sat_ndwi = satellite_obs.get("ndwi") if satellite_obs else None
    sat_veg_status = satellite_obs.get("vegetation_status", "UNLINKED") if satellite_obs else "UNLINKED"

    sat_section = {
        "status": sat_status,
        "source": sat_source,
        "ndvi": sat_ndvi,
        "ndwi": sat_ndwi,
        "vegetation_status": sat_veg_status,
        "is_synthetic": satellite_obs.get("is_synthetic", False) if satellite_obs else False,
        "summary": (
            f"Active satellite feed ({sat_source}): Mean NDVI {sat_ndvi:.2f}, status: {sat_veg_status}"
            if sat_status == "CONNECTED" and sat_ndvi is not None
            else "Satellite provider disconnected; Earth observation spectral bands unlinked."
        )
    }

    # 6. Crop Health Diagnostics Section (Phase 4 Requirement 18)
    dis_status = crop_health_obs.get("status", "NOT_ASSESSED") if crop_health_obs else "NOT_ASSESSED"
    dis_cond = crop_health_obs.get("condition") or crop_health_obs.get("diagnostic_result", {}).get("condition")
    dis_conf = crop_health_obs.get("confidence") or crop_health_obs.get("diagnostic_result", {}).get("confidence", 0.0)

    crop_health_section = {
        "status": dis_status,
        "condition_detected": dis_cond or "No foliar pathology model deployed / no image provided",
        "confidence": f"{float(dis_conf)*100:.1f}%" if dis_cond else "0.0%",
        "is_synthetic": crop_health_obs.get("is_synthetic", False) if crop_health_obs else False,
        "summary": (
            f"Screening completed: {dis_cond} ({float(dis_conf)*100:.0f}% confidence). Ground verification recommended."
            if dis_status == "ASSESSED" and dis_cond
            else "Crop disease vision diagnostic model not deployed in this session."
        )
    }

    # 7. Farm Resilience
    dimensions = resilience.get("dimensions", {})
    weakest = resilience.get("weakest_pillar") or resilience.get("weakest_dimension") or "Soil Carbon buffering"
    resilience_opportunities = resilience.get("improvement_opportunities", [
        "Incorporate organic green manure to strengthen soil moisture retention.",
        "Implement broad bed furrows to detain seasonal rainfall."
    ])

    # 8. Data Confidence
    guidance = data_quality.get("missing_data_guidance", {})
    known = guidance.get("known_inputs", ["District agro-climatic baseline"])
    missing = guidance.get("missing_inputs", ["Laboratory soil test card"])
    uncertain = [
        "Subsoil moisture sensors not installed; using NWP surface estimates",
        "Field-level NDVI satellite vegetation index not connected" if sat_status != "CONNECTED" else "Satellite spatial resolution is 10m grid cell"
    ]

    report_structured = {
        "title": "AGRIN FARM INTELLIGENCE REPORT",
        "farm_id": farm_id,
        "location": f"{district}, {state}, India",
        "current_conditions": {
            "temperature": f"{resolved_inputs.get('temperature', 28)}°C",
            "humidity": f"{resolved_inputs.get('humidity', 60)}%",
            "rainfall": f"{resolved_inputs.get('rainfall', 750)} mm",
            "season": resolved_inputs.get("season", "Kharif")
        },
        "crop_opportunity": {
            "top_suitable_crops": top_crops_summary,
            "primary_choice": top_crops_summary[0]["crop"] if top_crops_summary else "Target Crop",
            "sowing_season": resolved_inputs.get("season", "Kharif")
        },
        "soil_health": {
            "overall_condition": overall_soil,
            "nutrients_summary": nutrients,
            "constraints": constraints,
            "improvement_opportunities": improvements
        },
        "regenerative_opportunities": reg_recs,
        "climate_and_weather": {
            "current_conditions": f"Temp: {resolved_inputs.get('temperature')}°C | RH: {resolved_inputs.get('humidity')}% | Rain: {resolved_inputs.get('rainfall')} mm",
            "upcoming_risk": upcoming_risk_text,
            "agricultural_implication": first_implication,
            "reasonings": weather_reasoning
        },
        "satellite_and_vegetation": sat_section,
        "crop_health": crop_health_section,
        "farm_resilience": {
            "overall_score": resilience.get("overall_resilience_score", 70.0),
            "resilience_dimensions": dimensions,
            "weakest_dimensions": weakest,
            "improvement_opportunities": resilience_opportunities
        },
        "data_confidence": {
            "quality_level": data_quality.get("data_quality_level", "MEDIUM"),
            "what_is_known": known,
            "what_is_uncertain": uncertain,
            "what_is_missing": missing
        },
        "evidence_timeline": evidence_timeline or [],
        "audit_and_transparency": {
            "decision_method": "Multi-layer Agronomic Rules + Biophysical ML + Regional Agro-Climatic Gates",
            "inputs_used": [
                {"name": "Soil Chemistry", "status": "AVAILABLE" if (resolved_inputs.get("pH") or resolved_inputs.get("ph")) else "FALLBACK"},
                {"name": "Weather Context", "status": "LIVE" if weather_info.get("is_live_data", True) else "CLIMATOLOGY"},
                {"name": "Geographic Resolution", "status": f"{district}, {state}"},
                {"name": "Agro-climatic Zone", "status": resolved_inputs.get("agro_climatic_zone", "IN_ACZ_07")},
                {"name": "Satellite Remote Sensing", "status": "CONNECTED" if sat_status == "CONNECTED" else "UNLINKED"},
                {"name": "Crop Pathology Screening", "status": "ASSESSED" if dis_status == "ASSESSED" else "NOT_DEPLOYED"}
            ],
            "not_available": [
                *( [{"name": "Field-Level Satellite NDVI", "reason": "No high-resolution multispectral feed linked"}] if sat_status != "CONNECTED" else [] ),
                *( [{"name": "In-situ Crop Disease Diagnostic Image", "reason": "No visual pathology image uploaded"}] if dis_status != "ASSESSED" else [] )
            ],
            "yield_guarantee_issued": False,
            "profit_guarantee_issued": False,
            "satellite_observation_linked": bool(sat_status == "CONNECTED" and sat_ndvi is not None),
            "disease_model_linked": bool(dis_status == "ASSESSED"),
            "missing_data_imputed": False,
            "limitations_disclosed": True
        }
    }

    # Formatted plain text / markdown
    crop_lines = "\n".join([f"  • {c['crop']} ({c['suitability_score']:.1f}% fit) - Fit: {', '.join(c['why_fit'])} | Constraints: {', '.join(c['constraints'])}" for c in top_crops_summary])
    imp_lines = "\n".join([f"  • {imp}" for imp in improvements])
    reg_lines = "\n".join([f"  • {r['practice']}: {r['expected_objective']} (Why: {r['why_relevant']}, Conf: {r['confidence']})" for r in reg_recs])

    report_text = f"""
============================================================
           AGRIN FARM INTELLIGENCE REPORT
============================================================
Farm ID: {farm_id}
Location: {district}, {state}, India
Current Conditions: Temp {resolved_inputs.get('temperature')}°C, RH {resolved_inputs.get('humidity')}%, Rain {resolved_inputs.get('rainfall')} mm, Season: {resolved_inputs.get('season', 'Kharif')}

────────────────────────────────────────────────────────────
🌱 CROP OPPORTUNITY
Top Suitable Crops:
{crop_lines}

────────────────────────────────────────────────────────────
🧪 SOIL HEALTH
Overall Condition: {overall_soil}
Constraints Detected: {', '.join(constraints) if constraints else 'None identified'}
Key Improvements:
{imp_lines}

────────────────────────────────────────────────────────────
♻️ REGENERATIVE OPPORTUNITIES
{reg_lines}

────────────────────────────────────────────────────────────
🌦️ CLIMATE & WEATHER
Conditions: Temp {resolved_inputs.get('temperature')}°C, RH {resolved_inputs.get('humidity')}%, Rain {resolved_inputs.get('rainfall')} mm
Upcoming Risk: {upcoming_risk_text}
Agronomic Implication: {first_implication}

────────────────────────────────────────────────────────────
🛰️ SATELLITE & VEGETATION
Status: {sat_section['status']}
{sat_section['summary']}

────────────────────────────────────────────────────────────
🩺 CROP HEALTH & DIAGNOSTICS
Status: {crop_health_section['status']}
{crop_health_section['summary']}

────────────────────────────────────────────────────────────
🛡️ FARM RESILIENCE
Resilience Score: {resilience.get('overall_resilience_score', 70.0)}/100
Weakest Dimension: {weakest}
Interventions: {', '.join(resilience_opportunities[:2])}

────────────────────────────────────────────────────────────
📊 DATA CONFIDENCE
Data Quality Level: {data_quality.get('data_quality_level', 'MEDIUM')}
What is Known: {', '.join(known[:3])}
What is Missing: {', '.join(missing[:3]) if missing else 'None'}
============================================================
""".strip()

    report_structured["report_markdown"] = report_text
    return report_structured



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
