"""
AgriN Agricultural Risk Engine
===============================
Dedicated diagnostic engine for multi-factor agricultural risk detection.
Evaluates four biophysical risk pillars:
1. Water Risk (irrigation deficits, high water demand vs supply)
2. Soil Risk (salinity/EC, pH hazards, carbon depletion, nutrient imbalance)
3. Climate Risk (thermal spikes, heatwaves, frost, excessive rain/waterlogging)
4. Crop Risk (agronomic mismatch, seasonal misclassification, high limiting factors)

STRICT EVIDENCE RULE:
Every risk requires concrete empirical observations from farm, soil, or weather data.
Zero speculative predictions without data backing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum


class RiskSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskCategory(str, Enum):
    WATER = "WATER_RISK"
    SOIL = "SOIL_RISK"
    CLIMATE = "CLIMATE_RISK"
    CROP = "CROP_RISK"


def assess_agricultural_risks(
    farm_data: Dict[str, Any],
    soil_profile: Optional[Dict[str, Any]] = None,
    weather_info: Optional[Dict[str, Any]] = None,
    ranked_crops: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates farm, soil, weather, and crop factors to detect actionable agricultural risks.
    Returns structured list with:
    risk, severity, evidence, cause, implication, confidence, recommended_action, urgency
    """
    detected_risks = []
    
    # ── 1. WATER RISK ASSESSMENT ───────────────────────────────────────────────
    irrigation = str(farm_data.get("irrigation_available", "no")).lower() in ["yes", "true", "irrigated"]
    water_source = str(farm_data.get("water_source", "none")).lower()
    rainfall_val = None
    if farm_data.get("rainfall") is not None:
        try:
            rainfall_val = float(farm_data["rainfall"])
        except (ValueError, TypeError):
            pass
    elif weather_info and weather_info.get("rainfall") is not None:
        try:
            rainfall_val = float(weather_info["rainfall"])
        except (ValueError, TypeError):
            pass

    target_crop = (farm_data.get("crop") or farm_data.get("target_crop") or "").lower()
    top_crop = ranked_crops[0].get("crop", "").lower() if (ranked_crops and len(ranked_crops) > 0) else ""
    eval_crop = target_crop or top_crop

    # High water-demand crops
    HIGH_WATER_CROPS = {"rice", "sugarcane", "banana", "jute"}
    
    if eval_crop in HIGH_WATER_CROPS and not irrigation:
        if rainfall_val is not None and rainfall_val < 800:
            detected_risks.append({
                "category": RiskCategory.WATER.value,
                "risk": f"Severe Water Deficit Risk for {eval_crop.title()}",
                "severity": RiskSeverity.CRITICAL.value,
                "evidence": f"Crop '{eval_crop.title()}' requires 1000-1500 mm water, but farm is rainfed with only {rainfall_val:.0f} mm precipitation.",
                "cause": "Water requirement substantially exceeds ambient rainfed precipitation without irrigation.",
                "implication": "Acute terminal drought stress causing flower abortion or catastrophic crop failure.",
                "confidence": "HIGH",
                "recommended_action": "Switch to drought-hardy coarse cereals or pulses (Pigeonpea, Pearl Millet, Sorghum) unless supplemental irrigation is established.",
                "urgency": "IMMEDIATE"
            })
    elif not irrigation and (rainfall_val is not None and rainfall_val < 450):
        detected_risks.append({
            "category": RiskCategory.WATER.value,
            "risk": "Dryland Moisture Stress & Evaporative Deficit",
            "severity": RiskSeverity.HIGH.value,
            "evidence": f"Ambient rainfall ({rainfall_val:.0f} mm) is below dryland threshold (< 450 mm) under rainfed management.",
            "cause": "High atmospheric vapor pressure deficit combined with low precipitation.",
            "implication": "Mid-season dry spells may induce stomatal closure and vegetative stunting.",
            "confidence": "HIGH",
            "recommended_action": "Adopt Broad Bed and Furrow (BBF) layout and in-situ organic mulching to conserve moisture in rootzone.",
            "urgency": "SEASONAL"
        })

    # Drainage and Waterlogging risk
    drainage = str(farm_data.get("drainage", "good")).lower()
    soil_type = str(farm_data.get("soil_type", "black")).lower()
    if (drainage in ["poor", "very_poor", "waterlogged"]) or (soil_type in ["clay", "black"] and rainfall_val and rainfall_val > 1000):
        detected_risks.append({
            "category": RiskCategory.WATER.value,
            "risk": "Rootzone Waterlogging & Aeration Hazard",
            "severity": RiskSeverity.HIGH.value,
            "evidence": f"Heavy clay/Vertisol soil combined with {drainage} drainage and high rainfall ({rainfall_val:.0f} mm).",
            "cause": "Excess water cannot infiltrate subsoil, leading to standing surface water and oxygen depletion.",
            "implication": "Root asphyxiation, taproot rot, and high incidence of Phytophthora / Pythium fungal wilt.",
            "confidence": "HIGH",
            "recommended_action": "Construct drainage relief furrows and raised planting beds; avoid sensitive pulse crops like Chickpea in waterlogged parcels.",
            "urgency": "IMMEDIATE"
        })

    # ── 2. SOIL RISK ASSESSMENT ───────────────────────────────────────────────
    def _extract_val(container: Optional[Dict[str, Any]], *keys: str) -> Optional[float]:
        if not container:
            return None
        for k in keys:
            if k in container:
                v = container[k]
                if isinstance(v, dict):
                    v = v.get("value")
                if v is not None:
                    try:
                        return float(v)
                    except (ValueError, TypeError):
                        pass
        return None

    if soil_profile:
        # Check pH
        ph_val = _extract_val(soil_profile, "ph", "pH")
        if ph_val is not None:
            if ph_val < 5.2:
                detected_risks.append({
                    "category": RiskCategory.SOIL.value,
                    "risk": "Severe Soil Acidity & Aluminum Toxicity",
                    "severity": RiskSeverity.CRITICAL.value,
                    "evidence": f"Soil pH is {ph_val:.1f} (Critical limit < 5.5).",
                    "cause": "High aluminum/manganese activity inducing phosphorus fixation.",
                    "implication": "Root pruning, failed nodulation in legumes, and severe yield reduction in neutral-loving crops.",
                    "confidence": "HIGH",
                    "recommended_action": "Apply agricultural lime (CaCO3) or dolomite based on buffer lime requirement; use rock phosphate with compost.",
                    "urgency": "SEASONAL"
                })
            elif ph_val > 8.5:
                detected_risks.append({
                    "category": RiskCategory.SOIL.value,
                    "risk": "Sodic / High-Alkalinity Hazard",
                    "severity": RiskSeverity.CRITICAL.value,
                    "evidence": f"Soil pH is {ph_val:.1f} (Critical alkaline limit > 8.5).",
                    "cause": "Excess exchangeable sodium percentage (ESP) dispersing soil structure.",
                    "implication": "Surface soil crusting, poor water infiltration, and severe micronutrient immobilization (Zn, Fe).",
                    "confidence": "HIGH",
                    "recommended_action": "Apply agricultural gypsum @ 3-5 tonnes/ha followed by fresh water ponding and green manuring with Sesbania.",
                    "urgency": "SEASONAL"
                })

        # Check EC (Salinity)
        ec_val = _extract_val(soil_profile, "electrical_conductivity", "ec", "EC")
        if ec_val is not None:
            if ec_val >= 2.5:
                detected_risks.append({
                    "category": RiskCategory.SOIL.value,
                    "risk": "Rootzone Salinity Osmotic Shock",
                    "severity": RiskSeverity.HIGH.value,
                    "evidence": f"Electrical Conductivity (EC) is {ec_val:.2f} dS/m (Salinity threshold > 2.0 dS/m).",
                    "cause": "Accumulation of soluble salts in the capillary rootzone.",
                    "implication": "Osmotic resistance prevents root water uptake even in moist soil; leaf edge necrosis.",
                    "confidence": "HIGH",
                    "recommended_action": "Select salt-tolerant crops (Barley, Mustard, Cotton); avoid chloride fertilizers and improve drainage leaching.",
                    "urgency": "IMMEDIATE"
                })

        # Check Organic Carbon
        oc_val = _extract_val(soil_profile, "organic_carbon", "oc", "OC")
        if oc_val is not None:
            if oc_val < 0.40:
                detected_risks.append({
                    "category": RiskCategory.SOIL.value,
                    "risk": "Acute Soil Biological & Carbon Depletion",
                    "severity": RiskSeverity.HIGH.value,
                    "evidence": f"Soil Organic Carbon is {oc_val:.2f}% (Minimum threshold 0.50%).",
                    "cause": "Intensive tillage, residue removal, and lack of organic carbon return.",
                    "implication": "Low nutrient-use efficiency, collapsed soil structure, rapid moisture evaporation.",
                    "confidence": "HIGH",
                    "recommended_action": "Incorporate 8-10 tonnes/ha FYM or compost; implement cover cropping and zero-tillage residue retention.",
                    "urgency": "SEASONAL"
                })

    # ── 3. CLIMATE RISK ASSESSMENT ────────────────────────────────────────────
    temp_val = _extract_val(weather_info, "temperature", "temp") or _extract_val(farm_data, "temperature", "temp")
    humidity_val = _extract_val(weather_info, "humidity", "relative_humidity") or _extract_val(farm_data, "humidity", "relative_humidity")

    if temp_val is not None:
        if temp_val >= 41.0:
            detected_risks.append({
                "category": RiskCategory.CLIMATE.value,
                "risk": "Severe Thermal Heatwave Stress",
                "severity": RiskSeverity.HIGH.value,
                "evidence": f"Ambient temperature ({temp_val:.1f}°C) exceeds critical physiological threshold (40°C).",
                "cause": "Extreme atmospheric heat wave and solar radiation.",
                "implication": "Pollen sterility, flower drop, accelerated evapotranspiration, and leaf desiccation.",
                "confidence": "HIGH",
                "recommended_action": "Apply light evening irrigation or micro-sprinklers; apply kaolin foliar spray (5%) to reflect excess radiation.",
                "urgency": "IMMEDIATE"
            })
        elif temp_val <= 6.0:
            detected_risks.append({
                "category": RiskCategory.CLIMATE.value,
                "risk": "Chilling / Frost Exposure Risk",
                "severity": RiskSeverity.HIGH.value,
                "evidence": f"Minimum temperature ({temp_val:.1f}°C) approaches frost hazard range (< 6°C).",
                "cause": "Cold air inversion and nocturnal radiative heat loss.",
                "implication": "Cellular rupture in tender foliage, flower damage in mustard and vegetables.",
                "confidence": "HIGH",
                "recommended_action": "Provide light nighttime irrigation to raise latent soil heat; create protective field smoke screens around orchard borders.",
                "urgency": "IMMEDIATE"
            })

    if humidity_val is not None and humidity_val >= 88.0 and (temp_val and 22.0 <= temp_val <= 32.0):
        detected_risks.append({
            "category": RiskCategory.CLIMATE.value,
            "risk": "Fungal Folio-Pathology Environmental Window",
            "severity": RiskSeverity.MEDIUM.value,
            "evidence": f"Relative Humidity ({humidity_val:.0f}%) and Temperature ({temp_val:.1f}°C) create optimal fungal spore incubation conditions.",
            "cause": "Sustained high humidity and warm ambient temperatures.",
            "implication": "Elevated risk of foliar blights, powdery/downy mildew, and blast outbreaks.",
            "confidence": "MEDIUM",
            "recommended_action": "Enhance canopy aeration through pruning; scout lower leaves for initial fungal lesions before applying protective bio-fungicide (Trichoderma).",
            "urgency": "MONITORING"
        })

    # ── 4. CROP RISK ASSESSMENT ───────────────────────────────────────────────
    if target_crop and ranked_crops:
        matched = [c for c in ranked_crops if c.get("crop", "").lower() == target_crop]
        if matched:
            target_score = matched[0].get("overall_score") or matched[0].get("final_score") or 0.0
            if target_score < 45.0:
                detected_risks.append({
                    "category": RiskCategory.CROP.value,
                    "risk": f"Poor Agro-Ecological Suitability for Chosen Crop ({target_crop.title()})",
                    "severity": RiskSeverity.CRITICAL.value,
                    "evidence": f"Calculated suitability score is only {target_score:.1f}/100 with severe limiting gates.",
                    "cause": "Fundamental biophysical mismatch between crop thermal/soil needs and farm conditions.",
                    "implication": "High probability of economic loss, stunted growth, and susceptibility to pest complexes.",
                    "confidence": "HIGH",
                    "recommended_action": f"Reconsider cultivating {target_crop.title()}. Switch to top viable alternative: {ranked_crops[0].get('crop', '').title()} (Score: {ranked_crops[0].get('overall_score', 80):.1f}/100).",
                    "urgency": "IMMEDIATE"
                })

    return detected_risks


def generate_prioritized_advisories(
    risks: List[Dict[str, Any]],
    soil_profile: Optional[Dict[str, Any]] = None,
    regenerative_opportunities: Optional[List[Dict[str, Any]]] = None,
    ranked_crops: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Transforms detected risks, soil constraints, and regenerative opportunities into
    a strictly prioritized advisory queue (CRITICAL, HIGH, MEDIUM, LOW).
    """
    advisories = []
    
    # 1. Map Risks to Advisories
    for r in risks:
        advisories.append({
            "priority": r["severity"],  # CRITICAL, HIGH, MEDIUM, LOW
            "category": r["category"],
            "recommendation": r["recommended_action"],
            "reason": r["implication"],
            "trigger": r["evidence"],
            "confidence": r["confidence"],
            "urgency": r["urgency"],
            "limitations": ["Continuous field monitoring recommended."]
        })

    # 2. Map Regenerative Opportunities to HIGH / MEDIUM Advisories
    if regenerative_opportunities and isinstance(regenerative_opportunities, list):
        for opp in regenerative_opportunities:
            if not isinstance(opp, dict):
                continue
            # Avoid duplicating already generated advisories
            prio = "HIGH" if "low" in opp.get("trigger", "").lower() or "critical" in opp.get("trigger", "").lower() else "MEDIUM"
            advisories.append({
                "priority": prio,
                "category": "REGENERATIVE_OPPORTUNITY",
                "recommendation": f"{opp.get('practice')}: {opp.get('objective')}",
                "reason": opp.get("why"),
                "trigger": opp.get("trigger"),
                "confidence": opp.get("confidence", "HIGH"),
                "urgency": "SEASONAL",
                "limitations": opp.get("limitations", ["Depends on farm biomass and seed availability."])
            })

    # 3. Sort by priority rank: CRITICAL > HIGH > MEDIUM > LOW
    rank_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    advisories.sort(key=lambda x: rank_order.get(x["priority"], 4))

    return advisories
