"""
FarmFriend AI — Rule-Based NLG Explanation Engine
===================================================

Generates natural language explanations entirely from analytical results
WITHOUT any external LLM API.

Uses:
- Template-based generation
- Conditional logic based on score ranges, factor counts, and crop details
- Pre-built Q&A response patterns

This approach ensures:
- Explanations are ALWAYS grounded in actual model results
- No hallucinated measurements or unsupported claims
- Deterministic, reproducible outputs
- Zero external API dependency
"""

import random
from typing import List, Optional

# ── Score classification labels ───────────────────────────────────────────────
def _score_label(score: float) -> str:
    if score >= 80: return "highly suitable"
    if score >= 60: return "moderately suitable"
    if score >= 40: return "below the moderate threshold"
    return "not well-suited"


def _score_word(score: float) -> str:
    if score >= 85: return "excellent"
    if score >= 75: return "good"
    if score >= 60: return "moderate"
    if score >= 40: return "low"
    return "poor"


def _factor_list_text(factors: list, status_filter: str, max_items: int = 3) -> str:
    """Convert factor list to readable text."""
    items = [f for f in factors if f.get("status") == status_filter][:max_items]
    if not items:
        return ""
    names = [f["factor"] for f in items]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


# ── RECOMMENDATION EXPLANATIONS ───────────────────────────────────────────────

def explain_top_recommendations(ranked_crops: list, farm_data: dict, soil_data: dict) -> str:
    """
    Explain the overall crop ranking to the farmer.
    
    Args:
        ranked_crops: list of crop result dicts (from suitability scorer)
        farm_data: farmer's location/season/irrigation data
        soil_data: farmer's soil measurements
    
    Returns: plain English explanation string
    """
    if not ranked_crops:
        return "No crop recommendations could be computed with the provided information."

    top = ranked_crops[0]
    top_name = top.get("common_name", top.get("crop", "").title())
    top_score = top.get("final_score", 0)
    season = farm_data.get("season", "the current season")
    district = farm_data.get("district", "your area")

    # Count well-suited crops
    high_suitable = [c for c in ranked_crops if c.get("final_score", 0) >= 75]
    moderate_suitable = [c for c in ranked_crops if 50 <= c.get("final_score", 0) < 75]

    # Build explanation
    parts = []

    # Opening
    if top_score >= 80:
        parts.append(
            f"Based on the soil test values and farm conditions you have entered, "
            f"{top_name} appears to be the most suitable crop for {season} season in {district}, "
            f"with a suitability score of {top_score}/100."
        )
    elif top_score >= 60:
        parts.append(
            f"Based on the supplied information, {top_name} is the highest-ranked crop "
            f"with a moderate suitability score of {top_score}/100."
        )
    else:
        parts.append(
            f"The analysis found that crop suitability is generally limited with the current conditions. "
            f"{top_name} ranks highest with a score of {top_score}/100, "
            f"but conditions may need improvement."
        )

    # Supporting factors for top crop
    supporting = top.get("supporting_factors", [])
    if supporting:
        s_text = _factor_list_text(supporting, "suitable", 3)
        if s_text:
            parts.append(f"The {top_name} ranking is supported by favourable conditions in: {s_text}.")

    # Limiting factors for top crop
    limiting = top.get("limiting_factors", [])
    if limiting:
        l_text = _factor_list_text(limiting, "limiting", 2)
        if l_text:
            parts.append(f"The primary limiting factors identified for {top_name} are: {l_text}.")

    # Overall spread
    if len(high_suitable) > 1:
        names = [c.get("common_name", c["crop"].title()) for c in high_suitable[:4]]
        parts.append(
            f"In total, {len(high_suitable)} crops show high suitability under current conditions: "
            + ", ".join(names) + "."
        )
    elif moderate_suitable:
        parts.append(
            f"{len(moderate_suitable)} additional crops show moderate suitability. "
            "You can click any crop to see its detailed analysis."
        )

    # Data quality note
    confidence = top.get("data_confidence", "medium")
    if confidence == "low":
        parts.append(
            "Note: Several soil parameters were not entered. "
            "Providing more complete soil test data will improve the reliability of these results."
        )
    elif confidence == "medium":
        parts.append(
            "Some soil parameters were not provided. "
            "The analysis uses available data; additional soil test values would improve accuracy."
        )

    parts.append(
        "These are decision-support estimates only. "
        "Please verify recommendations with your local Krishi Vigyan Kendra (KVK) "
        "or agricultural extension officer."
    )

    return " ".join(parts)


def explain_crop_detail(crop_result: dict) -> str:
    """
    Explain a single crop's suitability analysis.
    """
    name = crop_result.get("common_name", crop_result.get("crop", "").title())
    score = crop_result.get("final_score", 0)
    classification = crop_result.get("classification", "")
    supporting = crop_result.get("supporting_factors", [])
    limiting = crop_result.get("limiting_factors", [])
    moderate = crop_result.get("moderate_factors", [])
    missing = crop_result.get("missing_factors", [])
    data_conf = crop_result.get("data_confidence", "medium")
    mh_regions = crop_result.get("maharashtra_regions", [])

    parts = []

    # Score interpretation
    score_word = _score_word(score)
    if score >= 80:
        parts.append(
            f"The analysis indicates that {name} has {score_word} suitability "
            f"(score: {score}/100) for the supplied conditions."
        )
    elif score >= 60:
        parts.append(
            f"The analysis indicates {score_word} suitability for {name} "
            f"(score: {score}/100). The crop can be considered but attention to some factors is needed."
        )
    elif score >= 40:
        parts.append(
            f"{name} shows {score_word} suitability (score: {score}/100) "
            f"under the current supplied conditions."
        )
    else:
        parts.append(
            f"The current supplied conditions appear unfavourable for {name} "
            f"(score: {score}/100). Growing this crop may be challenging without improvements."
        )

    # Supporting conditions
    s_suitable = [f for f in supporting if f.get("status") == "suitable"]
    if s_suitable:
        s_names = [f["factor"] for f in s_suitable[:4]]
        parts.append(f"Favourable conditions: {', '.join(s_names)}.")

    # Limiting factors
    if limiting:
        l_names = [f["factor"] for f in limiting[:3]]
        l_notes = [f.get("note", "") for f in limiting[:2]]
        parts.append(f"Main limiting factors: {', '.join(l_names)}.")
        for note in l_notes:
            if note:
                parts.append(f"  • {note}")

    # Moderate factors
    if moderate:
        m_names = [f["factor"] for f in moderate[:3]]
        parts.append(f"Factors needing attention: {', '.join(m_names)}.")

    # Missing data warning
    if missing:
        m_names = [f["factor"] for f in missing[:4]]
        parts.append(
            f"The following parameters were not entered and could not be evaluated: "
            f"{', '.join(m_names)}. This reduces the confidence of the result."
        )

    # Maharashtra regional note
    if mh_regions:
        regions_text = ", ".join(mh_regions[:3])
        parts.append(f"In Maharashtra, this crop is commonly grown in: {regions_text}.")

    # Data confidence
    if data_conf == "low":
        parts.append(
            "⚠️ Data confidence is LOW due to many missing input values. "
            "Please enter more soil test parameters for a more reliable analysis."
        )

    parts.append(
        "This result is a model-based decision-support estimate. "
        "Confirm with a qualified agricultural professional before making farming decisions."
    )

    return " ".join(parts)


# ── FEASIBILITY EXPLANATION ───────────────────────────────────────────────────

def explain_feasibility(crop_result: dict, farmer_chose: str) -> str:
    """
    Explain feasibility of a farmer-selected crop (the 'I Want to Grow This' feature).
    """
    name = crop_result.get("common_name", farmer_chose.title())
    score = crop_result.get("final_score", 0)
    supporting = crop_result.get("supporting_factors", [])
    limiting = crop_result.get("limiting_factors", [])
    moderate = crop_result.get("moderate_factors", [])
    missing = crop_result.get("missing_factors", [])

    parts = []

    # Opening
    if score >= 75:
        parts.append(
            f"Good news! The analysis of your supplied conditions suggests that "
            f"{name} is feasible for your farm with a suitability score of {score}/100. "
            f"Your current conditions appear compatible with this crop."
        )
    elif score >= 55:
        parts.append(
            f"The analysis shows that {name} is potentially feasible "
            f"(score: {score}/100) but with some conditions that need attention."
        )
    elif score >= 35:
        parts.append(
            f"The analysis indicates that {name} has low suitability "
            f"(score: {score}/100) under the current supplied conditions. "
            f"Growing this crop may require improvements to soil or other conditions."
        )
    else:
        parts.append(
            f"The analysis indicates that current supplied conditions are unfavourable "
            f"for {name} (score: {score}/100). "
            f"Significant improvements would be needed to grow this crop successfully."
        )

    # Favourable conditions
    s_suitable = [f for f in supporting if f.get("status") == "suitable"]
    if s_suitable:
        s_names = [f["factor"] for f in s_suitable[:4]]
        parts.append(f"Conditions currently in your favour: {', '.join(s_names)}.")

    # Limiting factors — most important
    if limiting:
        l_items = limiting[:3]
        parts.append("Primary conditions affecting suitability:")
        for f in l_items:
            parts.append(f"  ✗ {f['factor']}: {f.get('note', 'Limiting condition identified')}")

    # Moderate factors
    if moderate:
        m_items = moderate[:3]
        parts.append("Conditions that may need monitoring:")
        for f in m_items:
            parts.append(f"  ⚠ {f['factor']}: {f.get('note', 'May require attention')}")

    # Missing data
    if missing:
        m_names = [f["factor"] for f in missing[:4]]
        parts.append(
            f"Missing information (could not be evaluated): {', '.join(m_names)}. "
            "Providing these values would give a more complete picture."
        )

    # What-if hint
    if limiting:
        parts.append(
            "💡 Tip: Use the What-If Simulator to see how improving specific conditions "
            "might change the suitability score for this crop."
        )

    parts.append(
        "⚠️ These results are based on the information you supplied and should not be taken "
        "as a guarantee of crop performance. Consult your local agricultural extension office "
        "or Krishi Vigyan Kendra (KVK) before making farming decisions."
    )

    return "\n".join(parts)


# ── WHAT-IF EXPLANATION ───────────────────────────────────────────────────────

def explain_whatif(
    crop_name: str,
    before_score: float,
    after_score: float,
    changed_params: dict,
    before_result: dict,
    after_result: dict
) -> str:
    """
    Explain a what-if simulation result.
    
    Args:
        crop_name: the crop being analysed
        before_score: suitability score before changes
        after_score: suitability score after changes
        changed_params: dict of {param_name: {"before": val, "after": val}}
        before_result: full crop result before
        after_result: full crop result after
    """
    change = after_score - before_score
    name = after_result.get("common_name", crop_name.title())

    parts = []

    # Simulation disclaimer — always first
    parts.append(
        "⚠️ Simulation Note: This is a simulated scenario only. "
        "The values entered here have not been verified in your actual field. "
        "Results do not guarantee the same outcome in practice."
    )
    parts.append("")

    # Score change summary
    if abs(change) < 1:
        parts.append(
            f"The simulated changes had minimal effect on {name}'s suitability score "
            f"(remained approximately {before_score}/100)."
        )
    elif change > 0:
        parts.append(
            f"Under this simulated scenario, {name}'s suitability score increased from "
            f"{before_score}/100 → {after_score}/100 (improvement of +{change:.1f} points)."
        )
    else:
        parts.append(
            f"Under this simulated scenario, {name}'s suitability score decreased from "
            f"{before_score}/100 → {after_score}/100 (change of {change:.1f} points)."
        )

    # What changed
    if changed_params:
        parts.append("\nChanges simulated:")
        for param, vals in changed_params.items():
            bv = vals.get("before", "not entered")
            av = vals.get("after", "not entered")
            parts.append(f"  • {param}: {bv} → {av}")

    # New limiting factors (factors that became limiting after change)
    before_lim = {f["factor"] for f in before_result.get("limiting_factors", [])}
    after_lim = {f["factor"] for f in after_result.get("limiting_factors", [])}

    newly_resolved = before_lim - after_lim
    newly_limiting = after_lim - before_lim

    if newly_resolved:
        parts.append(
            f"\nConditions improved by the simulated changes: {', '.join(newly_resolved)}."
        )

    if newly_limiting:
        parts.append(
            f"\nConditions that became limiting in simulation: {', '.join(newly_limiting)}."
        )

    # New classification change
    before_class = before_result.get("classification", "")
    after_class = after_result.get("classification", "")
    if before_class != after_class:
        parts.append(
            f"\nThe classification changed from {before_class} to {after_class} "
            f"under the simulated conditions."
        )

    # Model explanation
    parts.append(
        "\nThe score change is computed by the same model used for the original analysis — "
        "both the ML model prediction and the rule-based agricultural knowledge layer "
        "recalculated with the simulated input values."
    )

    return "\n".join(parts)


# ── FARMER Q&A RESPONSES ──────────────────────────────────────────────────────

def answer_why_recommended(crop_result: dict, ranked_position: int) -> str:
    """Answer 'Why did you recommend this crop?'"""
    name = crop_result.get("common_name", crop_result.get("crop", "").title())
    score = crop_result.get("final_score", 0)
    supporting = crop_result.get("supporting_factors", [])
    ml_score = crop_result.get("ml_score", 0)
    rule_score = crop_result.get("rule_score", 0)

    parts = []

    if ranked_position == 1:
        parts.append(f"{name} ranks first because it has the highest overall suitability score ({score}/100) "
                     f"based on the soil test values and farm conditions you entered.")
    else:
        parts.append(f"{name} ranks at position {ranked_position} with a score of {score}/100.")

    s_suitable = [f for f in supporting if f.get("status") == "suitable"]
    if s_suitable:
        s_names = [f["factor"] for f in s_suitable[:4]]
        parts.append(f"The following conditions in your soil and environment are favourable for {name}: "
                     f"{', '.join(s_names)}.")

    parts.append(
        f"The score is computed from: the ML model prediction ({ml_score}/100, weight 60%) "
        f"and the agricultural rule check ({rule_score}/100, weight 40%)."
    )

    return " ".join(parts)


def answer_why_lower(crop_result: dict, better_crop_result: dict) -> str:
    """Answer 'Why is crop X ranked lower than crop Y?'"""
    name = crop_result.get("common_name", crop_result.get("crop", "").title())
    score = crop_result.get("final_score", 0)
    better_name = better_crop_result.get("common_name", better_crop_result.get("crop", "").title())
    better_score = better_crop_result.get("final_score", 0)
    limiting = crop_result.get("limiting_factors", [])

    parts = [
        f"{name} (score: {score}/100) ranks lower than {better_name} (score: {better_score}/100) "
        f"because the current supplied conditions are more compatible with {better_name}."
    ]

    if limiting:
        l_names = [f["factor"] for f in limiting[:3]]
        parts.append(
            f"The main factors reducing {name}'s score are: {', '.join(l_names)}."
        )
        for f in limiting[:2]:
            if f.get("note"):
                parts.append(f"  • {f['note']}")

    return " ".join(parts)


def answer_what_if_hint(crop_name: str, limiting_factors: list) -> str:
    """Suggest what to simulate in the what-if tool."""
    name = crop_name.title()
    if not limiting_factors:
        return (
            f"The current conditions already appear reasonably suitable for {name}. "
            "You can use the What-If Simulator to see how any changes might affect the score."
        )

    l_names = [f["factor"] for f in limiting_factors[:3]]
    return (
        f"To explore how to improve {name}'s suitability, "
        f"try simulating improvements to: {', '.join(l_names)}. "
        "Open the What-If Simulator and adjust these values to see the potential effect on the score."
    )


def generate_summary_card(crop_result: dict) -> dict:
    """
    Generate a structured summary card for the frontend AI explanation panel.
    Returns structured JSON (not raw LLM output).
    """
    name = crop_result.get("common_name", crop_result.get("crop", "").title())
    score = crop_result.get("final_score", 0)
    classification = crop_result.get("classification", "")
    data_conf = crop_result.get("data_confidence", "medium")
    limiting = crop_result.get("limiting_factors", [])
    missing = crop_result.get("missing_factors", [])

    return {
        "crop": crop_result.get("crop"),
        "common_name": name,
        "suitability_score": score,
        "classification": classification,
        "data_confidence": data_conf,
        "key_supporting_factors": [
            f["factor"] for f in crop_result.get("supporting_factors", [])
            if f.get("status") == "suitable"
        ][:4],
        "key_limiting_factors": [
            f["factor"] for f in limiting
        ][:3],
        "missing_information": [
            f["factor"] for f in missing
        ][:4],
        "explanation": explain_crop_detail(crop_result),
        "confidence": data_conf,
        "disclaimer_required": True,
        "disclaimer": (
            "This result is a decision-support estimate based on the information supplied. "
            "It does not replace professional agricultural advice or local agricultural recommendations."
        )
    }
