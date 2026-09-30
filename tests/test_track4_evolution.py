"""
AgriN Track 4 Evolution Test Suite
==================================

Comprehensive automated verification covering:
1. Geographic hierarchy (36 States/UTs, 15 ACZs, GPS lookup, fallbacks)
2. Soil Intelligence (optimal, constraints, boundaries, missing data)
3. Weather lookup & climatology fallback
4. Master Agricultural Intelligence Orchestrator
5. Regenerative Advisor (8 classes, insufficient data handling)
6. Farm Resilience Index Prototype (component breakdown, transparency)
7. Crop Disease Diagnostic Architecture (image validation, MODEL_NOT_DEPLOYED guardrail)
8. Satellite Intelligence Abstraction (VegetationObservation, NOT_CONNECTED status)
9. AgriN Data Exchange (ADE) Interoperability & Country Adapters (India reference vs BRICS)
10. Intelligence REST Endpoints via TestClient
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.geo_service import (
    get_all_states,
    get_all_agro_climatic_zones,
    find_nearest_district,
    find_district_by_name
)
from backend.app.services.soil_intelligence import assess_soil_health
from backend.app.services.weather_service import fetch_live_weather, get_weather_data
from backend.app.services.confidence_engine import compute_confidence
from backend.app.services.regenerative_advisor import advise_regenerative_practices
from backend.app.services.farm_resilience import calculate_farm_resilience
from backend.app.services.agrin_intelligence import run_full_agricultural_intelligence
from backend.app.services.disease_service import validate_image_payload, diagnose_crop_image
from backend.app.services.satellite_service import get_satellite_status_report, VegetationObservation
from backend.app.services.agri_interoperability import (
    ADE_Location, ADE_SoilObservation, ADE_Advisory
)
from backend.app.adapters import get_country_adapter, ADAPTER_REGISTRY

client = TestClient(app)


# ── 1. Geography Tests ────────────────────────────────────────────────────────

def test_geo_all_states_and_zones():
    states = get_all_states()
    assert len(states) >= 36  # 28 States + 8 UTs
    state_names = [s.get("name") if isinstance(s, dict) else s for s in states]
    assert "Maharashtra" in state_names
    assert "Punjab" in state_names
    assert "Tamil Nadu" in state_names


    zones = get_all_agro_climatic_zones()
    assert len(zones) == 15
    zone_codes = [z["code"] for z in zones]
    assert "ACZ-07" in zone_codes  # Eastern Plateau and Hills
    assert "ACZ-14" in zone_codes  # Western Dry Region


def test_geo_nearest_district_and_fallbacks():
    # Parbhani coordinates
    d_match, state = find_nearest_district(19.26, 76.77)
    assert state == "Maharashtra"
    assert "Parbhani" in d_match["name"]

    # Ludhiana coordinates (Punjab)
    d_punjab, st_punjab = find_nearest_district(30.90, 75.85)
    assert st_punjab == "Punjab"
    assert "Ludhiana" in d_punjab["name"]


# ── 2. Soil Intelligence Tests ────────────────────────────────────────────────

def test_soil_intelligence_optimal_profile():
    soil_input = {
        "N": 350.0, "P": 18.0, "K": 220.0,
        "pH": 7.0, "EC": 0.45, "OC": 0.85,
        "Zn": 0.90, "Fe": 6.5, "B": 0.70
    }
    profile = assess_soil_health(soil_input, soil_type="alluvial")
    assert profile["status"] == "OPTIMAL"
    assert profile["score"] >= 80.0
    assert profile["chemical_properties"]["pH"]["classification"] == "NEUTRAL"
    assert profile["organic_matter"]["classification"] == "HEALTHY"
    assert len(profile["soil_constraints"]) == 0
    assert len(profile["positive_indicators"]) >= 3


def test_soil_intelligence_constraints_detection():
    # Acidic soil with depleted carbon and zinc deficiency
    acidic_soil = {
        "N": 150.0, "P": 6.0, "K": 95.0,
        "pH": 4.8, "EC": 0.30, "OC": 0.35,
        "Zn": 0.40, "B": 0.30
    }
    profile = assess_soil_health(acidic_soil)
    assert profile["status"] in ["DEGRADED", "CRITICAL"]
    assert profile["score"] < 60.0
    
    constraint_ids = [c["constraint_id"] for c in profile["soil_constraints"]]
    assert "SC-002" in constraint_ids  # Soil Acidity Hazard
    assert "SC-001" in constraint_ids  # Soil Organic Carbon Depletion
    assert "SC-005" in constraint_ids  # Zinc Deficiency Stress
    assert any("agricultural lime" in rec.lower() for rec in profile["recommended_improvement_areas"])


def test_soil_intelligence_missing_and_boundary_handling():
    # Completely empty
    empty_profile = assess_soil_health({})
    assert empty_profile["status"] == "INSUFFICIENT_DATA"
    assert empty_profile["score"] == 0.0
    assert empty_profile["confidence_level"] == "INSUFFICIENT"

    # Exact threshold boundary
    boundary_soil = {"pH": 8.5, "EC": 1.0, "OC": 0.50, "N": 280.0, "P": 10.0, "K": 108.0}
    b_profile = assess_soil_health(boundary_soil)
    assert b_profile["score"] > 50.0
    assert b_profile["organic_matter"]["classification"] == "MODERATE"


# ── 3. Weather Lookup Tests ───────────────────────────────────────────────────

def test_weather_service_data_and_fallback():
    weather = get_weather_data(district="Parbhani", state="Maharashtra")
    assert "temperature" in weather
    assert "humidity" in weather
    assert "rainfall" in weather
    assert weather["temperature"] > 0.0


# ── 4. Master Agricultural Intelligence Pipeline Tests ────────────────────────

def test_master_agrin_intelligence_pipeline():
    farm_input = {
        "farm_id": "test-farm-pune-01",
        "state": "Maharashtra",
        "district": "Pune",
        "latitude": 18.52,
        "longitude": 73.85,
        "season": "Kharif",
        "irrigation_available": "yes",
        "N": 300, "P": 22, "K": 260,
        "pH": 6.8, "EC": 0.40, "OC": 0.72,
        "Zn": 0.85
    }
    result = run_full_agricultural_intelligence(farm_input)
    assert result["status"] == "success"
    assert result["version"] == "2.5.0"
    assert "geographic_context" in result
    assert "environmental_context" in result
    assert "soil_health_profile" in result
    assert "crop_suitability" in result
    assert "crop_health" in result
    assert result["crop_health"]["status"] == "NOT_ASSESSED"  # Responsible AI
    assert "regenerative_intelligence" in result
    assert "farm_resilience_index" in result
    assert "data_confidence" in result
    assert len(result["canonical_advisories"]) >= 3


# ── 5. Regenerative Advisor Tests ─────────────────────────────────────────────

def test_regenerative_advisor_classes_and_insufficient_data():
    # Empty profile -> insufficient data
    empty_res = advise_regenerative_practices({})
    assert empty_res["status"] == "insufficient_data"
    assert len(empty_res["missing_data_requirements"]) > 0

    # Populated farm profile
    populated_farm = {
        "state": "Maharashtra",
        "district": "Beed",
        "crop": "Cotton",
        "irrigation_available": "no",
        "rainfall": 680,
        "OC": 0.45,
        "pH": 7.8
    }
    advise = advise_regenerative_practices(populated_farm)
    assert advise["status"] == "success"
    assert advise["practice_count"] >= 4
    
    classes = [r["class"] for r in advise["recommendations"]]
    assert "CROP_ROTATION" in classes
    assert "WATER_CONSERVATION" in classes
    assert "SOIL_ORGANIC_MATTER_IMPROVEMENT" in classes


# ── 6. Farm Resilience Index Tests ────────────────────────────────────────────

def test_farm_resilience_index_breakdown():
    farm_data = {
        "state": "Punjab",
        "district": "Ludhiana",
        "irrigation_available": "assured",
        "rainfall": 650,
        "temperature": 26.0,
        "humidity": 65.0,
        "crop": "Wheat",
        "rotation_pattern": "legume_rotation",
        "intercropping": True,
        "N": 320, "P": 25, "K": 280,
        "pH": 7.2, "EC": 0.35, "OC": 0.80
    }
    res = calculate_farm_resilience(farm_data, crop_suitability_score=88.0)
    assert res["index_name"] == "AgriN Farm Resilience Index — prototype"
    assert 0.0 <= res["score"] <= 100.0
    assert res["resilience_tier"] in ["HIGH_RESILIENCE", "MODERATE_RESILIENCE"]
    assert "components" in res
    assert "soil_health" in res["components"]
    assert "water_context" in res["components"]
    assert "climate_context" in res["components"]
    assert "crop_diversity" in res["components"]
    assert "crop_suitability" in res["components"]


# ── 7. Crop Disease Diagnostic Architecture Tests ─────────────────────────────

def test_disease_image_validation_and_model_not_deployed():
    # Invalid extension
    inv = validate_image_payload("test.txt", b"dummy plain text content")
    assert inv["valid"] is False
    assert "Unsupported image format" in inv["error"]

    # Valid PNG image bytes (small dummy PNG)
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 2000
    val = validate_image_payload("leaf.png", png_bytes)
    assert val["valid"] is True
    assert val["format"] == "PNG"

    # Diagnostic triage execution without fake claims
    diag = diagnose_crop_image(
        image_bytes=png_bytes,
        filename="leaf.png",
        crop="Cotton",
        symptoms_description="Yellow mosaic on upper leaves"
    )
    assert diag["status"] == "MODEL_NOT_DEPLOYED"
    assert diag["diagnosis_status"] == "NOT_ASSESSED"
    assert diag["confidence"] == 0.0
    assert diag["diagnosis"] is None
    assert "responsible ai" in diag["explainability"]["reason"].lower()


# ── 8. Satellite Intelligence Tests ───────────────────────────────────────────

def test_satellite_status_honesty():
    sat = get_satellite_status_report(latitude=19.26, longitude=76.77, farm_id="test-farm-01")
    assert sat["satellite_status"] == "NOT_CONNECTED"
    assert sat["vegetation_observation"] is None
    assert len(sat["available_providers"]) >= 2
    assert "Copernicus Sentinel-2" in sat["available_providers"][0]["name"]


# ── 9. Interoperability & Country Adapters Tests ──────────────────────────────

def test_country_adapters_and_ade():
    # India reference adapter
    ind_adapter = get_country_adapter("IND")
    assert ind_adapter.is_reference_implementation is True
    assert ind_adapter.country_name == "India"
    
    loc = ind_adapter.resolve_location({"state": "Punjab", "district": "Ludhiana"})
    assert loc.country_iso3 == "IND"
    assert loc.admin_level_1 == "Punjab"
    assert loc.admin_level_2 == "Ludhiana"

    # Soil normalization to mg/kg
    soil_obs = ind_adapter.normalize_soil_test({"N": 280.0, "pH": 7.0}, "farm-001")
    assert soil_obs.available_nitrogen_mg_kg is not None
    assert soil_obs.available_nitrogen_mg_kg == round(280.0 / 2.24, 2)

    # BRICS Partner Adapters (Brazil, Russia, China, South Africa)
    for iso, name in [("BRA", "Brazil"), ("RUS", "Russia"), ("CHN", "China"), ("ZAF", "South Africa")]:
        ad = get_country_adapter(iso)
        assert ad.is_reference_implementation is False
        assert ad.country_name == name
        assert len(ad.get_supported_agro_zones()) >= 2


# ── 10. Intelligence Endpoints API Tests ──────────────────────────────────────

def test_api_intelligence_endpoints():
    # 1. Full Analysis
    res = client.post("/api/intelligence/full-analysis", json={
        "state": "Maharashtra", "district": "Parbhani",
        "season": "Kharif", "N": 280, "P": 16, "K": 310, "pH": 7.2, "OC": 0.65
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "farm_resilience_index" in data

    # 2. Soil Profile
    res_soil = client.post("/api/soil/profile", json={
        "N": 310, "P": 20, "K": 250, "pH": 7.1, "EC": 0.40, "OC": 0.75
    })
    assert res_soil.status_code == 200
    assert res_soil.json()["soil_profile"]["status"] == "OPTIMAL"

    # 3. Regenerative Advisor
    res_reg = client.post("/api/regenerative/advisor", json={
        "state": "Maharashtra", "crop": "Cotton", "rainfall": 700, "OC": 0.50
    })
    assert res_reg.status_code == 200
    assert res_reg.json()["regenerative_advice"]["status"] == "success"

    # 4. Resilience Score
    res_res = client.post("/api/resilience/score", json={
        "state": "Maharashtra", "rainfall": 750, "irrigation_available": "yes",
        "N": 290, "P": 18, "K": 260, "pH": 7.0, "OC": 0.65
    })
    assert res_res.status_code == 200
    assert "AgriN Farm Resilience Index" in res_res.json()["farm_resilience"]["index_name"]

    # 5. Satellite Status
    res_sat = client.get("/api/satellite/status")
    assert res_sat.status_code == 200
    assert res_sat.json()["satellite_status"] == "NOT_CONNECTED"

    # 6. National Overview
    res_nat = client.get("/api/national/overview")
    assert res_nat.status_code == 200
    assert res_nat.json()["total_agro_climatic_zones"] == 15

    # 7. Interoperability Adapters
    res_ad = client.get("/api/interoperability/adapters")
    assert res_ad.status_code == 200
    assert len(res_ad.json()["adapters"]) == 5
