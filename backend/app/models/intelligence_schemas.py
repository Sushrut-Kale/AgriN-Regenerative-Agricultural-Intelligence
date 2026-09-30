"""
AgriN — Standard Agricultural Intelligence Schemas (Phase 2.5)
==============================================================

Provides standardized, extensible Pydantic schemas for:
- Data Confidence & Coverage (`DataConfidenceLevel`, `DataCoverage`, `DataResolution`)
- Data Provenance (`DataSourceMetadata`, `DataSourceType`)
- Time-Series Agricultural Observations (`FarmObservation`, `ObservationType`)
- Farm Health Snapshot (`FarmHealthSnapshot`)
- Standard Advisory Objects (`AgriculturalAdvisory`, `AdvisoryCategory`, `AdvisoryPriority`)
- Satellite Intelligence Architecture (`SatelliteObservation`, `SpectralIndex`)
- Crop Disease Diagnostic Architecture (`DiseaseObservation`, `DiagnosisStatus`)
- Farm Boundary GeoJSON & Point representation
- Farmer Advisory Feedback Loop
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── Enumerations ─────────────────────────────────────────────────────────────

class DataCoverage(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    BASIC = "BASIC"
    UNAVAILABLE = "UNAVAILABLE"


class DataConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DataResolution(str, Enum):
    POINT = "POINT"
    PARCEL = "PARCEL"
    VILLAGE = "VILLAGE"
    SUB_DISTRICT = "SUB_DISTRICT"
    DISTRICT = "DISTRICT"
    STATE = "STATE"
    NATIONAL = "NATIONAL"


class DataSourceType(str, Enum):
    GOVERNMENT = "GOVERNMENT"
    SATELLITE = "SATELLITE"
    WEATHER = "WEATHER"
    SOIL = "SOIL"
    ML_MODEL = "ML_MODEL"
    AGRONOMIC_RULE = "AGRONOMIC_RULE"
    FARMER_INPUT = "FARMER_INPUT"
    FIELD_OBSERVATION = "FIELD_OBSERVATION"


class ObservationType(str, Enum):
    SOIL = "SOIL"
    WEATHER = "WEATHER"
    CROP = "CROP"
    SATELLITE = "SATELLITE"
    DISEASE = "DISEASE"
    IRRIGATION = "IRRIGATION"
    FIELD_VISIT = "FIELD_VISIT"


class AdvisoryCategory(str, Enum):
    CROP_SELECTION = "CROP_SELECTION"
    SOIL_HEALTH = "SOIL_HEALTH"
    WATER_MANAGEMENT = "WATER_MANAGEMENT"
    WEATHER_RISK = "WEATHER_RISK"
    CROP_HEALTH = "CROP_HEALTH"
    DISEASE = "DISEASE"
    REGENERATIVE = "REGENERATIVE"
    IRRIGATION = "IRRIGATION"
    NUTRIENT = "NUTRIENT"
    HARVEST = "HARVEST"


class AdvisoryPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class SpectralIndex(str, Enum):
    NDVI = "NDVI"
    NDWI = "NDWI"
    EVI = "EVI"
    SAVI = "SAVI"


class DiagnosisStatus(str, Enum):
    NOT_ASSESSED = "NOT_ASSESSED"
    SUSPECTED = "SUSPECTED"
    LIKELY = "LIKELY"
    CONFIRMED = "CONFIRMED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class FeedbackActionStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_FOLLOWED = "partially_followed"
    NOT_APPLICABLE = "not_applicable"


class FeedbackOutcome(str, Enum):
    OUTCOME_POSITIVE = "outcome_positive"
    OUTCOME_NEGATIVE = "outcome_negative"
    UNKNOWN = "unknown"


# ── Data Provenance & Confidence Models ───────────────────────────────────────

class DataSourceMetadata(BaseModel):
    source_name: str
    source_type: DataSourceType
    source_url: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    coverage: DataCoverage = DataCoverage.PARTIAL
    resolution: DataResolution = DataResolution.DISTRICT
    license: Optional[str] = None


DataSourceMeta = DataSourceMetadata



class ConfidenceMetadata(BaseModel):
    confidence: Optional[float] = None
    confidence_level: DataConfidenceLevel = DataConfidenceLevel.UNKNOWN
    coverage: DataCoverage = DataCoverage.PARTIAL
    data_resolution: DataResolution = DataResolution.DISTRICT
    data_timestamp: Optional[datetime] = None
    sources: List[DataSourceMetadata] = []


# ── Farm Boundary Model (Point & Polygon GeoJSON) ─────────────────────────────

class FarmBoundary(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    boundary_geojson: Optional[Dict[str, Any]] = None
    area_hectares: Optional[float] = Field(None, ge=0.0)
    crs: str = "EPSG:4326 (WGS84)"


# ── Farm Observation Models (Time-Series) ────────────────────────────────────

class FarmObservationCreate(BaseModel):
    farm_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    observation_type: ObservationType
    parameter_name: str
    value: float
    unit: str
    source: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class FarmObservationResponse(FarmObservationCreate):
    observation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Satellite Observation Architecture Model ──────────────────────────────────

class SatelliteObservation(BaseModel):
    farm_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    satellite: str = "Sentinel-2"
    sensor: str = "MSI"
    band: Optional[str] = None
    index: SpectralIndex
    value: Optional[float] = None
    resolution_meters: float = 10.0
    cloud_cover_percentage: Optional[float] = None
    source: str = "Copernicus Open Access Hub / Google Earth Engine (Planned)"
    status: str = "UNAVAILABLE"
    data_confidence: ConfidenceMetadata = Field(
        default_factory=lambda: ConfidenceMetadata(
            confidence_level=DataConfidenceLevel.UNKNOWN,
            coverage=DataCoverage.UNAVAILABLE,
            data_resolution=DataResolution.PARCEL
        )
    )


# ── Crop Disease Diagnostic Architecture Model ────────────────────────────────

class DiseaseObservation(BaseModel):
    farm_id: str
    crop: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_reference: Optional[str] = None
    symptoms: List[str] = []
    location: Optional[Dict[str, float]] = None
    model_prediction: Optional[str] = None
    confidence: Optional[float] = None
    diagnosis_status: DiagnosisStatus = DiagnosisStatus.NOT_ASSESSED
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    data_confidence: ConfidenceMetadata = Field(
        default_factory=lambda: ConfidenceMetadata(
            confidence_level=DataConfidenceLevel.UNKNOWN,
            coverage=DataCoverage.UNAVAILABLE,
            data_resolution=DataResolution.POINT
        )
    )


# ── Farm Health Snapshot Model ────────────────────────────────────────────────

class FarmHealthSnapshot(BaseModel):
    farm_id: str
    soil_health: Optional[Dict[str, Any]] = None
    water_status: Optional[Dict[str, Any]] = None
    crop_health: Optional[Dict[str, Any]] = None
    weather_risk: Optional[Dict[str, Any]] = None
    disease_risk: Optional[Dict[str, Any]] = None  # None when not assessed
    vegetation_health: Optional[Dict[str, Any]] = None  # None when satellite unavailable
    regenerative_score: Optional[Dict[str, Any]] = None
    overall_confidence: ConfidenceMetadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Standard Advisory Object Model ────────────────────────────────────────────

class AgriculturalAdvisory(BaseModel):
    advisory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farm_id: str
    category: AdvisoryCategory
    priority: AdvisoryPriority = AdvisoryPriority.MEDIUM
    title: str
    recommendation: str
    reasoning: List[str] = []
    supporting_observations: List[Dict[str, Any]] = []
    actions: List[str] = []
    confidence: ConfidenceMetadata
    data_sources: List[DataSourceMetadata] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


# ── Advisory Feedback Loop Model ─────────────────────────────────────────────

class AdvisoryFeedbackInput(BaseModel):
    advisory_id: str
    farm_id: str
    action_taken: FeedbackActionStatus
    outcome: FeedbackOutcome = FeedbackOutcome.UNKNOWN
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
