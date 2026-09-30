"""
AgriN — Phase 2.5 Hardening Test Suite
=====================================

Validates:
1. Data Confidence & Provenance Framework
2. Time-Series Farm Observation Model (SOIL, WEATHER, CROP)
3. Farm Health Snapshot Generation (honest UNAVAILABLE states for satellite/disease)
4. Standard Agricultural Advisory Synthesis & Decoupling of ML from Truth
5. Regenerative Agriculture Knowledge Base & Recommendation Engine
6. Farm Boundary GeoJSON & Area Support
7. Farmer Advisory Feedback Loop
8. Data Sources & System Coverage APIs
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.db import init_db, SessionLocal, FarmObservationRecord, AdvisoryRecord
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
    FarmBoundary,
    FarmObservationCreate,
    SatelliteObservation,
    DiseaseObservation,
    FarmHealthSnapshot,
    AgriculturalAdvisory,
)
from backend.app.services.regenerative_service import (
    load_practices, evaluate_practice_suitability,
    compute_regenerative_indicators, generate_regenerative_advisories
)
from backend.app.services.farm_health_service import build_farm_health_snapshot
from backend.app.services.advisory_service import (
    generate_crop_selection_advisory,
    generate_soil_health_advisory,
    generate_comprehensive_advisories
)


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c


# ── 1. Data Confidence & Provenance Tests ─────────────────────────────────────

def test_data_confidence_enums():
    """Verify confidence, coverage, and resolution enums are standardized."""
    assert DataCoverage.FULL.value == "FULL"
    assert DataCoverage.PARTIAL.value == "PARTIAL"
    assert DataCoverage.UNAVAILABLE.value == "UNAVAILABLE"

    assert DataConfidenceLevel.HIGH.value == "HIGH"
    assert DataConfidenceLevel.MEDIUM.value == "MEDIUM"
    assert DataConfidenceLevel.LOW.value == "LOW"
    assert DataConfidenceLevel.UNKNOWN.value == "UNKNOWN"

    assert DataResolution.POINT.value == "POINT"
    assert DataResolution.PARCEL.value == "PARCEL"
    assert DataResolution.DISTRICT.value == "DISTRICT"


def test_satellite_and_disease_schemas_honest_defaults():
    """Verify satellite and disease schemas enforce honest UNAVAILABLE baseline."""
    sat_obs = SatelliteObservation(
        farm_id="farm-test-1",
        timestamp=datetime.utcnow(),
        latitude=19.26,
        longitude=76.77,
        index=SpectralIndex.NDVI
    )
    assert sat_obs.status == "UNAVAILABLE"
    assert sat_obs.value is None
    assert sat_obs.data_confidence.coverage == DataCoverage.UNAVAILABLE

    dis_obs = DiseaseObservation(
        farm_id="farm-test-1",
        crop="Cotton",
        diagnosis_status=DiagnosisStatus.NOT_ASSESSED
    )
    assert dis_obs.diagnosis_status == DiagnosisStatus.NOT_ASSESSED
    assert dis_obs.confidence is None
    assert dis_obs.data_confidence.coverage == DataCoverage.UNAVAILABLE


# ── 2. Farm Boundary Tests (Point & GeoJSON) ──────────────────────────────────

def test_farm_boundary_point_and_polygon():
    """Verify farm boundary supports point and optional GeoJSON polygon."""
    point_boundary = FarmBoundary(latitude=19.26, longitude=76.77, area_hectares=2.5)
    assert point_boundary.latitude == 19.26
    assert point_boundary.longitude == 76.77
    assert point_boundary.boundary_geojson is None

    poly_geojson = {
        "type": "Polygon",
        "coordinates": [[[76.76, 19.25], [76.78, 19.25], [76.78, 19.27], [76.76, 19.27], [76.76, 19.25]]]
    }
    polygon_boundary = FarmBoundary(
        latitude=19.26,
        longitude=76.77,
        area_hectares=4.8,
        boundary_geojson=poly_geojson
    )
    assert polygon_boundary.boundary_geojson["type"] == "Polygon"
    assert len(polygon_boundary.boundary_geojson["coordinates"][0]) == 5


# ── 3. Time-Series Farm Observation Tests ────────────────────────────────────

def test_time_series_observation_api(client):
    """Test creating and retrieving time-series observations via API."""
    farm_id = "test-farm-observation-123"

    # Post SOIL observation
    soil_payload = {
        "farm_id": farm_id,
        "observation_type": "SOIL",
        "parameter_name": "available_nitrogen",
        "value": 185.5,
        "unit": "kg/ha",
        "source": "Soil Health Card Lab #402",
        "latitude": 19.26,
        "longitude": 76.77,
        "confidence": 0.95,
        "metadata": {"depth_cm": "0-15"}
    }
    resp1 = client.post(f"/api/farms/{farm_id}/observations", json=soil_payload)
    assert resp1.status_code == 200, resp1.text
    data1 = resp1.json()
    assert data1["observation_id"].startswith("obs-")
    assert data1["parameter_name"] == "available_nitrogen"
    assert data1["value"] == 185.5

    # Post WEATHER observation
    weather_payload = {
        "farm_id": farm_id,
        "observation_type": "WEATHER",
        "parameter_name": "precipitation",
        "value": 24.5,
        "unit": "mm",
        "source": "On-Farm Rain Gauge",
        "latitude": 19.26,
        "longitude": 76.77,
        "confidence": 0.90
    }
    resp2 = client.post(f"/api/farms/{farm_id}/observations", json=weather_payload)
    assert resp2.status_code == 200

    # Query observations back
    query_resp = client.get(f"/api/farms/{farm_id}/observations")
    assert query_resp.status_code == 200
    qdata = query_resp.json()
    assert qdata["total_observations"] >= 2
    types = [o["observation_type"] for o in qdata["observations"]]
    assert "SOIL" in types
    assert "WEATHER" in types


# ── 4. Farm Health Snapshot Tests (Honest Baseline) ───────────────────────────

def test_farm_health_snapshot_honesty():
    """Verify FarmHealthSnapshot populates real data and strictly leaves unmeasured fields UNAVAILABLE."""
    farm_data = {"state": "Maharashtra", "district": "Parbhani", "irrigation_available": "no", "soil_type": "Black"}
    soil_data = {"N": 160.0, "P": 14.0, "K": 220.0, "ph": 7.6, "OC": 0.48}
    env_data = {"temperature": 28.5, "humidity": 58.0, "rainfall": 750.0}

    snapshot = build_farm_health_snapshot("test-snap-farm", farm_data, soil_data, env_data)

    # Real data populated
    assert snapshot.soil_health["status"] == "ASSESSED"
    assert snapshot.soil_health["parameters_reported"] == 5
    assert snapshot.water_status["status"] == "ASSESSED"
    assert snapshot.water_status["irrigation_available"] is False

    # Satellite vegetation metrics strictly UNAVAILABLE (no fake indices)
    assert snapshot.vegetation_health["status"] == "UNAVAILABLE"
    assert snapshot.vegetation_health["indices"]["NDVI"] is None
    assert snapshot.vegetation_health["indices"]["EVI"] is None

    # Disease risk strictly UNAVAILABLE
    assert snapshot.disease_risk["status"] == "UNAVAILABLE"
    assert snapshot.disease_risk["confirmed_pathogens"] == []

    # Overall confidence attached
    assert snapshot.overall_confidence.confidence_level in [DataConfidenceLevel.HIGH, DataConfidenceLevel.MEDIUM]


def test_farm_health_api(client):
    """Test POST /api/farms/{id}/health endpoint."""
    payload = {
        "farm_data": {"state": "Punjab", "district": "Ludhiana", "season": "rabi"},
        "soil_data": {"N": 210.0, "P": 18.0, "K": 180.0, "ph": 7.2, "OC": 0.62},
        "env_data": {"temperature": 18.0, "humidity": 65.0, "rainfall": 650.0}
    }
    resp = client.post("/api/farms/ludhiana-farm-01/health", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["farm_id"] == "ludhiana-farm-01"
    assert data["soil_health"]["status"] == "ASSESSED"
    assert data["vegetation_health"]["status"] == "UNAVAILABLE"


# ── 5. Regenerative Knowledge & Recommendation Engine Tests ───────────────────

def test_regenerative_practices_loaded():
    """Verify practices repository contains 10+ validated practices."""
    practices = load_practices()
    assert len(practices) >= 10
    ids = [p["practice_id"] for p in practices]
    assert "PRACTICE_CROP_ROTATION" in ids
    assert "PRACTICE_COVER_CROPS" in ids
    assert "PRACTICE_INM" in ids
    assert "PRACTICE_WATER_CONSERVATION" in ids
    assert "PRACTICE_BIOCHAR" in ids or "PRACTICE_SOIL_CARBON_BIOCHAR" in ids


def test_regenerative_practice_suitability_evaluation():
    """Test biophysical suitability scoring of practices."""
    farm_data = {"state": "Maharashtra", "district": "Parbhani", "irrigation_available": "no"}
    soil_data = {"OC": 0.40, "N": 150.0}  # Deficient in carbon and nitrogen
    env_data = {"rainfall": 750.0}

    practices = load_practices()
    rotation_p = next(p for p in practices if p["practice_id"] == "PRACTICE_CROP_ROTATION")
    eval_res = evaluate_practice_suitability(rotation_p, farm_data, soil_data, env_data, target_crop="cotton")

    # Should be highly recommended because low OC & low N trigger synergy
    assert eval_res["match_score"] >= 80.0
    assert eval_res["recommendation_tier"] == "Highly Recommended"
    assert any("Nitrogen" in r for r in eval_res["reasons"])
    assert any("organic carbon" in r for r in eval_res["reasons"])


def test_regenerative_recommend_api(client):
    """Test POST /api/regenerative/recommend API endpoint."""
    payload = {
        "farm_data": {"state": "Gujarat", "district": "Rajkot", "season": "kharif", "irrigation_available": "yes", "water_source": "drip"},
        "soil_data": {"N": 180.0, "P": 12.0, "K": 200.0, "ph": 7.8, "OC": 0.52},
        "env_data": {"temperature": 31.0, "humidity": 60.0, "rainfall": 600.0}
    }
    resp = client.post("/api/regenerative/recommend", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert len(data["ranked_practices"]) >= 5
    assert "regenerative_indicators" in data
    assert data["regenerative_indicators"]["water_conservation"]["status"].startswith("High")


# ── 6. Advisory Engine & ML Decoupling Tests ─────────────────────────────────

def test_crop_selection_advisory_decoupling():
    """Verify AgriculturalAdvisory cleanly separates ML score, rule score, and final recommendation."""
    crop_res = {
        "crop": "cotton",
        "common_name": "Cotton",
        "final_score": 82.5,
        "ml_score": 85.0,
        "rule_score": 80.0,
        "classification": "Highly Suitable",
        "data_confidence": "High",
        "hard_gate_multiplier": 1.0,
        "supporting_factors": [{"factor": "Potassium", "note": "Adequate K"}],
        "limiting_factors": []
    }
    farm_data = {"state": "Maharashtra", "district": "Parbhani", "season": "kharif"}
    soil_data = {"ph": 7.4, "N": 210.0, "P": 18.0, "K": 240.0}
    env_data = {"rainfall": 750.0}

    advisory = generate_crop_selection_advisory(crop_res, farm_data, soil_data, env_data)

    assert advisory.category == AdvisoryCategory.CROP_SELECTION
    assert advisory.priority == AdvisoryPriority.HIGH
    assert advisory.confidence.confidence_level == DataConfidenceLevel.HIGH
    # Verify ML is explicitly acknowledged as probability evidence, not sole truth
    assert any("[ML Model Prediction]" in r for r in advisory.reasoning)
    assert any("[Agronomic Rule Evaluation]" in r for r in advisory.reasoning)
    assert any("[Regional Calendar]" in r for r in advisory.reasoning)


def test_farm_advisories_generation_api(client):
    """Test POST /api/farms/{id}/advisories endpoint."""
    payload = {
        "farm_data": {"state": "Karnataka", "district": "Dharwad", "season": "kharif"},
        "soil_data": {"N": 200.0, "P": 15.0, "K": 210.0, "ph": 6.8, "OC": 0.65},
        "env_data": {"temperature": 27.0, "humidity": 65.0, "rainfall": 820.0}
    }
    resp = client.post("/api/farms/dharwad-farm-01/advisories", json=payload)
    assert resp.status_code == 200, resp.text
    advisories = resp.json()
    assert len(advisories) >= 2
    categories = [a["category"] for a in advisories]
    assert "CROP_SELECTION" in categories
    assert "REGENERATIVE" in categories


# ── 7. Farmer Advisory Feedback Loop Tests ───────────────────────────────────

def test_advisory_feedback_submission(client):
    """Test submitting farmer feedback for an advisory."""
    feedback_payload = {
        "advisory_id": "adv-crop-sample-001",
        "farm_id": "farm-parbhani-99",
        "action_taken": "accepted",
        "outcome": "outcome_positive",
        "notes": "Followed legume rotation with Chickpea; soil nitrogen noticeably improved next season."
    }
    resp = client.post("/api/advisory/feedback", json=feedback_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert "feedback_id" in data


# ── 8. Data Sources & System Coverage API Tests ──────────────────────────────

def test_data_sources_api(client):
    """Verify /api/data-sources catalog returns legitimate sources with provenance."""
    resp = client.get("/api/data-sources")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_sources"] >= 5
    source_names = [s["source_name"] for s in data["data_sources"]]
    assert any("Open-Meteo" in name for name in source_names)
    assert any("ICAR" in name for name in source_names)
    assert any("Soil Health Card" in name for name in source_names)
    assert any("Sentinel-2" in name for name in source_names)


def test_system_coverage_api(client):
    """Verify /api/coverage returns accurate national scope."""
    resp = client.get("/api/coverage")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["geographic_coverage"]["states_covered"] == 28
    assert data["geographic_coverage"]["union_territories_covered"] == 8
    assert data["agronomic_coverage"]["crops_profiled"] == 23
    assert data["agronomic_coverage"]["regenerative_practices_cataloged"] >= 10
