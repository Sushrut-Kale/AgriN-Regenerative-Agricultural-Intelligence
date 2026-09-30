"""
FarmFriend AI — Pydantic Schemas
==================================

All request/response models for the FastAPI endpoints including Feedback schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Input Schemas ─────────────────────────────────────────────────────────────

class FarmDataInput(BaseModel):
    country: Optional[str] = "India"
    state: str = "Maharashtra"
    district: Optional[str] = "Parbhani"
    sub_district: Optional[str] = None  # Taluka / Tehsil / Block
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    agro_climatic_zone: Optional[str] = None
    season: Optional[str] = "kharif"  # kharif | rabi | summer | perennial
    farm_area: Optional[float] = None
    area_hectares: Optional[float] = None
    boundary_geojson: Optional[Dict[str, Any]] = None
    soil_type: Optional[str] = None
    irrigation_available: Optional[str] = "no"  # yes | no
    water_source: Optional[str] = None
    drainage: Optional[str] = None  # good | moderate | poor | unknown
    previous_crop: Optional[str] = None
    intent: Optional[str] = "seasonal_field_crop"  # seasonal_field_crop | perennial_horticulture | all



class SoilDataInput(BaseModel):
    # Macronutrients (kg/ha)
    N: Optional[float] = Field(None, ge=0, le=800, description="Available Nitrogen (kg/ha)")
    P: Optional[float] = Field(None, ge=0, le=300, description="Available Phosphorus (kg/ha)")
    K: Optional[float] = Field(None, ge=0, le=1200, description="Available Potassium (kg/ha)")
    # Secondary nutrient (ppm)
    S: Optional[float] = Field(None, ge=0, le=100, description="Available Sulphur (ppm)")
    # Micronutrients (ppm)
    Zn: Optional[float] = Field(None, ge=0, le=20, description="Available Zinc (ppm)")
    Fe: Optional[float] = Field(None, ge=0, le=100, description="Available Iron (ppm)")
    Cu: Optional[float] = Field(None, ge=0, le=20, description="Available Copper (ppm)")
    Mn: Optional[float] = Field(None, ge=0, le=50, description="Available Manganese (ppm)")
    B: Optional[float] = Field(None, ge=0, le=10, description="Available Boron (ppm)")
    # Chemical properties
    ph: Optional[float] = Field(None, ge=3.0, le=11.0, description="Soil pH")
    EC: Optional[float] = Field(None, ge=0, le=20, description="Electrical Conductivity (dS/m)")
    OC: Optional[float] = Field(None, ge=0, le=5, description="Organic Carbon (%)")


class EnvDataInput(BaseModel):
    temperature: Optional[float] = Field(None, ge=-5, le=50, description="Temperature (°C)")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Relative Humidity (%)")
    rainfall: Optional[float] = Field(None, ge=0, le=5000, description="Annual Rainfall (mm)")


class AnalysisRequest(BaseModel):
    farm_data: FarmDataInput
    soil_data: SoilDataInput
    env_data: EnvDataInput
    session_id: Optional[str] = None


class FeasibilityRequest(BaseModel):
    chosen_crop: str
    farm_data: FarmDataInput
    soil_data: SoilDataInput
    env_data: EnvDataInput
    session_id: Optional[str] = None


class WhatIfRequest(BaseModel):
    crop_name: str
    original_soil: SoilDataInput
    original_env: EnvDataInput
    farm_data: FarmDataInput
    simulated_changes: Dict[str, float]
    session_id: Optional[str] = None


class ExplainRequest(BaseModel):
    crop_result: Dict[str, Any]
    explanation_type: str = "crop_detail"  # crop_detail | recommendation | feasibility | whatif
    session_id: Optional[str] = None


class ExplainQARequest(BaseModel):
    question_type: str = "why_recommended"  # why_recommended | why_lower | whatif_hint
    crop_result: Dict[str, Any]
    context: Optional[Dict[str, Any]] = {}


class FeedbackInput(BaseModel):
    session_id: str
    analysis_id: Optional[str] = None
    recommended_crop: str
    selected_crop: Optional[str] = None
    suitability_score: Optional[float] = None
    rating: str  # 'helpful', 'not_helpful', 'partially'
    reason: Optional[str] = None
    free_text: Optional[str] = None
    outcome_status: Optional[str] = "not_yet_grown"  # 'not_yet_grown', 'growing', 'harvested'
    crop_performance: Optional[str] = None  # 'poor', 'average', 'good', 'excellent'
    actual_yield: Optional[float] = None
    yield_unit: Optional[str] = "quintals_per_ha"
    model_version: Optional[str] = "random_forest_v2"
    region: Optional[str] = None
    season: Optional[str] = None


# ── Factor Schema ─────────────────────────────────────────────────────────────

class Factor(BaseModel):
    factor: str
    status: str  # suitable | moderate | limiting | missing
    note: str
    score: Optional[float] = None


# ── Response Schemas ───────────────────────────────────────────────────────────

class CropResult(BaseModel):
    crop: str
    common_name: str
    local_name: Optional[str] = ""
    final_score: float
    ml_score: float
    rule_score: Optional[float] = None
    classification: str
    classification_color: str
    supporting_factors: List[Dict] = []
    limiting_factors: List[Dict] = []
    moderate_factors: List[Dict] = []
    missing_factors: List[Dict] = []
    data_confidence: str
    maharashtra_suitability: Optional[str] = None
    maharashtra_regions: List[str] = []
    category: Optional[str] = None
    rank: Optional[int] = None
    disclaimer: str


class AnalysisResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    ranked_crops: List[CropResult]
    model_info: Dict[str, Any]
    feature_importance: List[Dict]
    data_completeness: Dict[str, Any]
    recommendation_explanation: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FeasibilityResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    crop: str
    result: Dict[str, Any]
    feasibility_explanation: str
    summary_card: Dict[str, Any]
    feasibility_outcome: str
    feasibility_label: str
    feasibility_color: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WhatIfResponse(BaseModel):
    success: bool
    is_simulation: bool = True
    crop: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    changed_params: Dict[str, Any]
    score_change: float
    score_change_direction: str
    explanation: str
    disclaimer: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[Dict]
    warnings: List[Dict]


class ModelInfoResponse(BaseModel):
    model_version: Optional[str]
    model_type: Optional[str]
    training_date: Optional[str]
    metrics: Dict[str, Any]
    n_classes: Optional[int]
    all_models: List[Dict]
    feature_importance: List[Dict]


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalyticsResponse(BaseModel):
    total_analyses: int
    total_feasibility_checks: int
    total_whatif_runs: int
    top_recommended_crops: List[Dict]
    top_chosen_crops: List[Dict]
    score_distribution: Dict[str, int]
    district_distribution: List[Dict]
    season_distribution: List[Dict]
    model_info: Dict[str, Any]
    missing_data_stats: Dict[str, Any]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# ── Phase 2.5 Intelligence Schemas Re-Export ──────────────────────────────────
from backend.app.models.intelligence_schemas import (
    DataCoverage,
    DataConfidenceLevel,
    DataResolution,
    DataSourceType,
    ObservationType,
    AdvisoryCategory,
    AdvisoryPriority,
    SpectralIndex,
    DiagnosisStatus,
    FeedbackActionStatus,
    FeedbackOutcome,
    DataSourceMetadata,
    ConfidenceMetadata,
    FarmBoundary,
    FarmObservationCreate,
    FarmObservationResponse,
    SatelliteObservation,
    DiseaseObservation,
    FarmHealthSnapshot,
    AgriculturalAdvisory,
    AdvisoryFeedbackInput,
)
