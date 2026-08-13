"""FarmFriend AI — Analytics Dashboard Routes"""

import json, os
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
def get_reference_data():
    """Return knowledge base reference data for frontend dropdowns."""
    try:
        mh_path = os.path.join(BASE_DIR, "knowledge", "maharashtra_data.json")
        with open(mh_path) as f:
            mh_data = json.load(f)
        return {
            "districts": mh_data.get("districts", []),
            "seasons": mh_data.get("seasons", []),
            "soil_types": mh_data.get("soil_types_ui", []),
            "water_sources": mh_data.get("water_sources", []),
            "drainage_conditions": mh_data.get("drainage_conditions", []),
            "previous_crops": mh_data.get("previous_crops", [])
        }
    except Exception as e:
        return {"error": str(e)}
