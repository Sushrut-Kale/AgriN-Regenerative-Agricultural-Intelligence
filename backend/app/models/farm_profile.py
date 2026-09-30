"""
AgriN Unified Farm Digital Profile Model
Extensible, country-neutral schema encapsulating the complete farm digital twin:
Location, Soil, Crops, Season, Irrigation, Weather, Crop Health, Soil Health,
Recommendations, and Historical Observations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class FarmLocation(BaseModel):
    country: str = "India"
    admin_level_1: str = Field(description="State / Province")
    admin_level_2: str = Field(description="District / Municipality")
    admin_level_3: Optional[str] = Field(None, description="Sub-district / Taluka / Tehsil / County")
    admin_level_4: Optional[str] = Field(None, description="Village / Parish / Locality")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    boundary_geojson: Optional[Dict[str, Any]] = None
    area_hectares: Optional[float] = None
    agro_ecological_zone_code: Optional[str] = None


class FarmSoilContext(BaseModel):
    soil_type: Optional[str] = None
    nitrogen_kg_ha: Optional[float] = None
    phosphorus_kg_ha: Optional[float] = None
    potassium_kg_ha: Optional[float] = None
    ph: Optional[float] = None
    electrical_conductivity_ds_m: Optional[float] = None
    organic_carbon_percent: Optional[float] = None
    sulphur_ppm: Optional[float] = None
    zinc_ppm: Optional[float] = None
    iron_ppm: Optional[float] = None
    copper_ppm: Optional[float] = None
    manganese_ppm: Optional[float] = None
    boron_ppm: Optional[float] = None
    moisture_percent: Optional[float] = None
    last_tested_date: Optional[str] = None


class FarmCropContext(BaseModel):
    current_crop: Optional[str] = None
    target_crop: Optional[str] = None
    season: Optional[str] = None
    cropping_system: Optional[str] = None
    historical_crops: List[str] = Field(default_factory=list)


class FarmWaterContext(BaseModel):
    irrigation_available: bool = False
    irrigation_source: Optional[str] = None
    water_security_tier: str = "RAIN_DEPENDENT"


class FarmEnvironmentalContext(BaseModel):
    temperature_celsius: Optional[float] = None
    relative_humidity_percent: Optional[float] = None
    seasonal_rainfall_mm: Optional[float] = None
    weather_provider: str = "Open-Meteo REST API"


class UnifiedFarmProfile(BaseModel):
    """
    Country-neutral digital profile of an agricultural parcel.
    Serves as the canonical interchange entity across the AgriN platform.
    """
    farm_id: str
    farmer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    location: FarmLocation
    soil: FarmSoilContext
    crop: FarmCropContext
    water: FarmWaterContext
    environment: FarmEnvironmentalContext
    
    soil_health_summary: Optional[Dict[str, Any]] = None
    crop_health_summary: Optional[Dict[str, Any]] = None
    resilience_summary: Optional[Dict[str, Any]] = None
    active_advisories: List[Dict[str, Any]] = Field(default_factory=list)
    historical_observations_count: int = 0
