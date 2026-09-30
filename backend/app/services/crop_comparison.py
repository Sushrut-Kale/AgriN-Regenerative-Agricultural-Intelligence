"""
AgriN Multi-Crop Comparative Analysis & Trade-Off Engine
=========================================================
Compares 2 to 4 candidate crops under identical farm, soil, and weather conditions.
Extracts multi-vector biophysical fits without picking an arbitrary 'winner'.
Synthesizes honest, transparent agronomic trade-off explanations.
"""

from typing import Dict, Any, List, Optional
try:
    from backend.app.services.suitability_scorer import compute_detailed_suitability
except ImportError:
    from app.services.suitability_scorer import compute_detailed_suitability


def compare_candidate_crops(
    candidate_crops: List[str],
    farm_data: Dict[str, Any],
    soil_data: Optional[Dict[str, Any]] = None,
    env_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compares 2 to 4 candidate crops against a farm profile.

    Returns:
    - crop_evaluations: List of rich evaluations with sub-compatibilities
    - comparison_matrix: Side-by-side comparison across 5 dimensions
    - trade_offs: Explicit pairwise trade-off analysis and agronomic decision context
    """
    if not candidate_crops:
        return {"error": "At least 2 candidate crops required for comparison."}

    selected_crops = candidate_crops[:4]  # Max 4 crops
    crop_evaluations = []

    s_dict = soil_data or {}
    e_dict = env_data or {}
    f_dict = farm_data or {}

    for crop in selected_crops:
        eval_res = compute_detailed_suitability(
            crop_name=crop,
            farm_data=f_dict,
            soil_data=s_dict,
            env_data=e_dict
        )
        crop_evaluations.append(eval_res)

    # Build side-by-side matrix
    comparison_matrix = {
        "crops": [c["crop_name"] for c in crop_evaluations],
        "overall_scores": {c["crop_name"]: c["overall_score"] for c in crop_evaluations},
        "soil_compatibility": {c["crop_name"]: c["soil_compatibility"] for c in crop_evaluations},
        "weather_compatibility": {c["crop_name"]: c["weather_compatibility"] for c in crop_evaluations},
        "season_compatibility": {c["crop_name"]: c["season_compatibility"] for c in crop_evaluations},
        "water_compatibility": {c["crop_name"]: c["water_compatibility"] for c in crop_evaluations},
        "location_compatibility": {c["crop_name"]: c["location_compatibility"] for c in crop_evaluations},
        "confidences": {c["crop_name"]: c["confidence"] for c in crop_evaluations}
    }

    # Generate Trade-off Narratives (Step 8)
    trade_off_notes = []
    decision_contexts = []

    if len(crop_evaluations) >= 2:
        for i in range(len(crop_evaluations)):
            for j in range(i + 1, len(crop_evaluations)):
                cA = crop_evaluations[i]
                cB = crop_evaluations[j]
                nameA = cA["crop_name"]
                nameB = cB["crop_name"]

                diffs = []
                # Compare soil
                if abs(cA["soil_compatibility"] - cB["soil_compatibility"]) >= 8.0:
                    better = nameA if cA["soil_compatibility"] > cB["soil_compatibility"] else nameB
                    diffs.append(f"{better} has superior soil compatibility ({max(cA['soil_compatibility'], cB['soil_compatibility'])}% vs {min(cA['soil_compatibility'], cB['soil_compatibility'])}%)")

                # Compare water
                if abs(cA["water_compatibility"] - cB["water_compatibility"]) >= 8.0:
                    better = nameA if cA["water_compatibility"] > cB["water_compatibility"] else nameB
                    diffs.append(f"{better} has better water fit for the current irrigation regime")

                # Compare weather/climate
                if abs(cA["weather_compatibility"] - cB["weather_compatibility"]) >= 8.0:
                    better = nameA if cA["weather_compatibility"] > cB["weather_compatibility"] else nameB
                    diffs.append(f"{better} is better adapted to current thermal and hygrometric conditions")

                if diffs:
                    trade_off_notes.append(f"Between {nameA} and {nameB}: " + "; ".join(diffs) + ".")
                else:
                    trade_off_notes.append(f"{nameA} and {nameB} show balanced biophysical profiles under current field conditions.")

        # Overall synthesis
        irrigation_avail = str(farm_data.get("irrigation_available", "no")).lower() in ["yes", "true", "irrigated"]
        if not irrigation_avail:
            decision_contexts.append(
                "Under rainfed conditions, prioritizing crops with higher water-compatibility and drought tolerance "
                "reduces downside risk during monsoon dry spells, even if another crop offers a marginally higher theoretical soil score."
            )
        else:
            decision_contexts.append(
                "With assured irrigation, the farmer can afford to prioritize crops with higher soil suitability "
                "and economic value, as moisture deficit risks are mitigated."
            )

    return {
        "status": "success",
        "total_compared": len(crop_evaluations),
        "crop_evaluations": crop_evaluations,
        "comparison_matrix": comparison_matrix,
        "trade_off_analysis": {
            "pairwise_trade_offs": trade_off_notes,
            "decision_context": " ".join(decision_contexts),
            "disclaimer": "AgriN does not pick an absolute winner; the optimal crop depends on your farm's risk tolerance, irrigation assurance, and soil health priorities."
        }
    }


# Convenience alias
compare_crops = compare_candidate_crops

