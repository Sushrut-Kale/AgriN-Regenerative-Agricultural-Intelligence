"""
AgriN Agricultural Interoperability Model
Defines normalized, country-neutral domain entities for the AgriN Data Exchange (ADE):
- Farm
- Farmer
- Location
- SoilObservation
- WeatherObservation
- CropObservation
- CropHealthObservation
- Advisory
- RegenerativePractice
- AgriculturalEvent

Standardized on SI units (°C, mm, hectares, mg/kg) and WGS84 coordinates.
Strictly decoupled from single-country administrative taxonomies.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from enum import Enum


class StandardUnit(str, Enum):
    CELSIUS = "degC"
    MILLIMETER = "mm"
    HECTARE = "ha"
    MILLIGRAM_PER_KILOGRAM = "mg/kg"
    DECISIEMENS_PER_METER = "dS/m"
    PERCENT = "%"
    TONNES_PER_HECTARE = "t/ha"


class ADE_Location(BaseModel):
    country_iso3: str = Field(description="ISO 3166-1 alpha-3 code (e.g. IND, BRA, ZAF, RUS, CHN)")
    admin_level_1: str = Field(description="First-order administrative subdivision (e.g. State, Province, Oblast)")
    admin_level_2: str = Field(description="Second-order administrative subdivision (e.g. District, County, Rayon)")
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    coordinate_reference_system: str = "EPSG:4326"  # WGS84
    parcel_boundary_wkt: Optional[str] = None
    elevation_meters: Optional[float] = None


class ADE_Farmer(BaseModel):
    farmer_uuid: str
    country_iso3: str
    anonymized_id: str
    preferred_language_iso639: str = "eng"


class ADE_Farm(BaseModel):
    farm_uuid: str
    farmer_uuid: str
    location: ADE_Location
    area_hectares: float = Field(gt=0.0)
    primary_agro_ecological_zone: Optional[str] = None
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ADE_SoilObservation(BaseModel):
    observation_id: str
    farm_uuid: str
    observed_at: datetime
    sampling_depth_cm: float = 15.0
    laboratory_standard: str = "ISO_17025"
    
    # Standard SI units: mg/kg (= ppm)
    ph_water: Optional[float] = None
    organic_carbon_percent: Optional[float] = None
    electrical_conductivity_ds_m: Optional[float] = None
    available_nitrogen_mg_kg: Optional[float] = None
    available_phosphorus_mg_kg: Optional[float] = None
    available_potassium_mg_kg: Optional[float] = None
    available_sulphur_mg_kg: Optional[float] = None
    available_zinc_mg_kg: Optional[float] = None
    available_iron_mg_kg: Optional[float] = None
    available_boron_mg_kg: Optional[float] = None


class ADE_WeatherObservation(BaseModel):
    observation_id: str
    farm_uuid: str
    observed_at: datetime
    temperature_celsius: float
    relative_humidity_percent: float
    precipitation_24h_mm: float
    solar_radiation_mj_m2: Optional[float] = None
    wind_speed_m_s: Optional[float] = None
    source_agency: str


class ADE_CropObservation(BaseModel):
    observation_id: str
    farm_uuid: str
    fao_crop_code: str
    botanical_name: str
    common_english_name: str
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    crop_stage: str = "VEGETATIVE"  # SOWING, VEGETATIVE, FLOWERING, GRAIN_FILLING, MATURITY, HARVESTED


class ADE_CropHealthObservation(BaseModel):
    observation_id: str
    farm_uuid: str
    observed_at: datetime
    pathogen_eppo_code: Optional[str] = None
    suspected_pathology: Optional[str] = None
    severity_percentage: float = 0.0
    triage_status: str = "NOT_ASSESSED"  # NOT_ASSESSED, SUSPECTED, LIKELY, CONFIRMED, REVIEW_REQUIRED
    diagnostic_method: str = "VISUAL_OBSERVATION"


class ADE_Advisory(BaseModel):
    advisory_id: str
    farm_uuid: str
    generated_at: datetime
    category: str
    urgency: str
    title: str
    recommendation_text: str
    scientific_basis: List[str]
    action_items: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    data_provenance_sources: List[str]


class ADE_RegenerativePractice(BaseModel):
    practice_id: str
    fao_practice_code: Optional[str] = None
    name: str
    practice_category: str
    target_carbon_impact: str
    target_water_impact: str
    implementation_complexity: str


class ADE_AgriculturalEvent(BaseModel):
    event_id: str
    farm_uuid: str
    event_timestamp: datetime
    event_type: str  # SOWING, FERTIGATION, RAINFALL_SURGE, PEST_INCIDENCE, HARVEST
    details: Dict[str, Any]
