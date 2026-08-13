"""FarmFriend AI — What-If Routes"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.database.db import get_db, WhatIfRecord
from backend.app.models.schemas import WhatIfRequest, WhatIfResponse
from backend.app.services.what_if import run_whatif

router = APIRouter()


@router.post("/whatif", response_model=WhatIfResponse)
def what_if_simulation(request: WhatIfRequest, db: Session = Depends(get_db)):
    """Run a what-if simulation with modified inputs."""
    result = run_whatif(
        crop_name=request.crop_name,
        original_soil=request.original_soil.model_dump(),
        original_env=request.original_env.model_dump(),
        farm_data=request.farm_data.model_dump(),
        simulated_changes=request.simulated_changes
    )

    if result.get("error"):
        raise HTTPException(
            status_code=422,
            detail=result.get("validation_errors", "Invalid simulation inputs")
        )

    # Persist whatif record to DB
    try:
        whatif_rec = WhatIfRecord(
            session_id=request.session_id,
            crop_name=request.crop_name,
            before_score=result.get("before", {}).get("score", 0.0),
            after_score=result.get("after", {}).get("score", 0.0),
            score_change=result.get("score_change", 0.0),
            changed_params_json=result.get("changed_params", {}),
        )
        db.add(whatif_rec)
        db.commit()
    except Exception as db_err:
        db.rollback()
        print(f"Warning: Failed to persist what-if simulation to DB: {db_err}")

    return WhatIfResponse(
        success=True,
        is_simulation=True,
        crop=result["crop"],
        before=result["before"],
        after=result["after"],
        changed_params=result["changed_params"],
        score_change=result["score_change"],
        score_change_direction=result["score_change_direction"],
        explanation=result["explanation"],
        disclaimer=result["disclaimer"]
    )

