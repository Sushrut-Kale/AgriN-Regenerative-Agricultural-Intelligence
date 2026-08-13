"""FarmFriend AI — Farm & Validation Routes"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.db import (
    get_db, FarmerSession, SoilRecord, EnvRecord, PredictionRecord
)
from backend.app.models.schemas import (
    AnalysisRequest, AnalysisResponse, ValidationResponse
)
from backend.app.services.validation import (
    validate_farm_inputs, validate_soil_inputs, validate_env_inputs,
    compute_data_confidence
)
from backend.app.services.crop_prediction import get_ranked_crops
from backend.app.services.nlg_explainer import explain_top_recommendations
from backend.app.services.weather_service import fetch_live_weather

router = APIRouter()


@router.get("/weather")
def get_live_weather_for_district(district: str = "Parbhani"):
    """Fetch real-time current weather parameters for a given district."""
    return fetch_live_weather(district)



@router.post("/validate", response_model=ValidationResponse)
def validate_inputs(request: AnalysisRequest):
    """Validate all farmer inputs and return errors/warnings."""
    farm_v = validate_farm_inputs(request.farm_data.model_dump())
    soil_v = validate_soil_inputs(request.soil_data.model_dump())
    env_v = validate_env_inputs(request.env_data.model_dump())

    all_errors = farm_v.errors + soil_v.errors + env_v.errors
    all_warnings = farm_v.warnings + soil_v.warnings + env_v.warnings

    return ValidationResponse(
        is_valid=len(all_errors) == 0,
        errors=[e.to_dict() for e in all_errors],
        warnings=[w.to_dict() for w in all_warnings]
    )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Full analysis pipeline: validate → ML predict → rule scoring → ranked crops.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Validate
    farm_v = validate_farm_inputs(request.farm_data.model_dump())
    soil_v = validate_soil_inputs(request.soil_data.model_dump())
    env_v = validate_env_inputs(request.env_data.model_dump())

    errors = farm_v.errors + soil_v.errors + env_v.errors
    if errors:
        raise HTTPException(
            status_code=422,
            detail={"message": "Validation failed", "errors": [e.to_dict() for e in errors]}
        )

    soil_dict = request.soil_data.model_dump()
    env_dict = request.env_data.model_dump()
    farm_dict = request.farm_data.model_dump()

    try:
        result = get_ranked_crops(soil_dict, env_dict, farm_dict)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ML model not found. Please train the model first: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # NLG explanation for top recommendations
    explanation = explain_top_recommendations(
        result["ranked_crops"], farm_dict, soil_dict
    )

    # Persist to database
    try:
        # Farmer Session
        existing_sess = db.query(FarmerSession).filter(FarmerSession.session_id == session_id).first()
        if not existing_sess:
            farmer_sess = FarmerSession(
                session_id=session_id,
                state=farm_dict.get("state", "Maharashtra"),
                district=farm_dict.get("district"),
                season=farm_dict.get("season"),
            )
            db.add(farmer_sess)
            db.commit()

        # Soil Record
        soil_rec = SoilRecord(
            session_id=session_id,
            N=soil_dict.get("N"), P=soil_dict.get("P"), K=soil_dict.get("K"),
            S=soil_dict.get("S"), Zn=soil_dict.get("Zn"), Fe=soil_dict.get("Fe"),
            Cu=soil_dict.get("Cu"), Mn=soil_dict.get("Mn"), B=soil_dict.get("B"),
            ph=soil_dict.get("ph"), EC=soil_dict.get("EC"), OC=soil_dict.get("OC"),
            soil_type=farm_dict.get("soil_type"),
        )
        db.add(soil_rec)

        # Env Record
        env_rec = EnvRecord(
            session_id=session_id,
            temperature=env_dict.get("temperature"),
            humidity=env_dict.get("humidity"),
            rainfall=env_dict.get("rainfall"),
        )
        db.add(env_rec)

        # Prediction Record
        top_crop = result["ranked_crops"][0] if result.get("ranked_crops") else {}
        pred_rec = PredictionRecord(
            session_id=session_id,
            model_version=result.get("model_info", {}).get("model_version", "random_forest_v1"),
            top_crop=top_crop.get("crop", "Unknown"),
            top_score=top_crop.get("final_score", 0.0),
            ranked_crops_json=[c for c in result.get("ranked_crops", [])],
            data_confidence=top_crop.get("data_confidence", "medium"),
        )
        db.add(pred_rec)
        db.commit()
    except Exception as db_err:
        db.rollback()
        # Log error silently so API response still succeeds
        print(f"Warning: Failed to persist analysis to DB: {db_err}")

    return AnalysisResponse(
        success=True,
        session_id=session_id,
        ranked_crops=result["ranked_crops"],
        model_info=result["model_info"],
        feature_importance=result["feature_importance"],
        data_completeness=result["data_completeness"],
        recommendation_explanation=explanation
    )

