"""
AgriN — Agricultural Intelligence & Provenance Routes (Phase 2.5)
================================================================

Provides production endpoints for:
- Regenerative Agriculture Practices & Recommendation Engine
- Non-fabricated Farm Health Snapshots
- Canonical Multi-Category Agricultural Advisories
- Time-Series Farm Observations
- Farmer Advisory Feedback Loop
- Data Sources Catalog & System Coverage Matrix
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session

from backend.app.database.db import (
    get_db, FarmerSession, SoilRecord, EnvRecord, PredictionRecord,
    FarmObservationRecord, AdvisoryRecord, AdvisoryFeedbackRecord, FeedbackRecord
)
from backend.app.models.schemas import (
    AnalysisRequest,
    FarmObservationCreate, FarmObservationResponse,
    FarmHealthSnapshot, AgriculturalAdvisory, AdvisoryFeedbackInput,
    DataCoverage, DataConfidenceLevel, DataResolution, DataSourceType
)
from backend.app.services.regenerative_service import (
    load_practices, evaluate_practice_suitability,
    compute_regenerative_indicators, generate_regenerative_advisories
)
from backend.app.services.farm_health_service import build_farm_health_snapshot
from backend.app.services.advisory_service import generate_comprehensive_advisories
from backend.app.services.crop_prediction import get_ranked_crops
from backend.app.services.weather_service import fetch_live_weather
try:
    from backend.app.services.soil_intelligence import assess_soil_health
    from backend.app.services.regenerative_advisor import advise_regenerative_practices
    from backend.app.services.farm_resilience import calculate_farm_resilience
    from backend.app.services.agrin_intelligence import run_full_agricultural_intelligence
    from backend.app.services.disease_service import diagnose_crop_image, get_disease_provider
    from backend.app.services.satellite_service import (
        get_satellite_status_report,
        get_satellite_observation,
        analyze_satellite_time_series,
        get_satellite_provider
    )
    from backend.app.adapters import ADAPTER_REGISTRY, get_country_adapter
    from backend.app.adapters.brics import run_brics_interoperability_simulation
    from backend.app.services.geo_service import get_all_agro_climatic_zones, get_all_states
    from backend.app.services.crop_comparison import compare_crops
    from backend.app.services.knowledge_graph import knowledge_graph
except ImportError:
    from app.services.soil_intelligence import assess_soil_health
    from app.services.regenerative_advisor import advise_regenerative_practices
    from app.services.farm_resilience import calculate_farm_resilience
    from app.services.agrin_intelligence import run_full_agricultural_intelligence
    from app.services.disease_service import diagnose_crop_image, get_disease_provider
    from app.services.satellite_service import (
        get_satellite_status_report,
        get_satellite_observation,
        analyze_satellite_time_series,
        get_satellite_provider
    )
    from app.adapters import ADAPTER_REGISTRY, get_country_adapter
    from app.adapters.brics import run_brics_interoperability_simulation
    from app.services.geo_service import get_all_agro_climatic_zones, get_all_states
    from app.services.crop_comparison import compare_crops
    from app.services.knowledge_graph import knowledge_graph



router = APIRouter()


# ── 1. Regenerative Agriculture Endpoints ─────────────────────────────────────

@router.get("/regenerative/practices")
def list_regenerative_practices():
    """Retrieve all scientifically validated regenerative agricultural practices."""
    practices = load_practices()
    return {
        "success": True,
        "total_practices": len(practices),
        "practices": practices
    }


@router.post("/regenerative/recommend")
def recommend_regenerative_practices(request: AnalysisRequest):
    """
    Evaluates regenerative practices against farm soil, water, and climate parameters.
    Returns ranked practices and component-level regenerative readiness indicators.
    """
    farm_dict = request.farm_data.model_dump()
    soil_dict = request.soil_data.model_dump()
    env_dict = request.env_data.model_dump()

    practices = load_practices()
    evaluations = [
        evaluate_practice_suitability(p, farm_dict, soil_dict, env_dict)
        for p in practices
    ]
    evaluations.sort(key=lambda x: x["match_score"], reverse=True)

    indicators = compute_regenerative_indicators(farm_dict, soil_dict, env_dict)

    return {
        "success": True,
        "ranked_practices": evaluations,
        "regenerative_indicators": indicators
    }


# ── 2. Farm Health Snapshot Endpoints ─────────────────────────────────────────

@router.post("/farms/{farm_id}/health", response_model=FarmHealthSnapshot)
def get_farm_health(farm_id: str, request: Optional[AnalysisRequest] = None, db: Session = Depends(get_db)):
    """
    Generates a scientifically grounded FarmHealthSnapshot.
    Satellite and disease components explicitly report UNAVAILABLE unless live data exists.
    """
    if request:
        farm_dict = request.farm_data.model_dump()
        soil_dict = request.soil_data.model_dump()
        env_dict = request.env_data.model_dump()
    else:
        # Attempt to load from existing session in database
        sess = db.query(FarmerSession).filter(FarmerSession.session_id == farm_id).first()
        soil_rec = db.query(SoilRecord).filter(SoilRecord.session_id == farm_id).first()
        env_rec = db.query(EnvRecord).filter(EnvRecord.session_id == farm_id).first()

        farm_dict = {"state": sess.state, "district": sess.district} if sess else {"state": "Maharashtra", "district": "Parbhani"}
        soil_dict = {c.name: getattr(soil_rec, c.name) for c in SoilRecord.__table__.columns if c.name not in ["id", "session_id", "created_at"]} if soil_rec else {}
        env_dict = {c.name: getattr(env_rec, c.name) for c in EnvRecord.__table__.columns if c.name not in ["id", "session_id", "created_at"]} if env_rec else {}

    # Fetch live weather context if possible
    weather_info = fetch_live_weather(
        district_name=farm_dict.get("district", "Parbhani"),
        state_name=farm_dict.get("state", "Maharashtra"),
        lat=farm_dict.get("latitude"),
        lon=farm_dict.get("longitude")
    )

    snapshot = build_farm_health_snapshot(
        farm_id=farm_id,
        farm_data=farm_dict,
        soil_data=soil_dict,
        env_data=env_dict,
        weather_info=weather_info
    )
    return snapshot


# ── 3. Canonical Advisory Generation & Retrieval ─────────────────────────────

@router.post("/farms/{farm_id}/advisories", response_model=List[AgriculturalAdvisory])
def generate_farm_advisories(farm_id: str, request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Executes the intelligence pipeline to generate canonical multi-category advisories.
    Persists advisories to DB for traceability.
    """
    farm_dict = request.farm_data.model_dump()
    soil_dict = request.soil_data.model_dump()
    env_dict = request.env_data.model_dump()

    try:
        ranked_res = get_ranked_crops(soil_dict, env_dict, farm_dict)
        ranked_crops = ranked_res.get("ranked_crops", [])
    except Exception:
        ranked_crops = []

    advisories = generate_comprehensive_advisories(
        farm_data=farm_dict,
        soil_data=soil_dict,
        env_data=env_dict,
        ranked_crops=ranked_crops
    )

    # Persist advisories
    for adv in advisories:
        adv_rec = AdvisoryRecord(
            advisory_id=adv.advisory_id,
            farm_id=farm_id,
            category=adv.category.value,
            priority=adv.priority.value,
            title=adv.title,
            recommendation=adv.recommendation,
            reasoning_json=adv.reasoning,
            supporting_observations_json=adv.supporting_observations,
            actions_json=adv.actions,
            confidence_json=adv.confidence.model_dump(),
            data_sources_json=[s.model_dump() for s in adv.data_sources],
            valid_until=adv.valid_until
        )
        db.add(adv_rec)
    try:
        db.commit()
    except Exception as err:
        db.rollback()
        print(f"Notice: Advisory persistence warning: {err}")

    return advisories


@router.get("/farms/{farm_id}/advisories")
def get_persisted_advisories(farm_id: str, db: Session = Depends(get_db)):
    """Fetch previously stored advisories for a farm."""
    records = db.query(AdvisoryRecord).filter(AdvisoryRecord.farm_id == farm_id).order_by(AdvisoryRecord.created_at.desc()).all()
    results = []
    for r in records:
        results.append({
            "advisory_id": r.advisory_id,
            "farm_id": r.farm_id,
            "category": r.category,
            "priority": r.priority,
            "title": r.title,
            "recommendation": r.recommendation,
            "reasoning": r.reasoning_json or [],
            "supporting_observations": r.supporting_observations_json or [],
            "actions": r.actions_json or [],
            "confidence": r.confidence_json or {},
            "data_sources": r.data_sources_json or [],
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return {"farm_id": farm_id, "total_advisories": len(results), "advisories": results}


# ── 4. Time-Series Farm Observations ─────────────────────────────────────────

@router.post("/farms/{farm_id}/observations", response_model=FarmObservationResponse)
def add_farm_observation(farm_id: str, obs: FarmObservationCreate, db: Session = Depends(get_db)):
    """Record an extensible biophysical or environmental observation."""
    new_obs_id = f"obs-{uuid.uuid4().hex[:8]}"
    record = FarmObservationRecord(
        observation_id=new_obs_id,
        farm_id=farm_id,
        timestamp=obs.timestamp or datetime.now(),
        observation_type=obs.observation_type.value,
        parameter_name=obs.parameter_name,
        value=obs.value,
        unit=obs.unit,
        source=obs.source,
        latitude=obs.latitude,
        longitude=obs.longitude,
        confidence=obs.confidence,
        metadata_json=obs.metadata or {}
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return FarmObservationResponse(
        observation_id=record.observation_id,
        farm_id=record.farm_id,
        timestamp=record.timestamp,
        observation_type=record.observation_type,
        parameter_name=record.parameter_name,
        value=record.value,
        unit=record.unit,
        source=record.source,
        latitude=record.latitude,
        longitude=record.longitude,
        confidence=record.confidence,
        metadata=record.metadata_json,
        created_at=record.created_at
    )


@router.get("/farms/{farm_id}/observations")
def get_farm_observations(farm_id: str, observation_type: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve time-series observations for a farm."""
    query = db.query(FarmObservationRecord).filter(FarmObservationRecord.farm_id == farm_id)
    if observation_type:
        query = query.filter(FarmObservationRecord.observation_type == observation_type.upper())

    records = query.order_by(FarmObservationRecord.timestamp.desc()).all()
    return {
        "farm_id": farm_id,
        "total_observations": len(records),
        "observations": [
            {
                "observation_id": r.observation_id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "observation_type": r.observation_type,
                "parameter_name": r.parameter_name,
                "value": r.value,
                "unit": r.unit,
                "source": r.source,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "confidence": r.confidence,
                "metadata": r.metadata_json
            }
            for r in records
        ]
    }


# ── 5. Farmer Advisory Feedback Loop ─────────────────────────────────────────

@router.post("/advisory/feedback")
def submit_advisory_feedback(feedback: AdvisoryFeedbackInput, db: Session = Depends(get_db)):
    """Record farmer adoption and real-world outcomes for an advisory."""
    rec = AdvisoryFeedbackRecord(
        advisory_id=feedback.advisory_id,
        farm_id=feedback.farm_id,
        action_taken=feedback.action_taken.value,
        outcome=feedback.outcome.value,
        notes=feedback.notes,
        created_at=feedback.timestamp or datetime.now()
    )
    db.add(rec)
    db.commit()

    return {
        "success": True,
        "feedback_id": rec.feedback_id,
        "message": "Advisory feedback recorded successfully to learning pipeline."
    }


# ── 6. Data Provenance Catalog & Coverage Matrix ─────────────────────────────

@router.get("/data-sources")
def get_registered_data_sources():
    """Returns official registry of data sources utilized across AgriN."""
    sources = [
        {
            "source_name": "Open-Meteo Real-Time Weather API",
            "source_type": "WEATHER",
            "source_url": "https://open-meteo.com",
            "coverage": "FULL",
            "resolution": "DISTRICT / POINT",
            "license": "CC BY 4.0",
            "status": "OPERATIONAL"
        },
        {
            "source_name": "Indian Regional Climatology Database (IMD Benchmarks)",
            "source_type": "GOVERNMENT",
            "source_url": "https://mausam.imd.gov.in",
            "coverage": "FULL",
            "resolution": "DISTRICT",
            "license": "Government Open Data License - India",
            "status": "OPERATIONAL"
        },
        {
            "source_name": "ICAR National Agro-Climatic Zones & Crop Requirements",
            "source_type": "AGRONOMIC_RULE",
            "source_url": "https://icar.org.in",
            "coverage": "FULL",
            "resolution": "ZONE / STATE",
            "license": "Government Open Data",
            "status": "OPERATIONAL"
        },
        {
            "source_name": "Soil Health Card (SHC) Critical Thresholds (DAC&FW)",
            "source_type": "GOVERNMENT",
            "source_url": "https://soilhealth.dac.gov.in",
            "coverage": "FULL",
            "resolution": "NATIONAL",
            "license": "Open Government Data (OGD)",
            "status": "OPERATIONAL"
        },
        {
            "source_name": "ICAR-IIFSR & CRIDA Regenerative Practices Repository",
            "source_type": "AGRONOMIC_RULE",
            "source_url": "http://crida.in",
            "coverage": "FULL",
            "resolution": "STATE / ZONE",
            "license": "Open Research",
            "status": "OPERATIONAL"
        },
        {
            "source_name": "Copernicus Sentinel-2 Multispectral Instrument (MSI)",
            "source_type": "SATELLITE",
            "source_url": "https://dataspace.copernicus.eu",
            "coverage": "UNAVAILABLE",
            "resolution": "PARCEL (10m)",
            "license": "Free, full and open Copernicus data policy",
            "status": "ARCHITECTURE_READY (Ingestion pipeline planned)"
        },
        {
            "source_name": "AgriN Plant Pathology Vision Model",
            "source_type": "ML_MODEL",
            "source_url": None,
            "coverage": "UNAVAILABLE",
            "resolution": "POINT",
            "license": "Proprietary Research",
            "status": "ARCHITECTURE_READY (Awaiting validated diagnostic model)"
        }
    ]
    return {
        "success": True,
        "total_sources": len(sources),
        "data_sources": sources
    }


@router.get("/coverage")
def get_system_coverage():
    """Returns official breakdown of geographic, agronomic, and sensor coverage."""
    return {
        "geographic_coverage": {
            "country": "India",
            "states_covered": 28,
            "union_territories_covered": 8,
            "agro_climatic_zones": 15,
            "administrative_resolution": "State -> District -> Taluka/Tehsil -> Village -> Farm Point/Parcel"
        },
        "agronomic_coverage": {
            "crops_profiled": 23,
            "soil_parameters_measured": 12,
            "regenerative_practices_cataloged": 10,
            "seasons_supported": ["Kharif", "Rabi", "Summer/Zaid", "Perennial"]
        },
        "sensor_and_intelligence_status": {
            "ground_soil_test": "OPERATIONAL",
            "real_time_weather": "OPERATIONAL",
            "crop_suitability_ml": "OPERATIONAL",
            "agronomic_rule_engine": "OPERATIONAL",
            "regenerative_recommendation": "OPERATIONAL",
            "satellite_indices": "ARCHITECTURE_READY (Not yet connected)",
            "crop_disease_vision": "ARCHITECTURE_READY (Not yet connected)",
            "brics_data_exchange": "ARCHITECTURE_READY (Standard schemas implemented)"
        }
    }


# ── 7. Unified AgriN Intelligence Orchestrator ───────────────────────────────

@router.post("/intelligence/full-analysis")
def execute_full_intelligence_analysis(payload: Dict[str, Any]):
    """
    Executes the modular end-to-end AgriN Agricultural Intelligence pipeline.
    Synthesizes Location, Soil Health, Weather, Crop Suitability, Regenerative Plan,
    Resilience Prototype, and canonical advisories.
    """
    try:
        result = run_full_agricultural_intelligence(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence pipeline error: {str(e)}")


# ── 8. Dedicated Soil Intelligence Profile Endpoint ──────────────────────────

@router.post("/soil/profile")
def get_soil_health_profile(soil_payload: Dict[str, Any]):
    """
    Evaluates raw Soil Health Card test observations against ICAR/DAC&FW standards.
    Returns status, score, limiting factors, constraints, and targeted amendments.
    """
    soil_type = soil_payload.pop("soil_type", None)
    profile = assess_soil_health(soil_payload, soil_type=soil_type)
    return {
        "success": True,
        "soil_profile": profile
    }


# ── 9. Dedicated Regenerative Advisor Endpoint ────────────────────────────────

@router.post("/regenerative/advisor")
def get_regenerative_advice(farm_payload: Dict[str, Any]):
    """
    Dedicated Regenerative Agriculture Advisor evaluating 8 practice classes
    based on soil health, moisture regime, crop sequence, and diversity.
    """
    advice = advise_regenerative_practices(
        farm_data=farm_payload,
        current_crop=farm_payload.get("crop") or farm_payload.get("target_crop")
    )
    return {
        "success": True,
        "regenerative_advice": advice
    }


# ── 10. Farm Resilience Index Prototype Endpoint ─────────────────────────────

@router.post("/resilience/score")
def get_farm_resilience_score(farm_payload: Dict[str, Any]):
    """
    Computes the transparent AgriN Farm Resilience Index — prototype,
    exposing all component scores (soil, water, climate, crop diversity, crop suitability).
    """
    resilience = calculate_farm_resilience(
        farm_data=farm_payload,
        crop_suitability_score=farm_payload.get("suitability_score")
    )
    return {
        "success": True,
        "farm_resilience": resilience
    }


# ── 11. Crop Health & Disease Diagnostic Endpoint (Honest Guardrail) ─────────

@router.post("/crop-health/diagnose")
async def diagnose_crop_disease(
    file: UploadFile = File(...),
    crop: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    farm_id: Optional[str] = Form(None)
):
    """
    Crop disease diagnostic endpoint. Validates image integrity and passes to provider interface.
    Strictly returns MODEL_NOT_DEPLOYED when trained vision weights are unlinked.
    Enforces payload size bounds and safe extension whitelist.
    """
    import os
    filename = file.filename or "leaf.jpg"
    ext = os.path.splitext(filename.lower())[1]
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image extension '{ext}'. Permitted extensions: .jpg, .jpeg, .png, .webp"
        )

    # Read with 10MB max ceiling to protect against memory exhaustion
    max_bytes = 10 * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File size exceeds maximum allowable limit of 10 MB.")
    if len(content) < 64:
        raise HTTPException(status_code=400, detail="Uploaded file is corrupt or too small (< 64 bytes).")

    result = diagnose_crop_image(
        image_bytes=content,
        filename=filename,
        crop=crop,
        symptoms_description=symptoms,
        farm_id=farm_id
    )
    return result


# ── 12. Satellite Observation Query Endpoint (GET) ───────────────────────────

@router.get("/satellite/observation")
def get_satellite_observation_query(
    latitude: float,
    longitude: float,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    allow_demo: bool = False
):
    """
    Normalized Earth Observation query via GET query parameters.
    Returns normalized contract with status = NOT_CONNECTED when provider is offline.
    """
    obs = get_satellite_observation(latitude=latitude, longitude=longitude, start_date=start_date, end_date=end_date, allow_demo=allow_demo)
    return obs



# ── 13. National Agricultural Intelligence Overview ──────────────────────────

@router.get("/national/overview")
def get_national_agricultural_overview():
    """
    Pan-India overview aggregating 15 National Agro-Climatic Zones,
    soil distributions, and key regional cropping patterns without exposing farmer PII.
    """
    zones = get_all_agro_climatic_zones()
    states = get_all_states()
    return {
        "country": "India",
        "total_states_and_uts": len(states),
        "total_agro_climatic_zones": len(zones),
        "agro_climatic_zones": zones,
        "sample_coverage": {
            "arid_zone": "Western Dry Region (Rajasthan) — Bajra, Mothbeans, Mustard",
            "gangetic_plains": "Middle/Upper Gangetic Plain — Rice, Wheat, Sugarcane",
            "black_soil_plateau": "Western/Central Plateau (Maharashtra/MP) — Cotton, Soybean, Pulses",
            "coastal_plains": "East/West Coast Plains & Ghats (Kerala, TN) — Coconut, Rice, Spices"
        },
        "data_license": "Government Open Data License - India"
    }


# ── 14. Interoperability & Country Adapters Registry ─────────────────────────

@router.get("/interoperability/adapters")
def list_interoperability_adapters():
    """
    Lists registered country adapters for the AgriN Data Exchange (ADE).
    Highlights India as reference implementation, with BRICS partner interfaces.
    """
    adapters_info = []
    for iso, adapter in ADAPTER_REGISTRY.items():
        adapters_info.append({
            "country_iso3": adapter.country_iso3,
            "country_name": adapter.country_name,
            "is_reference_implementation": adapter.is_reference_implementation,
            "supported_zones": adapter.get_supported_agro_zones()
        })

    return {
        "standard": "AgriN Data Exchange (ADE) v1.0.0",
        "units": "SI (mg/kg, mm, ha, degC)",
        "spatial_crs": "WGS84 (EPSG:4326)",
        "adapters": adapters_info
    }


# ── 15. Longitudinal Farm History & Empirical Trends (Phase 11) ─────────────

@router.get("/farms/{farm_id}/history")
def get_farm_longitudinal_history(farm_id: str, db: Session = Depends(get_db)):
    """
    Retrieves repeated farm soil tests, environmental readings, prediction records,
    and calculates empirical trends (SOC, pH, EC, N, P, K, resilience) only when
    at least 2 real historical observations exist. Never manufactures synthetic trends.
    """
    soil_records = db.query(SoilRecord).filter(SoilRecord.session_id == farm_id).order_by(SoilRecord.created_at.asc()).all()
    pred_records = db.query(PredictionRecord).filter(PredictionRecord.session_id == farm_id).order_by(PredictionRecord.created_at.asc()).all()
    feedback_records = db.query(FeedbackRecord).filter(FeedbackRecord.session_id == farm_id).order_by(FeedbackRecord.created_at.asc()).all()

    total_records = len(soil_records)

    history_snapshots = []
    for idx, s in enumerate(soil_records):
        p = pred_records[idx] if idx < len(pred_records) else None
        history_snapshots.append({
            "observation_index": idx + 1,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "soil": {
                "OC": s.OC, "pH": s.ph, "EC": s.EC,
                "N": s.N, "P": s.P, "K": s.K,
                "Zn": s.Zn, "Fe": s.Fe, "B": s.B
            },
            "top_crop": p.top_crop if p else None,
            "suitability_score": p.top_score if p else None,
            "data_confidence": p.data_confidence if p else None
        })

    if total_records < 2:
        return {
            "success": True,
            "farm_id": farm_id,
            "has_sufficient_history": False,
            "observation_count": total_records,
            "message": "At least 2 longitudinal soil observations are required to compute trends without synthetic interpolation.",
            "history": history_snapshots,
            "trends": None,
            "feedback_history": [
                {
                    "recommended_crop": fb.recommended_crop,
                    "rating": fb.rating,
                    "notes": fb.free_text,
                    "created_at": fb.created_at.isoformat() if fb.created_at else None
                } for fb in feedback_records
            ]
        }

    # Calculate Empirical Multi-Observation Trends (Phase 11)
    s_first, s_last = soil_records[0], soil_records[-1]

    def _trend(val_start, val_end, unit=""):
        if val_start is None or val_end is None:
            return None
        delta = round(val_end - val_start, 2)
        direction = "STABLE"
        if delta > 0.05:
            direction = "INCREASING"
        elif delta < -0.05:
            direction = "DECREASING"
        return {
            "initial": val_start,
            "latest": val_end,
            "delta": delta,
            "direction": direction,
            "unit": unit
        }

    trends = {
        "organic_carbon": _trend(s_first.OC, s_last.OC, "%"),
        "soil_ph": _trend(s_first.ph, s_last.ph, "pH units"),
        "electrical_conductivity": _trend(s_first.EC, s_last.EC, "dS/m"),
        "nitrogen": _trend(s_first.N, s_last.N, "kg/ha"),
        "phosphorus": _trend(s_first.P, s_last.P, "kg/ha"),
        "potassium": _trend(s_first.K, s_last.K, "kg/ha"),
        "resilience_suitability": _trend(
            pred_records[0].top_score if pred_records else None,
            pred_records[-1].top_score if pred_records else None,
            "pts"
        )
    }

    return {
        "success": True,
        "farm_id": farm_id,
        "has_sufficient_history": True,
        "observation_count": total_records,
        "history": history_snapshots,
        "trends": trends,
        "feedback_history": [
            {
                "recommended_crop": fb.recommended_crop,
                "rating": fb.rating,
                "notes": fb.free_text,
                "created_at": fb.created_at.isoformat() if fb.created_at else None
            } for fb in feedback_records
        ]
    }


# ── 16. Multi-Crop Comparison & Trade-Off Evaluation (Phase 3 Requirement 7 & 8) ──

@router.post("/crops/compare")
def compare_candidate_crops(payload: Dict[str, Any]):
    """
    Evaluates 2 to 4 candidate crops side-by-side across:
    - Soil compatibility
    - Climate fit
    - Water requirement & fit
    - Season fit
    - Biophysical risks & limitations
    - Pairwise trade-off narratives (e.g. Higher water vs better soil fit)
    """
    candidate_crops = payload.get("candidate_crops") or payload.get("crops", [])
    if not candidate_crops or len(candidate_crops) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 candidate crops for comparison (maximum 4).")
    if len(candidate_crops) > 4:
        candidate_crops = candidate_crops[:4]

    farm_data = payload.get("farm_data") or payload.get("location", {})
    soil_data = payload.get("soil_data") or payload.get("soil", {})
    env_data = payload.get("env_data") or payload.get("weather")

    res = compare_crops(
        candidate_crops=candidate_crops,
        farm_data=farm_data,
        soil_data=soil_data,
        env_data=env_data
    )
    return res


# ── 17. Centralized Knowledge Sources Registry (Phase 3 Requirement 18) ────────

@router.get("/knowledge/sources")
def get_knowledge_sources_registry():
    """Returns the centralized registry of authoritative agronomic and climate data sources."""
    import json
    from pathlib import Path
    sources_path = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "knowledge_sources.json"
    if sources_path.exists():
        with open(sources_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sources": [], "error": "knowledge_sources.json not found"}


# ── 18. Externalized Regenerative Practice Knowledge Base (Phase 3 Requirement 16) ─

@router.get("/knowledge/regenerative-practices")
def get_regenerative_practices_kb():
    """Returns the structured regenerative practices knowledge base with target conditions, objectives, and evidence levels."""
    import json
    from pathlib import Path
    kb_path = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "regenerative_practices.json"
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"practices": [], "error": "regenerative_practices.json not found"}


# ── 19. Realistic Synthetic Demo Farms (Phase 3 Requirement 23) ──────────────────

@router.get("/demo/farms")
def get_demo_farms():
    """
    Returns realistic demonstration farms covering key Indian agro-climatic archetypes.
    Every record is explicitly marked 'synthetic: true' with documented agronomic rationale.
    """
    import json
    from pathlib import Path
    demo_path = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "demo_farms.json"
    if demo_path.exists():
        with open(demo_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"demo_farms": [], "error": "demo_farms.json not found"}


# ── 20. Satellite Provider Status & Observation (Phase 4 Requirements 2 & 3) ────

@router.get("/satellite/status")
def get_satellite_status(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    farm_id: Optional[str] = None,
    allow_demo: bool = False
):
    """Returns real-time connectivity status of Earth Observation satellite providers."""
    return get_satellite_status_report(latitude=latitude, longitude=longitude, farm_id=farm_id, allow_demo=allow_demo)


@router.post("/satellite/observation")
def get_satellite_observation_endpoint(payload: Dict[str, Any]):
    """Retrieves standard normalized observation from active satellite provider."""
    lat = float(payload.get("latitude", 19.26))
    lon = float(payload.get("longitude", 76.77))
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    allow_demo = bool(payload.get("allow_demo", False))
    return get_satellite_observation(lat, lon, start_date=start_date, end_date=end_date, allow_demo=allow_demo)


@router.post("/satellite/time-series")
def get_satellite_time_series_endpoint(payload: Dict[str, Any]):
    """Analyzes chronological satellite time series: NDVI(t1), NDVI(t2), NDVI(t3)."""
    observations = payload.get("observations", [])
    if not observations:
        lat = float(payload.get("latitude", 19.26))
        lon = float(payload.get("longitude", 76.77))
        allow_demo = bool(payload.get("allow_demo", False))
        prov = get_satellite_provider(allow_demo=allow_demo)
        observations = prov.fetch_time_series(lat, lon, farm_id=payload.get("farm_id"))
    return analyze_satellite_time_series(observations)


# ── 21. Crop Disease Diagnostics & Triage (Phase 4 Requirements 7-10 & 25) ─────

@router.post("/disease/diagnose")
async def diagnose_leaf_image(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    farm_id: Optional[str] = Form(None),
    allow_demo: bool = Form(False)
):
    """
    Diagnostic endpoint with strict file validation, magic byte checks,
    local model triage, and IPM cultural management advisories.
    """
    file_bytes = await file.read()
    return diagnose_crop_image(
        image_bytes=file_bytes,
        filename=file.filename or "leaf.jpg",
        crop=crop_hint,
        symptoms_description=symptoms,
        farm_id=farm_id,
        allow_demo=allow_demo
    )


# ── 22. Agricultural Knowledge Graph Query (Phase 4 Requirement 16 & 17) ──────

@router.get("/knowledge/graph/crop/{crop_name}")
def get_crop_graph_relationships(crop_name: str):
    """Queries lightweight relationship graph for crop biophysical links, risks, and practices."""
    return knowledge_graph.get_crop_relationships(crop_name)


# ── 23. BRICS Interoperability Simulation (Phase 4 Requirements 11 & 15) ────────

@router.post("/brics/simulate")
def simulate_brics_interoperability(payload: Dict[str, Any]):
    """
    Executes a deterministic interoperability test for IND, BRA, ZAF, RUS, CHN.
    Validates, normalizes localized units to AgriN Common Schema, and runs intelligence.
    """
    country_code = payload.get("country_code", "BRA")
    raw_data = payload.get("raw_payload", payload)
    return run_brics_interoperability_simulation(country_code, raw_data)




