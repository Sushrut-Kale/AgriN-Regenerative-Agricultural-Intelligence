"""
AgriN Canonical Agricultural Data Model & Provenance Architecture
===================================================================
Establishes the country-neutral, interoperable canonical entities for:
- Farm Profile & Location
- Multi-Layer Observations:
  * SoilObservation (with units, test standard, depth, lab standard)
  * WeatherObservation (with NWP station, observation timestamp, units)
  * CropObservation (with FAO crop codes, season, planting date)
  * SatelliteObservation (with NDVI, NDWI, cloud cover, sensor, resolution)
  * DiseaseObservation (with AI screening confidence, image hash, triage)
- Advisory, Risk, and Confidence
- Provenance Chain:
  Observation -> Source -> Timestamp -> Provider -> Transformation -> Analysis -> Advisory
- Compact Farm-Level Intelligence Snapshot (Requirement 20)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid


class ProvenanceRecord(BaseModel):
    """Immutable audit trail for external and calculated agricultural observations."""
    source_name: str
    source_agency: str
    source_type: str = "OFFICIAL_REGISTRY"  # NWP, REMOTE_SENSING, LABORATORY, REGIONAL_STANDARD, SENSOR
    provider: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    geographic_precision: str = "DISTRICT"  # PARCEL, VILLAGE, SUB_DISTRICT, DISTRICT, PROVINCE
    original_units: Optional[Dict[str, str]] = None
    transformations_applied: List[str] = Field(default_factory=list)
    evidence_level: str = "HIGH"  # HIGH, MEDIUM, LOW


class CanonicalLocation(BaseModel):
    country_iso3: str = "IND"
    admin_level_1: str = Field(description="State/Province/Oblast")
    admin_level_2: str = Field(description="District/Municipality/County")
    sub_district: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    elevation_meters: Optional[float] = None
    agro_climatic_zone: Optional[str] = None


class CanonicalSoilObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs-soil-{uuid.uuid4().hex[:8]}")
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sampling_depth_cm: float = 15.0
    laboratory_standard: str = "ICAR_SHC_STANDARD"
    ph: Optional[float] = None
    organic_carbon_pct: Optional[float] = None
    electrical_conductivity_ds_m: Optional[float] = None
    nitrogen_kg_ha: Optional[float] = None
    phosphorus_kg_ha: Optional[float] = None
    potassium_kg_ha: Optional[float] = None
    soil_texture: Optional[str] = None
    provenance: Optional[ProvenanceRecord] = None


class CanonicalWeatherObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs-met-{uuid.uuid4().hex[:8]}")
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    temperature_celsius: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    rainfall_24h_mm: Optional[float] = None
    is_live_nwp: bool = True
    forecast_window_days: int = 7
    provenance: Optional[ProvenanceRecord] = None


class CanonicalSatelliteObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs-sat-{uuid.uuid4().hex[:8]}")
    observation_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provider: str = "Copernicus Sentinel-2"
    satellite: str = "Sentinel-2A"
    sensor: str = "MSI"
    spatial_resolution_meters: float = 10.0
    cloud_cover_pct: float = 0.0
    ndvi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    vegetation_status: str = "UNLINKED"  # VIGOROUS, MODERATE, STRESSED, SPARSE, UNLINKED
    data_quality: str = "HIGH"
    is_synthetic: bool = False
    provenance: Optional[ProvenanceRecord] = None


class CanonicalDiseaseObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs-dis-{uuid.uuid4().hex[:8]}")
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    crop: str
    condition_detected: str = "NO_SYMPTOMS_DETECTED"
    screening_confidence: float = 0.0
    triage_status: str = "SCREENING_ONLY"  # SCREENING_ONLY, REVIEW_REQUIRED, CONFIRMED_SAMPLE
    model_version: str = "MobileNetV4-PlantPathology-v1.0"
    model_deployed: bool = False
    is_synthetic: bool = False
    limitations: List[str] = Field(default_factory=list)
    provenance: Optional[ProvenanceRecord] = None


class CanonicalWaterAvailability(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs-wat-{uuid.uuid4().hex[:8]}")
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    irrigation_available: bool = False
    water_source: Optional[str] = "rainfed"  # canal, tube_well, open_well, drip, sprinkler, rainfed
    seasonal_rainfall_mm: Optional[float] = None
    water_deficit_risk: str = "LOW"  # LOW, MODERATE, HIGH, SEVERE
    irrigation_capacity_m3_ha: Optional[float] = None
    provenance: Optional[ProvenanceRecord] = None


class CanonicalAdvisoryItem(BaseModel):
    advisory_id: str
    priority: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    recommendation: str
    reason: str
    trigger: str
    confidence: str = "HIGH"
    urgency: str = "SEASONAL"  # IMMEDIATE, SHORT_TERM, SEASONAL
    limitations: List[str] = Field(default_factory=list)


class FarmIntelligenceSnapshot(BaseModel):
    """
    Compact canonical snapshot passed between intelligence services and clients (Requirement 20).
    """
    snapshot_id: str = Field(default_factory=lambda: f"snap-{uuid.uuid4().hex[:10]}")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    farm_id: str
    is_demo: bool = False
    location: CanonicalLocation
    soil: Optional[CanonicalSoilObservation] = None
    weather: Optional[CanonicalWeatherObservation] = None
    water: Optional[CanonicalWaterAvailability] = None
    satellite: Optional[CanonicalSatelliteObservation] = None
    crop: Dict[str, Any] = Field(default_factory=dict)
    crop_health: Optional[CanonicalDiseaseObservation] = None
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[CanonicalAdvisoryItem] = Field(default_factory=list)
    resilience: Dict[str, Any] = Field(default_factory=dict)
    confidence: Dict[str, Any] = Field(default_factory=dict)
    data_quality: Dict[str, Any] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)

