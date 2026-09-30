"""
AgriN Farm Resilience Index — prototype
Transparent, component-based resilience scoring framework.
Evaluates farm adaptive capacity across 5 biophysical dimensions:
1. Soil Health (0.25)
2. Water Availability & Security (0.25)
3. Climate & Meteorological Context (0.20)
4. Crop Diversity & Rotational Health (0.15)
5. Crop Suitability (0.15)
Modulated by Data Confidence.
Explicitly labeled as a prototype index without unvalidated scientific claims.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from backend.app.services.soil_intelligence import assess_soil_health
    from backend.app.services.confidence_engine import compute_confidence
except ImportError:
    from app.services.soil_intelligence import assess_soil_health
    from app.services.confidence_engine import compute_confidence


def calculate_farm_resilience(
    farm_data: Dict[str, Any],
    soil_profile: Optional[Dict[str, Any]] = None,
    crop_suitability_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes the transparent AgriN Farm Resilience Index — prototype.
    Exposes every component and sub-indicator without black-box opacity.
    """
    # 1. Soil Health Component (0.25 weight)
    if soil_profile is None:
        soil_profile = assess_soil_health(farm_data, soil_type=farm_data.get("soil_type"))

    soil_score = float(soil_profile.get("score", 50.0))

    # 2. Water Availability & Context (0.25 weight)
    irrigation = str(farm_data.get("irrigation_available", "")).lower()
    rainfall_val = None
    if farm_data.get("rainfall") is not None:
        try:
            rainfall_val = float(farm_data["rainfall"])
        except (ValueError, TypeError):
            pass

    if irrigation in ["yes", "assured", "drip", "canal", "sprinkler", "tube_well"]:
        water_score = 85.0
        water_desc = "Assured irrigation buffers against meteorological drought."
    elif irrigation in ["partial", "limited", "protective"]:
        water_score = 65.0
        water_desc = "Partial protective irrigation; vulnerable to extended dry spells."
    else:  # Rainfed / no
        if rainfall_val is not None:
            if rainfall_val >= 1000:
                water_score = 75.0
                water_desc = f"Rainfed with high seasonal rainfall ({rainfall_val:.0f} mm); soil drainage is critical."
            elif rainfall_val >= 600:
                water_score = 60.0
                water_desc = f"Rainfed semi-arid tract ({rainfall_val:.0f} mm); high vulnerability to mid-season dry spells."
            else:
                water_score = 40.0
                water_desc = f"Arid rainfed condition ({rainfall_val:.0f} mm); severe water stress risk."
        else:
            water_score = 50.0
            water_desc = "Rainfed status with unspecified seasonal precipitation."

    # 3. Climate & Meteorological Context (0.20 weight)
    temp_val = None
    if farm_data.get("temperature") is not None:
        try:
            temp_val = float(farm_data["temperature"])
        except (ValueError, TypeError):
            pass

    humidity_val = None
    if farm_data.get("humidity") is not None:
        try:
            humidity_val = float(farm_data["humidity"])
        except (ValueError, TypeError):
            pass

    climate_penalties = 0.0
    climate_notes = []

    if temp_val is not None:
        if temp_val > 40.0:
            climate_penalties += 25.0
            climate_notes.append(f"Extreme heat stress ({temp_val:.1f}°C > 40°C) elevates evapotranspiration and pollen sterility.")
        elif temp_val < 10.0:
            climate_penalties += 20.0
            climate_notes.append(f"Chilling / frost risk ({temp_val:.1f}°C < 10°C) slows vegetative metabolism.")
        elif 20.0 <= temp_val <= 32.0:
            climate_notes.append(f"Ambient temperature ({temp_val:.1f}°C) is in the optimal physiological range.")

    if humidity_val is not None:
        if humidity_val > 85.0:
            climate_penalties += 15.0
            climate_notes.append("High relative humidity (>85%) elevates fungal disease proliferation risk.")
        elif humidity_val < 30.0:
            climate_penalties += 15.0
            climate_notes.append("Low atmospheric humidity (<30%) increases atmospheric water deficit.")

    climate_score = max(20.0, min(95.0, 90.0 - climate_penalties))

    # 4. Crop Diversity & Rotational Health (0.15 weight)
    crop_name = farm_data.get("crop") or farm_data.get("target_crop")
    rotation_type = farm_data.get("rotation_pattern") or farm_data.get("cropping_system")
    intercropping = farm_data.get("intercropping")

    diversity_score = 50.0  # Baseline monoculture
    diversity_notes = []

    if intercropping in [True, "yes", "true", "Intercropped"]:
        diversity_score += 25.0
        diversity_notes.append("Intercropping polyculture increases spatial land resilience and canopy cover.")
    
    if rotation_type in ["legume_rotation", "cereal_pulse", "diversified"]:
        diversity_score += 20.0
        diversity_notes.append("Legume inclusion in rotation breaks pest cycles and fixes biological nitrogen.")
    elif crop_name and str(crop_name).lower() in ["chickpea", "pigeonpeas", "mungbean", "blackgram", "lentil", "mothbeans"]:
        diversity_score += 15.0
        diversity_notes.append("Selected crop is a pulse/legume with biological nitrogen fixing capacity.")

    diversity_score = min(95.0, max(30.0, diversity_score))

    # 5. Crop Suitability (0.15 weight)
    if crop_suitability_score is not None:
        suitability_component = max(10.0, min(100.0, float(crop_suitability_score)))
    else:
        suitability_component = 70.0  # Default neutral

    # Calculate Data Confidence
    conf_assessment = compute_confidence(
        provided_fields=farm_data,
        geographic_resolution=farm_data.get("data_resolution", "DISTRICT"),
        model_probability=suitability_component / 100.0
    )
    confidence_val = conf_assessment["confidence_score"]

    # Composite Resilience Index
    composite_resilience = (
        0.25 * soil_score +
        0.25 * water_score +
        0.20 * climate_score +
        0.15 * diversity_score +
        0.15 * suitability_component
    )
    composite_resilience = round(composite_resilience, 1)

    # Classification
    if composite_resilience >= 80.0:
        resilience_tier = "HIGH_RESILIENCE"
        tier_description = "Farm exhibits strong adaptive buffers across soil, water, and agronomic management."
    elif composite_resilience >= 60.0:
        resilience_tier = "MODERATE_RESILIENCE"
        tier_description = "Farm has adequate baseline capacity but requires targeted interventions in limiting areas."
    elif composite_resilience >= 40.0:
        resilience_tier = "VULNERABLE"
        tier_description = "Farm is exposed to climate or resource shocks; priority should be placed on soil and water conservation."
    else:
        resilience_tier = "HIGHLY_VULNERABLE"
        tier_description = "Critical exposure across multiple biophysical dimensions; urgent regenerative interventions needed."

    # Identify Key Strengths & Vulnerabilities
    components_dict = {
        "soil_health": round(soil_score, 1),
        "water_context": round(water_score, 1),
        "climate_context": round(climate_score, 1),
        "crop_diversity": round(diversity_score, 1),
        "crop_suitability": round(suitability_component, 1)
    }

    strengths = [k.replace("_", " ").title() for k, v in components_dict.items() if v >= 75.0]
    vulnerabilities = [k.replace("_", " ").title() for k, v in components_dict.items() if v < 60.0]

    return {
        "index_name": "AgriN Farm Resilience Index — prototype",
        "score": composite_resilience,
        "resilience_tier": resilience_tier,
        "tier_description": tier_description,
        "confidence": confidence_val,
        "confidence_level": conf_assessment["confidence_level"],
        "components": components_dict,
        "weights": {
            "soil_health": 0.25,
            "water_context": 0.25,
            "climate_context": 0.20,
            "crop_diversity": 0.15,
            "crop_suitability": 0.15
        },
        "strengths": strengths,
        "vulnerabilities": vulnerabilities,
        "water_assessment": water_desc,
        "climate_notes": climate_notes,
        "diversity_notes": diversity_notes,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
