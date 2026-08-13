"""FarmFriend AI — Crop Prediction Routes"""

import json, os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.db import get_db, FeasibilityRecord
from backend.app.services.feasibility import analyze_farmer_chosen_crop
from backend.app.models.schemas import FeasibilityRequest, FeasibilityResponse

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

@router.get("/crops")
def list_crops():
    """List all supported crops with basic metadata."""
    knowledge_path = os.path.join(BASE_DIR, "knowledge", "crop_requirements.json")
    with open(knowledge_path) as f:
        data = json.load(f)
    crops = []
    for key, val in data["crops"].items():
        crops.append({
            "id": key,
            "common_name": val.get("common_name", key.title()),
            "local_name": val.get("local_name", ""),
            "category": val.get("category", ""),
            "maharashtra_suitability": val.get("maharashtra_suitability", "unknown"),
            "seasons": val.get("seasons", {}).get("maharashtra", [])
        })
    return {"crops": crops, "total": len(crops)}


@router.post("/feasibility", response_model=FeasibilityResponse)
def check_feasibility(request: FeasibilityRequest, db: Session = Depends(get_db)):
    """Run 'I Want to Grow This' feasibility analysis."""
    result = analyze_farmer_chosen_crop(
        chosen_crop=request.chosen_crop,
        soil_data=request.soil_data.model_dump(),
        env_data=request.env_data.model_dump(),
        farm_data=request.farm_data.model_dump()
    )

    # Persist feasibility record to DB
    try:
        feasibility_rec = FeasibilityRecord(
            session_id=request.session_id,
            chosen_crop=request.chosen_crop,
            suitability_score=result.get("final_score", 0.0),
            feasibility_outcome=result.get("feasibility_outcome", "unknown"),
            result_json=result,
        )
        db.add(feasibility_rec)
        db.commit()
    except Exception as db_err:
        db.rollback()
        print(f"Warning: Failed to persist feasibility to DB: {db_err}")

    return FeasibilityResponse(
        success=True,
        session_id=request.session_id,
        crop=request.chosen_crop,
        result=result,
        feasibility_explanation=result.get("feasibility_explanation", ""),
        summary_card=result.get("summary_card", {}),
        feasibility_outcome=result.get("feasibility_outcome", "unknown"),
        feasibility_label=result.get("feasibility_label", ""),
        feasibility_color=result.get("feasibility_color", "gray")
    )

