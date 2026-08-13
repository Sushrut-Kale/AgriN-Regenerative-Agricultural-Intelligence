"""
FarmFriend AI — Closed-Loop Feedback Routes
==============================================

Handles farmer recommendation feedback, harvest outcome logging,
and analytics aggregation. Ensures zero immediate model auto-retraining
to prevent feedback poisoning.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database.db import get_db, FeedbackRecord
from backend.app.models.schemas import FeedbackInput, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackInput, db: Session = Depends(get_db)):
    """
    Store farmer feedback and crop outcomes.
    No automatic retraining occurs — feedback is queued for expert data quality review.
    """
    try:
        feedback_id = str(uuid.uuid4())
        rec = FeedbackRecord(
            feedback_id=feedback_id,
            session_id=request.session_id,
            analysis_id=request.analysis_id,
            recommended_crop=request.recommended_crop,
            selected_crop=request.selected_crop or request.recommended_crop,
            suitability_score=request.suitability_score,
            rating=request.rating,
            reason=request.reason,
            free_text=request.free_text,
            outcome_status=request.outcome_status or "not_yet_grown",
            crop_performance=request.crop_performance,
            actual_yield=request.actual_yield,
            yield_unit=request.yield_unit or "quintals_per_ha",
            model_version=request.model_version or "random_forest_v2",
            region=request.region,
            season=request.season,
        )
        db.add(rec)
        db.commit()
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Thank you! Your feedback has been recorded securely."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.get("/feedback/summary")
def get_feedback_summary(db: Session = Depends(get_db)):
    """Return technical dashboard feedback analytics."""
    try:
        total = db.query(FeedbackRecord).count()
        helpful = db.query(FeedbackRecord).filter(FeedbackRecord.rating == "helpful").count()
        not_helpful = db.query(FeedbackRecord).filter(FeedbackRecord.rating == "not_helpful").count()
        partially = db.query(FeedbackRecord).filter(FeedbackRecord.rating == "partially").count()

        harvested_count = db.query(FeedbackRecord).filter(FeedbackRecord.outcome_status == "harvested").count()

        helpful_pct = round((helpful / total * 100), 1) if total > 0 else 0.0

        # Most disputed crops
        disputed = (
            db.query(FeedbackRecord.recommended_crop, func.count(FeedbackRecord.id).label("count"))
            .filter(FeedbackRecord.rating == "not_helpful")
            .group_by(FeedbackRecord.recommended_crop)
            .order_by(func.count(FeedbackRecord.id).desc())
            .limit(5)
            .all()
        )

        return {
            "success": True,
            "total_feedback": total,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful,
            "partially_helpful_count": partially,
            "helpful_percentage": helpful_pct,
            "harvested_outcomes_logged": harvested_count,
            "top_disputed_crops": [{"crop": c, "disputes": cnt} for c, cnt in disputed]
        }
    except Exception as e:
        return {"success": False, "message": f"Feedback summary unavailable: {str(e)}"}
