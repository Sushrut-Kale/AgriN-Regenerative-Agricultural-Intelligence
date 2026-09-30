"""FarmFriend AI — Analytics Dashboard Routes"""

import json, os
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from backend.app.database.db import get_db, PredictionRecord, FeasibilityRecord, WhatIfRecord

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Return analytics data for the dashboard."""

    # Counts
    total_analyses = db.query(func.count(PredictionRecord.id)).scalar() or 0
    total_feasibility = db.query(func.count(FeasibilityRecord.id)).scalar() or 0
    total_whatif = db.query(func.count(WhatIfRecord.id)).scalar() or 0

    # Top recommended crops
    top_rec_raw = (
        db.query(PredictionRecord.top_crop, func.count().label("count"))
        .group_by(PredictionRecord.top_crop)
        .order_by(text("count DESC"))
        .limit(10)
        .all()
    )
    top_recommended = [{"crop": r[0], "count": r[1]} for r in top_rec_raw]

    # Top chosen crops (feasibility)
    top_chosen_raw = (
        db.query(FeasibilityRecord.chosen_crop, func.count().label("count"))
        .group_by(FeasibilityRecord.chosen_crop)
        .order_by(text("count DESC"))
        .limit(10)
        .all()
    )
    top_chosen = [{"crop": r[0], "count": r[1]} for r in top_chosen_raw]

    # Score distribution
    score_buckets = {"0-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    scores = db.query(PredictionRecord.top_score).all()
    for (s,) in scores:
        if s is not None:
            if s < 40: score_buckets["0-40"] += 1
            elif s < 60: score_buckets["40-60"] += 1
            elif s < 80: score_buckets["60-80"] += 1
            else: score_buckets["80-100"] += 1

    # Model info
    model_info = {}
    try:
        from ml.predict import predictor
        predictor.load()
        model_info = predictor.get_model_info()
    except Exception:
        pass

    return {
        "total_analyses": total_analyses,
        "total_feasibility_checks": total_feasibility,
        "total_whatif_runs": total_whatif,
        "top_recommended_crops": top_recommended,
        "top_chosen_crops": top_chosen,
        "score_distribution": score_buckets,
        "district_distribution": [],
        "season_distribution": [],
        "model_info": model_info,
        "missing_data_stats": {}
    }


@router.get("/reference-data")
def get_reference_data(state: Optional[str] = None):
    """Return knowledge base reference data for frontend dropdowns across India."""
    try:
        from backend.app.services.geo_service import get_all_states, get_districts_for_state
        target_state = state or "Maharashtra"
        all_states = get_all_states()
        districts = get_districts_for_state(target_state)

        # Fallback seasons & soil types from MH data or generic standard
        mh_path = os.path.join(BASE_DIR, "knowledge", "maharashtra_data.json")
        seasons = [
            {"id": "kharif", "name": "Kharif", "period": "June – October (Monsoon)"},
            {"id": "rabi", "name": "Rabi", "period": "October – March (Winter)"},
            {"id": "summer", "name": "Summer (Zaid)", "period": "March – June"},
            {"id": "perennial", "name": "Perennial", "period": "Year-round (Orchards/Plantations)"}
        ]
        soil_types = [
            {"id": "black", "name": "Black Soil (Vertisol / Regur)", "desc": "High clay, moisture retentive, excellent for cotton and soybean"},
            {"id": "alluvial", "name": "Alluvial Soil", "desc": "Fertile loam/sandy loam formed by river plains"},
            {"id": "red", "name": "Red & Yellow Soil", "desc": "Porous, rich in iron, responsive to irrigation"},
            {"id": "laterite", "name": "Laterite Soil", "desc": "Acidic, porous, typical of high-rainfall coastal/ghat regions"},
            {"id": "sandy_loam", "name": "Sandy Loam", "desc": "Light, well-drained, ideal for horticulture and vegetables"},
            {"id": "clay_loam", "name": "Clay Loam", "desc": "Balanced texture, good water and nutrient retention"},
            {"id": "sandy", "name": "Sandy / Desert Soil", "desc": "Low water retention, suited for arid pulses like mothbeans"},
            {"id": "unknown", "name": "Not Sure / Mixed", "desc": "General agricultural analysis"}
        ]
        water_sources = [
            {"id": "canal", "name": "Canal"},
            {"id": "borewell", "name": "Borewell / Tube well"},
            {"id": "open_well", "name": "Open Well"},
            {"id": "farm_pond", "name": "Farm Pond / Check Dam"},
            {"id": "river_lift", "name": "River / Stream Lift"},
            {"id": "rainfed_only", "name": "Rainfed Only (No irrigation source)"}
        ]
        drainage_conditions = [
            {"id": "good", "name": "Good (No waterlogging, water drains within 24h)"},
            {"id": "moderate", "name": "Moderate (Temporary pooling after heavy rain)"},
            {"id": "poor", "name": "Poor (Prone to waterlogging / high clay subsoil)"},
            {"id": "unknown", "name": "Unknown"}
        ]
        previous_crops = [
            {"id": "none", "name": "Fallow / None"},
            {"id": "cotton", "name": "Cotton"},
            {"id": "soybean", "name": "Soybean"},
            {"id": "pigeonpeas", "name": "Pigeonpeas (Tur)"},
            {"id": "chickpea", "name": "Chickpea (Gram)"},
            {"id": "wheat", "name": "Wheat"},
            {"id": "rice", "name": "Rice (Paddy)"},
            {"id": "maize", "name": "Maize"},
            {"id": "vegetables", "name": "Vegetables"},
            {"id": "sugarcane", "name": "Sugarcane"},
            {"id": "other", "name": "Other"}
        ]

        if os.path.exists(mh_path):
            with open(mh_path) as f:
                mh_data = json.load(f)
                if mh_data.get("seasons"): seasons = mh_data["seasons"]
                if mh_data.get("soil_types_ui"): soil_types = mh_data["soil_types_ui"]
                if mh_data.get("water_sources"): water_sources = mh_data["water_sources"]
                if mh_data.get("drainage_conditions"): drainage_conditions = mh_data["drainage_conditions"]
                if mh_data.get("previous_crops"): previous_crops = mh_data["previous_crops"]

        return {
            "country": "India",
            "selected_state": target_state,
            "states": all_states,
            "districts": districts,
            "seasons": seasons,
            "soil_types": soil_types,
            "water_sources": water_sources,
            "drainage_conditions": drainage_conditions,
            "previous_crops": previous_crops
        }
    except Exception as e:
        return {"error": str(e)}
