"""
AgriN — Farm Health Snapshot & Diagnostic Aggregator
===================================================

Aggregates biophysical evidence from verified farm inputs, real-time weather,
and soil observations to construct an honest, transparent FarmHealthSnapshot.

Track 4 Compliance:
- Zero fabrication: If satellite or disease data is not connected, fields remain null / UNAVAILABLE.
- Clear data confidence and provenance attached to every snapshot.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

from backend.app.models.intelligence_schemas import (
    DataCoverage,
    DataConfidenceLevel,
    DataResolution,
    DataSourceType,
    DataSourceMetadata,
    ConfidenceMetadata,
    FarmHealthSnapshot,
)
from backend.app.services.regenerative_service import compute_regenerative_indicators


def build_farm_health_snapshot(
    farm_id: str,
    farm_data: Dict[str, Any],
    soil_data: Dict[str, Any],
    env_data: Dict[str, Any],
    weather_info: Optional[Dict[str, Any]] = None,
    ranked_crops: Optional[List[Dict[str, Any]]] = None
) -> FarmHealthSnapshot:
    """
    Constructs a scientifically grounded, non-fabricated FarmHealthSnapshot.
    """
    sources: List[DataSourceMetadata] = []

    # 1. Soil Health Evaluation
    soil_fields_present = [k for k, v in soil_data.items() if v is not None]
    if soil_fields_present:
        ph = soil_data.get("ph")
        oc = soil_data.get("OC")
        n_val = soil_data.get("N")
        p_val = soil_data.get("P")
        k_val = soil_data.get("K")

        ph_status = "Optimal" if ph and 6.0 <= ph <= 7.8 else ("Acidic/Alkaline Stress" if ph else "Unknown")
        soc_status = "Adequate" if oc and oc >= 0.75 else ("Deficient" if oc else "Unmeasured")

        soil_health = {
            "status": "ASSESSED",
            "parameters_reported": len(soil_fields_present),
            "total_parameters": 12,
            "ph_condition": ph_status,
            "organic_carbon_condition": soc_status,
            "macronutrients": {
                "N": "Reported" if n_val is not None else "Missing",
                "P": "Reported" if p_val is not None else "Missing",
                "K": "Reported" if k_val is not None else "Missing",
            },
            "summary": f"Soil profile contains {len(soil_fields_present)} tested parameters."
        }
        sources.append(DataSourceMetadata(
            source_name="Farmer Soil Health Card / Soil Test Input",
            source_type=DataSourceType.FARMER_INPUT,
            coverage=DataCoverage.PARTIAL if len(soil_fields_present) < 10 else DataCoverage.FULL,
            resolution=DataResolution.POINT,
            license="User Submitted"
        ))
    else:
        soil_health = {
            "status": "UNAVAILABLE",
            "summary": "No soil laboratory parameters recorded."
        }

    # 2. Water Status Evaluation
    irrigation = farm_data.get("irrigation_available", "no")
    water_source = farm_data.get("water_source")
    rainfall = env_data.get("rainfall")

    water_status = {
        "status": "ASSESSED",
        "irrigation_available": irrigation == "yes",
        "primary_water_source": water_source or "Rainfed dependent",
        "annual_rainfall_benchmark_mm": rainfall,
        "drainage_condition": farm_data.get("drainage", "unknown")
    }

    # 3. Weather Risk Evaluation
    temp = env_data.get("temperature")
    humidity = env_data.get("humidity")
    weather_alerts = []

    if temp is not None:
        if temp > 40.0:
            weather_alerts.append(f"Extreme Heat Stress ({temp}°C): High evapotranspiration risk.")
        elif temp < 8.0:
            weather_alerts.append(f"Cold Stress ({temp}°C): Potential vegetative slowing.")

    if weather_info and weather_info.get("is_live_data"):
        sources.append(DataSourceMetadata(
            source_name="Open-Meteo Real-Time Weather API",
            source_type=DataSourceType.WEATHER,
            source_url="https://open-meteo.com",
            coverage=DataCoverage.FULL,
            resolution=DataResolution.DISTRICT,
            license="CC BY 4.0"
        ))
    else:
        sources.append(DataSourceMetadata(
            source_name="Indian Regional Climatology Database",
            source_type=DataSourceType.GOVERNMENT,
            coverage=DataCoverage.BASIC,
            resolution=DataResolution.STATE,
            license="Government Open Data"
        ))

    weather_risk = {
        "status": "ASSESSED",
        "current_temperature_c": temp,
        "current_relative_humidity": humidity,
        "active_alerts": weather_alerts,
        "risk_level": "HIGH" if weather_alerts else "NORMAL"
    }

    # 4. Crop Health / Suitability Status
    if ranked_crops:
        top_crop = ranked_crops[0]
        crop_health = {
            "status": "PREDICTED",
            "optimal_recommended_crop": top_crop.get("crop"),
            "top_suitability_score": top_crop.get("final_score"),
            "classification": top_crop.get("classification"),
            "summary": f"Top suitable crop identified as {top_crop.get('common_name')} ({top_crop.get('final_score')}%)."
        }
        sources.append(DataSourceMetadata(
            source_name="AgriN Random Forest Crop Model & Rule Engine",
            source_type=DataSourceType.ML_MODEL,
            coverage=DataCoverage.FULL,
            resolution=DataResolution.POINT,
            license="Proprietary / Open Research"
        ))
    else:
        crop_health = {
            "status": "UNAVAILABLE",
            "summary": "No crop analysis executed for this snapshot."
        }

    # 5. Satellite Vegetation Health — STRICTLY UNAVAILABLE (No fake data!)
    vegetation_health = {
        "status": "UNAVAILABLE",
        "reason": "Satellite multispectral imagery ingest not connected. Spectral indices (NDVI/EVI) cannot be fabricated.",
        "indices": {
            "NDVI": None,
            "NDWI": None,
            "EVI": None,
            "SAVI": None
        }
    }

    # 6. Crop Disease Risk — STRICTLY UNAVAILABLE (No fake data!)
    disease_risk = {
        "status": "UNAVAILABLE",
        "reason": "No on-field leaf image or diagnostic sensor observation received.",
        "confirmed_pathogens": [],
        "active_warnings": []
    }

    # 7. Regenerative Indicators
    regenerative_score = compute_regenerative_indicators(farm_data, soil_data, env_data)

    # 8. Overall Confidence Calculation
    total_sources = len(sources)
    has_live_weather = any(s.source_type == DataSourceType.WEATHER for s in sources)
    has_soil = len(soil_fields_present) >= 3

    if has_live_weather and has_soil:
        conf_level = DataConfidenceLevel.HIGH
        conf_score = 0.85
        cov = DataCoverage.PARTIAL  # Partial because satellite/disease are not yet present
    elif has_soil or has_live_weather:
        conf_level = DataConfidenceLevel.MEDIUM
        conf_score = 0.65
        cov = DataCoverage.PARTIAL
    else:
        conf_level = DataConfidenceLevel.LOW
        conf_score = 0.35
        cov = DataCoverage.BASIC

    overall_confidence = ConfidenceMetadata(
        confidence=conf_score,
        confidence_level=conf_level,
        coverage=cov,
        data_resolution=DataResolution.DISTRICT,
        data_timestamp=datetime.utcnow(),
        sources=sources
    )

    return FarmHealthSnapshot(
        farm_id=farm_id,
        soil_health=soil_health,
        water_status=water_status,
        crop_health=crop_health,
        weather_risk=weather_risk,
        disease_risk=disease_risk,
        vegetation_health=vegetation_health,
        regenerative_score=regenerative_score,
        overall_confidence=overall_confidence,
        timestamp=datetime.utcnow()
    )
