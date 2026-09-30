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
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.db import (
    get_db, FarmerSession, SoilRecord, EnvRecord, PredictionRecord,
    FarmObservationRecord, AdvisoryRecord, AdvisoryFeedbackRecord
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
