"""
AgriN — Irrigation Intelligence Service
=======================================
Deterministic, agronomic irrigation advisory service combining:
1. In-situ capacitive soil moisture measurements (% volumetric water content)
2. Soil texture physical properties (Field Capacity, Permanent Wilting Point)
3. Crop-specific water depletion thresholds (FAO-56 Irrigation & Drainage guidelines)
4. Upcoming precipitation forecast (Open-Meteo / weather telemetry)

CRITICAL RULE:
If in-situ soil moisture sensor data is absent/invalid, the engine returns an
explicit UNAVAILABLE status rather than fabricating an irrigation schedule.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Soil Physical Constants: Available Water Capacity (AWC) by Texture Class
# Values: (Field Capacity %, Permanent Wilting Point %)
# Source: USDA NRCS & ICAR Soil Physics Guidelines
# ---------------------------------------------------------------------------
SOIL_HYDROLOGY_PROPERTIES = {
    "clay": {"fc": 40.0, "pwp": 22.0, "name": "Clay / Black Cotton Soil"},
    "clay_loam": {"fc": 34.0, "pwp": 18.0, "name": "Clay Loam"},
    "silt_loam": {"fc": 30.0, "pwp": 12.0, "name": "Silt Loam"},
    "loam": {"fc": 26.0, "pwp": 10.0, "name": "Loam / Alluvial"},
    "sandy_loam": {"fc": 18.0, "pwp": 7.0, "name": "Sandy Loam"},
    "sand": {"fc": 10.0, "pwp": 4.0, "name": "Sand / Arid Sandy"},
    "red_loam": {"fc": 24.0, "pwp": 9.0, "name": "Red Sandy Loam"},
    "black": {"fc": 38.0, "pwp": 20.0, "name": "Medium/Deep Black (Vertisol)"},
    "default": {"fc": 28.0, "pwp": 12.0, "name": "Generic Agricultural Loam"},
}

# ---------------------------------------------------------------------------
# Crop Maximum Allowable Depletion (MAD / fraction p)
# Fraction of total available water (TAW) that can be depleted before stress occurs.
# Source: FAO-56 Table 22
# ---------------------------------------------------------------------------
CROP_MAD_THRESHOLDS = {
    "rice": 0.20,        # Sensitive to any drying (lowland/paddy)
    "wheat": 0.55,
    "maize": 0.50,
    "cotton": 0.65,      # Deep-rooted, drought tolerant
    "soybean": 0.50,
    "sugarcane": 0.65,
    "groundnut": 0.50,
    "chickpea": 0.60,    # Pulses handle higher depletion
    "pigeonpeas": 0.65,
    "mothbeans": 0.70,
    "mungbean": 0.55,
    "blackgram": 0.55,
    "lentil": 0.60,
    "coffee": 0.40,
    "banana": 0.35,      # High water demand, shallow root zone
    "apple": 0.50,
    "orange": 0.50,
    "papaya": 0.40,
    "coconut": 0.55,
    "jute": 0.45,
    "default": 0.50,
}


def compute_irrigation_advisory(
    soil_moisture_pct: Optional[float],
    soil_type: str = "default",
    crop: str = "default",
    forecast_rain_mm_next_48h: float = 0.0,
    temperature_c: Optional[float] = None,
    humidity_pct: Optional[float] = None,
    measurement_quality: str = "GOOD",
    data_source: str = "SENSOR_MEASURED"
) -> Dict[str, Any]:
    """
    Computes an evidence-grounded irrigation advisory.

    Returns an explicit UNAVAILABLE structure if soil_moisture_pct is None.
    """
    # Guard: Missing or invalid physical measurement
    if soil_moisture_pct is None or measurement_quality in ("INVALID", "MISSING"):
        return {
            "status": "UNAVAILABLE",
            "irrigation_needed": False,
            "urgency": "UNKNOWN",
            "recommended_amount_mm": 0.0,
            "soil_moisture_pct": None,
            "data_source": "UNAVAILABLE",
            "rationale": (
                "In-situ soil moisture sensor reading is unavailable or invalid. "
                "AgriN enforces zero data fabrication and does not guess irrigation schedules."
            ),
            "recommendation": "Verify physical probe connection, power supply, and ADC calibration.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Normalize soil properties
    clean_soil = str(soil_type).lower().replace(" ", "_")
    soil_props = SOIL_HYDROLOGY_PROPERTIES.get(clean_soil, SOIL_HYDROLOGY_PROPERTIES["default"])
    fc = soil_props["fc"]
    pwp = soil_props["pwp"]
    taw = max(1.0, fc - pwp)  # Total Available Water (%)

    # Normalize crop MAD
    clean_crop = str(crop).lower().strip()
    mad = CROP_MAD_THRESHOLDS.get(clean_crop, CROP_MAD_THRESHOLDS["default"])

    # Readily Available Water threshold moisture
    raw_threshold = fc - (taw * mad)

    # Calculate current moisture status
    if soil_moisture_pct > fc:
        moisture_condition = "SATURATED"
        depletion_fraction = 0.0
        irrigation_needed = False
        urgency = "NONE"
        recommended_mm = 0.0
        rationale = (
            f"Soil moisture ({soil_moisture_pct:.1f}%) exceeds field capacity ({fc:.1f}%). "
            f"Field is saturated. Aeration risk present; cease all irrigation and check drainage."
        )
    elif soil_moisture_pct >= raw_threshold:
        moisture_condition = "OPTIMAL"
        depletion_fraction = (fc - soil_moisture_pct) / taw
        irrigation_needed = False
        urgency = "LOW"
        recommended_mm = 0.0
        rationale = (
            f"Soil moisture ({soil_moisture_pct:.1f}%) is within optimal buffer zone "
            f"(Threshold: {raw_threshold:.1f}%, FC: {fc:.1f}%). No moisture stress detected."
        )
    elif soil_moisture_pct > pwp:
        moisture_condition = "DEPLETED"
        depletion_fraction = (fc - soil_moisture_pct) / taw
        irrigation_needed = True
        deficit_pct = fc - soil_moisture_pct
        # Assuming 200 mm effective root zone for topsoil: 1% deficit ≈ 2 mm water
        raw_deficit_mm = deficit_pct * 2.0
        # Discount upcoming rain
        effective_rain = max(0.0, forecast_rain_mm_next_48h * 0.8)
        recommended_mm = max(0.0, round(raw_deficit_mm - effective_rain, 1))

        if recommended_mm <= 5.0 and forecast_rain_mm_next_48h > 10.0:
            urgency = "DEFERRED"
            irrigation_needed = False
            rationale = (
                f"Moisture ({soil_moisture_pct:.1f}%) is below MAD ({raw_threshold:.1f}%), "
                f"but {forecast_rain_mm_next_48h:.1f} mm rain is forecasted in next 48h. "
                f"Defer irrigation to conserve water and prevent nutrient leaching."
            )
        else:
            urgency = "MODERATE" if depletion_fraction < 0.8 else "HIGH"
            rationale = (
                f"Soil moisture ({soil_moisture_pct:.1f}%) depleted past allowable limit ({raw_threshold:.1f}%). "
                f"Replenishment of {recommended_mm:.1f} mm required to restore root zone to field capacity."
            )
    else:
        moisture_condition = "SEVERELY_DEPLETED"
        depletion_fraction = 1.0
        irrigation_needed = True
        urgency = "CRITICAL"
        deficit_pct = fc - soil_moisture_pct
        raw_deficit_mm = deficit_pct * 2.0
        effective_rain = max(0.0, forecast_rain_mm_next_48h * 0.8)
        recommended_mm = max(10.0, round(raw_deficit_mm - effective_rain, 1))
        rationale = (
            f"CRITICAL: Soil moisture ({soil_moisture_pct:.1f}%) has fallen below the Permanent Wilting Point ({pwp:.1f}%). "
            f"Crop is experiencing severe water stress. Immediate irrigation of {recommended_mm:.1f} mm required."
        )

    # Recommended method based on soil texture
    if "sand" in clean_soil:
        method = "High-frequency Drip (sandy soils have high percolation and low water holding capacity)"
    elif "clay" in clean_soil or "black" in clean_soil:
        method = "Controlled Drip or Furrow (heavy soils have low infiltration rate; prevent surface waterlogging)"
    else:
        method = "Drip or Micro-sprinkler"

    return {
        "status": "CALCULATED",
        "irrigation_needed": irrigation_needed,
        "urgency": urgency,
        "moisture_condition": moisture_condition,
        "soil_moisture_pct": round(soil_moisture_pct, 1),
        "field_capacity_pct": fc,
        "wilting_point_pct": pwp,
        "depletion_threshold_pct": round(raw_threshold, 1),
        "recommended_amount_mm": recommended_mm,
        "recommended_method": method,
        "forecast_rain_discount_mm": round(forecast_rain_mm_next_48h, 1),
        "data_source": data_source,
        "measurement_quality": measurement_quality,
        "rationale": rationale,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
