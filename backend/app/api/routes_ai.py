"""FarmFriend AI — AI Explanation Routes (Rule-Based NLG)"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import ExplainRequest, ExplainQARequest
from backend.app.services.nlg_explainer import (
    explain_crop_detail, explain_top_recommendations, explain_feasibility,
    generate_summary_card, answer_why_recommended, answer_why_lower, answer_what_if_hint
)

router = APIRouter()


@router.post("/explain")
def explain(request: ExplainRequest):
    """
    Generate a natural-language explanation using the rule-based NLG engine.
    No external LLM API is called. Explanations are grounded in actual model results.
    """
    crop_result = request.crop_result
    explanation_type = request.explanation_type

    if explanation_type == "crop_detail":
        text = explain_crop_detail(crop_result)
    elif explanation_type == "feasibility":
        chosen = crop_result.get("crop", "")
        text = explain_feasibility(crop_result, chosen)
    elif explanation_type == "summary_card":
        card = generate_summary_card(crop_result)
        return {"success": True, "explanation_type": explanation_type,
                "summary_card": card, "engine": "rule_based_nlg"}
    else:
        text = explain_crop_detail(crop_result)

    return {
        "success": True,
        "explanation_type": explanation_type,
        "explanation": text,
        "engine": "rule_based_nlg",
        "disclaimer": (
            "Explanation generated from analytical model results. "
            "No external AI API was used. "
            "This is a decision-support tool — not a replacement for professional agricultural advice."
        )
    }


@router.post("/explain/qa")
def explain_qa(request: ExplainQARequest):
    """Answer specific farmer questions about the analysis."""
    question_type = request.question_type
    crop_result = request.crop_result
    context = request.context or {}

    if question_type == "why_recommended":
        rank = context.get("rank", 1)
        text = answer_why_recommended(crop_result, rank)
    elif question_type == "why_lower":
        better_result = context.get("better_crop_result", {})
        text = answer_why_lower(crop_result, better_result)
    elif question_type == "whatif_hint":
        limiting = crop_result.get("limiting_factors", [])
        text = answer_what_if_hint(crop_result.get("crop", ""), limiting)
    else:
        text = explain_crop_detail(crop_result)

    return {
        "success": True,
        "question_type": question_type,
        "answer": text,
        "engine": "rule_based_nlg"
    }



@router.get("/model-info")
def model_info():
    """Return ML model information."""
    try:
        from ml.predict import predictor
        predictor.load()
        return {"success": True, "model_info": predictor.get_model_info(),
                "feature_importance": predictor.get_feature_importance()}
    except FileNotFoundError:
        return {"success": False, "message": "Model not yet trained."}
