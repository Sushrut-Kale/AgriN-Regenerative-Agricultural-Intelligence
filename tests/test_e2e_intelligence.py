"""
AgriN End-to-End Comprehensive Intelligence Pipeline Tests (Phase 20)
Validates:
- Complete execution path from farm input to API response across 7 target states:
  * Maharashtra
  * Punjab
  * Rajasthan
  * Kerala
  * Tamil Nadu
  * Assam
  * Karnataka
- Verification of unified schema (11 canonical response blocks)
- Actionable soil constraints connected to regenerative advisory
- Multifactorial crop suitability scoring with sub-compatibility breakdown
- Decoupled biophysical resilience vs data confidence
- 5-pillar explainability (WHAT, WHY, BASED ON, CONFIDENCE, LIMITATIONS)
- Graceful degradation under weather API failures, incomplete soil data, disconnected satellite/disease models
- Multi-observation farm history and farmer feedback loops
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.agrin_intelligence import run_full_agricultural_intelligence
from backend.app.services.satellite_service import get_observation
from backend.app.services.disease_service import diagnose_crop_image

client = TestClient(app)

REGIONAL_TEST_FARMS = [
    {
        "state": "Maharashtra",
        "district": "Parbhani",
        "season": "kharif",
        "target_crop": "cotton",
        "soil_type": "black",
        "irrigation_available": "no",
        "nitrogen": 120.0,
        "phosphorus": 25.0,
        "potassium": 220.0,
        "ph": 7.8,
        "organic_carbon": 0.45,
        "electrical_conductivity": 0.6
    },
    {
        "state": "Punjab",
        "district": "Ludhiana",
        "season": "rabi",
        "target_crop": "wheat",
        "soil_type": "alluvial",
        "irrigation_available": "yes",
        "nitrogen": 220.0,
        "phosphorus": 45.0,
        "potassium": 260.0,
        "ph": 7.4,
        "organic_carbon": 0.52,
        "electrical_conductivity": 0.4
    },
    {
        "state": "Rajasthan",
        "district": "Jodhpur",
        "season": "kharif",
        "target_crop": "mothbeans",
        "soil_type": "sandy",
        "irrigation_available": "no",
        "nitrogen": 90.0,
        "phosphorus": 14.0,
        "potassium": 150.0,
        "ph": 8.3,
        "organic_carbon": 0.24,
        "electrical_conductivity": 2.3  # Elevated salinity
    },
    {
        "state": "Kerala",
        "district": "Wayanad",
        "season": "kharif",
        "target_crop": "rice",
        "soil_type": "laterite",
        "irrigation_available": "yes",
        "nitrogen": 175.0,
        "phosphorus": 20.0,
        "potassium": 180.0,
        "ph": 5.2,  # Acidic
        "organic_carbon": 1.40,
        "electrical_conductivity": 0.3
    },
    {
        "state": "Tamil Nadu",
        "district": "Thanjavur",
        "season": "kharif",
        "target_crop": "rice",
        "soil_type": "alluvial",
        "irrigation_available": "yes",
        "nitrogen": 190.0,
        "phosphorus": 30.0,
        "potassium": 210.0,
        "ph": 7.1,
        "organic_carbon": 0.65,
        "electrical_conductivity": 0.5
    },
    {
        "state": "Assam",
        "district": "Jorhat",
        "season": "kharif",
        "target_crop": "rice",
        "soil_type": "alluvial",
        "irrigation_available": "no",
        "nitrogen": 160.0,
        "phosphorus": 22.0,
        "potassium": 195.0,
        "ph": 5.4,
        "organic_carbon": 1.10,
        "electrical_conductivity": 0.25
    },
    {
        "state": "Karnataka",
        "district": "Dharwad",
        "season": "rabi",
        "target_crop": "chickpea",
        "soil_type": "black",
        "irrigation_available": "no",
        "nitrogen": 110.0,
        "phosphorus": 28.0,
        "potassium": 240.0,
        "ph": 7.6,
        "organic_carbon": 0.48,
        "electrical_conductivity": 0.5
    }
]

def test_unified_pipeline_across_all_seven_regions():
    """Validates end-to-end execution across Maharashtra, Punjab, Rajasthan, Kerala, Tamil Nadu, Assam, Karnataka."""
    for farm in REGIONAL_TEST_FARMS:
        res = run_full_agricultural_intelligence(farm)

        # 1. Canonical Schema Verification
        assert "farm_context" in res
        assert "location_context" in res
        assert "weather_context" in res
        assert "soil_health" in res
        assert "crop_suitability" in res
        assert "regenerative_opportunities" in res
        assert "farm_resilience" in res
        assert "confidence" in res
        assert "explanation" in res
        assert "data_sources" in res
        assert "limitations" in res

        # 2. Location Resolution
        assert res["location_context"]["district"].lower() == farm["district"].lower()
        assert res["location_context"]["state"].lower() == farm["state"].lower()

        # 3. Crop Suitability Output Quality
        assert len(res["crop_suitability"]) > 0
        top_crop = res["crop_suitability"][0]
        assert "overall_score" in top_crop
        assert "soil_compatibility" in top_crop
        assert "weather_compatibility" in top_crop
        assert "season_compatibility" in top_crop
        assert "location_compatibility" in top_crop
        assert "water_compatibility" in top_crop
        assert "risk_factors" in top_crop
        assert "reason" in top_crop
        assert "why" in top_crop["reason"]
        assert "considerations" in top_crop["reason"]
        assert "confidence" in top_crop["reason"]

        # 4. Decoupled Farm Resilience
        assert "agricultural_resilience" in res["farm_resilience"]
        assert "data_confidence" in res["farm_resilience"]
        assert res["farm_resilience"]["score"] > 0
        assert res["confidence"]["confidence_score"] > 0

        # 5. Explainability 5-Pillar Structure
        exp = res["explanation"]
        assert "what" in exp and len(exp["what"]) > 0
        assert "why" in exp and len(exp["why"]) > 0
        assert "based_on" in exp and len(exp["based_on"]) > 0
        assert "confidence" in exp and len(exp["confidence"]) > 0
        assert "limitations" in exp

def test_api_analyze_endpoint_e2e():
    """Validates /api/analyze endpoint with a live FastAPI client for a complete farm."""
    payload = {
        "farm_data": {
            "state": "Maharashtra",
            "district": "Parbhani",
            "season": "kharif",
            "soil_type": "black",
            "irrigation_available": "no",
            "water_source": "borewell"
        },
        "soil_data": {
            "N": 130.0,
            "P": 24.0,
            "K": 210.0,
            "ph": 7.9,
            "OC": 0.44
        },
        "env_data": {
            "temperature": 29.0,
            "humidity": 65.0,
            "rainfall": 120.0
        }
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Preserves backward compatibility
    assert data["success"] is True
    assert "session_id" in data
    assert "ranked_crops" in data
    assert len(data["ranked_crops"]) == 10
    assert "recommendation_explanation" in data

    # Contains new unified Phase 3 fields
    assert "soil_health" in data
    assert "regenerative_opportunities" in data
    assert "farm_resilience" in data
    assert "confidence" in data
    assert "explanation" in data

def test_graceful_degradation_weather_api_failure():
    """When weather API raises an exception, system falls back to climatology and adds limitation."""
    farm = {
        "state": "Maharashtra",
        "district": "Parbhani",
        "season": "kharif"
    }
    with patch("backend.app.services.agrin_intelligence.get_weather_data", side_effect=Exception("Timeout connecting to weather provider")), \
         patch("backend.app.services.agrin_intelligence.get_weather_forecast", side_effect=Exception("Backup failed")):
        res = run_full_agricultural_intelligence(farm)
        assert res["weather_context"]["is_live"] is False
        assert any("weather" in lim.lower() for lim in res["limitations"])
        assert len(res["crop_suitability"]) > 0

def test_graceful_degradation_incomplete_soil_data():
    """Incomplete soil data executes cleanly with reduced confidence assessment."""
    farm = {
        "state": "Punjab",
        "district": "Ludhiana",
        "season": "rabi"
        # Zero N, P, K, pH, OC provided
    }
    res = run_full_agricultural_intelligence(farm)
    assert res["confidence"]["confidence_level"] in ["LOW", "MEDIUM"]
    assert len(res["confidence"]["metadata"]["missing_core_fields"]) >= 3
    assert len(res["crop_suitability"]) > 0

def test_honest_satellite_and_disease_guardrails():
    """Ensures satellite and disease diagnostic abstractions do not fabricate predictions."""
    sat_obs = get_observation(19.26, 76.77, "2026-09-01", "2026-09-30")
    assert sat_obs["status"] == "NOT_CONNECTED"
    assert sat_obs["ndvi"] is None
    assert "disconnected" in sat_obs["message"].lower()

    # Image disease diagnostic guardrail (must be >= 1024 bytes)
    valid_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 2000
    diag = diagnose_crop_image(valid_png, "sample.png", "Cotton", "Leaf curl")
    assert diag["status"] == "MODEL_NOT_DEPLOYED"
    assert diag["diagnosis_status"] == "NOT_ASSESSED"
    assert diag["confidence"] == 0.0

def test_farm_history_and_feedback_flow():
    """Validates longitudinal farm history and farmer feedback recording."""
    # Test farm history for new farm (insufficient history)
    hist_resp = client.get("/api/farms/FARM-NEW-001/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["has_sufficient_history"] is False

    # Test farmer feedback submission (Phase 12)
    feedback_payload = {
        "session_id": "TEST-SESSION-E2E",
        "recommended_crop": "Cotton",
        "crop": "Cotton",
        "did_you_follow": "YES",
        "outcome": "Successful",
        "yield_observation": "16 quintals/acre",
        "disease_observation": "None",
        "free_text": "Cover crop recommendation noticeably conserved soil moisture."
    }
    fb_resp = client.post("/api/feedback", json=feedback_payload)
    assert fb_resp.status_code == 200
    fb_data = fb_resp.json()
    assert fb_data["success"] is True
    assert "feedback_id" in fb_data
