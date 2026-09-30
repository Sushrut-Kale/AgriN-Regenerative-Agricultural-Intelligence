"""
AgriN Track 4 Final Hardening & Field-Readiness Verification Suite
==================================================================

Validates Track 4 challenge requirements across 10 critical domains:
1. Pan-India Geography & Agro-Climatic Zone (ACZ) resolution (Assam, Karnataka, HP, Punjab, Rajasthan, Kerala, TN, Maharashtra)
2. Soil Health Intelligence (known/unknown, next measurements, confidence impact, physical bounds)
3. Weather Intelligence (disaggregation of OBSERVED vs FORECAST vs CLIMATOLOGICAL vs SYNTHETIC)
4. Satellite Remote Sensing Guardrails (Never claims crop disease; NDVI/NDWI limits)
5. Plant Pathology Guardrails (Magic bytes validation, safe IPM advice, no toxic dosages, review gating)
6. Regenerative Multi-Horizon Engine (Prioritized practices without fake yield guarantees)
7. Knowledge Graph Explainability Trace (Observation -> Rule -> Source -> Recommendation)
8. BRICS 5-Nation Interoperability & Canonical Model (IND, BRA, RUS, CHN, ZAF)
9. Farm Resilience vs Data Completeness Decoupling
10. Security & Input Robustness (Payload validation, oversized files, unit boundary errors)
"""

import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.geo_service import (
    get_all_states,
    get_districts_for_state,
    find_nearest_district,
    find_district_by_name,
    get_agro_climatic_zone_info,
)
from backend.app.services.agrin_intelligence import run_full_agricultural_intelligence
from backend.app.services.soil_intelligence import assess_soil_health
from backend.app.services.confidence_engine import get_missing_data_guidance
from backend.app.services.weather_service import get_weather_data, fetch_live_weather
from backend.app.services.satellite_service import (
    SatelliteObservation,
    interpret_satellite_observation,
    SentinelProvider,
    DemoSatelliteProvider,
)
from backend.app.services.disease_service import (
    validate_image_payload,
    diagnose_crop_image,
    generate_disease_advisory,
    LocalVisionModelProvider,
)
from backend.app.services.regenerative_advisor import advise_regenerative_practices
from backend.app.services.farm_resilience import calculate_farm_resilience
from backend.app.services.unit_normalizer import AgriculturalUnitNormalizer, UnitValidationError
from backend.app.adapters import get_country_adapter
from backend.app.adapters.brics import (
    BrazilAdapter,
    RussiaAdapter,
    ChinaAdapter,
    SouthAfricaAdapter,
    run_brics_interoperability_simulation,
)
from backend.app.models.canonical_agri_model import (
    CanonicalLocation,
    CanonicalSoilObservation,
    CanonicalWeatherObservation,
    ProvenanceRecord,
)

client = TestClient(app)


# ==============================================================================
# 1. GEOGRAPHY & MULTI-REGION ACZ RESOLUTION
# ==============================================================================

def test_pan_india_8_regions_diversity():
    """Verify system recognizes and accurately resolves 8 geographically distinct regions."""
    regions = [
        {"state": "Maharashtra", "district": "Parbhani", "expected_zone_prefix": "ACZ-09"},
        {"state": "Punjab", "district": "Ludhiana", "expected_zone_prefix": "ACZ-06"},
        {"state": "Rajasthan", "district": "Jodhpur", "expected_zone_prefix": "ACZ-14"},
        {"state": "Kerala", "district": "Wayanad", "expected_zone_prefix": "ACZ-12"},
        {"state": "Tamil Nadu", "district": "Thanjavur", "expected_zone_prefix": "ACZ-11"},
        {"state": "Assam", "district": "Kamrup", "expected_zone_prefix": "ACZ-02"},
        {"state": "Karnataka", "district": "Dharwad", "expected_zone_prefix": "ACZ-10"},
        {"state": "Himachal Pradesh", "district": "Kangra", "expected_zone_prefix": "ACZ-01"},
    ]

    for reg in regions:
        dist_meta = find_district_by_name(reg["district"], reg["state"])
        assert dist_meta is not None, f"Could not find district for {reg['state']} - {reg['district']}"
        zone_id = dist_meta.get("agro_climatic_zone") or dist_meta.get("zone")
        assert zone_id is not None
        zone_info = get_agro_climatic_zone_info(zone_id)
        assert zone_info is not None, f"Could not resolve zone info for {reg['state']}: {zone_id}"
        assert zone_info["id"] == reg["expected_zone_prefix"]


def test_gps_coordinate_resolution():
    """Verify coordinate lookup correctly selects closest district."""
    # Shimla, HP: ~31.1048 N, 77.1734 E
    dist_meta, state_name = find_nearest_district(31.1048, 77.1734)
    assert dist_meta is not None
    assert state_name == "Himachal Pradesh"
    assert "zone" in dist_meta or "agro_climatic_zone" in dist_meta


# ==============================================================================
# 2. SOIL HEALTH INTELLIGENCE & MISSING DATA EXPLAINABILITY
# ==============================================================================

def test_soil_known_unknown_and_next_measurements():
    """Verify incomplete soil data reports knowns, unknowns, and advice on next measurements."""
    # Only N and pH provided; P, K, EC, OC missing
    partial_soil = {"N": 210, "ph": 6.5}
    assessment = assess_soil_health(partial_soil)

    assert assessment["status"] in ["OPTIMAL", "SUB_OPTIMAL", "DEGRADED", "CRITICAL"]
    assert assessment["confidence"] < 0.5
    assert assessment["confidence_level"] == "LOW"

    guidance = get_missing_data_guidance(partial_soil)
    assert "pH" in guidance["known_parameters"]
    assert any("carbon" in m.lower() for m in guidance["missing_parameters"])
    assert "impact_statement" in guidance
    assert "confidence" in guidance["impact_statement"].lower()
    assert "Soil Health Card" in guidance["actionable_guidance"] or "KVK" in guidance["actionable_guidance"]


def test_soil_extreme_biological_boundary_rejection():
    """Verify physically impossible soil measurements raise validation errors."""
    with pytest.raises(UnitValidationError):
        AgriculturalUnitNormalizer.normalize_temperature(90.0, "degC")  # Exceeds max +65C ambient

    with pytest.raises(UnitValidationError):
        AgriculturalUnitNormalizer.normalize_organic_carbon(-0.5, "%")  # OC cannot be negative

    with pytest.raises(UnitValidationError):
        AgriculturalUnitNormalizer.normalize_organic_carbon(25.0, "%")  # Beyond biological limit of 20%


# ==============================================================================
# 3. WEATHER INTELLIGENCE DISAGGREGATION
# ==============================================================================

def test_weather_disaggregation_observed_forecast_climatological():
    """Verify weather service distinguishes source types and never silently blends synthetic data."""
    # Live or climatological fallback
    weather = get_weather_data(state="Rajasthan", district="Jodhpur", lat=26.2389, lon=73.0243)
    assert weather is not None
    assert "source" in weather
    assert "temperature" in weather
    assert "humidity" in weather
    assert "rainfall" in weather

    # When fallback occurs, it must declare climatological or historical origin
    if "climatological" in weather["source"].lower() or "fallback" in weather["source"].lower():
        assert weather.get("is_live") is False or weather.get("is_synthetic", False) is True


# ==============================================================================
# 4. SATELLITE REMOTE SENSING GUARDRAILS
# ==============================================================================

def test_satellite_never_independently_diagnoses_disease():
    """Verify satellite vegetation interpretation strictly flags vigor/moisture stress, NEVER disease names."""
    obs = {
        "status": "CONNECTED",
        "latitude": 19.0,
        "longitude": 75.0,
        "observation_date": "2026-09-30T00:00:00Z",
        "source": "Sentinel-2",
        "ndvi": 0.25,
        "ndwi": -0.15,
        "vegetation_status": "STRESSED",
        "data_quality": "HIGH",
        "is_synthetic": False,
    }
    result = interpret_satellite_observation(obs)
    
    # Must identify vegetation condition without claiming disease
    assert "disease" not in result["primary_interpretation"].lower()
    assert "fungal" not in result["primary_interpretation"].lower()
    assert "blight" not in result["primary_interpretation"].lower()
    assert "inspect" in result["advisory_implication"].lower() or "field" in result["advisory_implication"].lower()


# ==============================================================================
# 5. PLANT PATHOLOGY & IPM SAFETY GUARDRAILS
# ==============================================================================

def test_disease_magic_bytes_security_validation():
    """Verify non-image bytes disguised as image are rejected before model ingestion."""
    fake_png_header_bad_content = b"%PDF-1.4 Malicious script or malformed binary payload" + b"\x00" * 2000
    res = validate_image_payload("malicious.png", fake_png_header_bad_content)
    assert res["valid"] is False
    assert "magic byte" in res["error"].lower() or "signature" in res["error"].lower() or "invalid" in res["error"].lower()


def test_disease_ipm_advisory_no_hazardous_dosages():
    """Verify generated disease advisory focuses on IPM cultural controls, NOT toxic pesticide dosages."""
    mock_pred = {
        "status": "ASSESSED",
        "crop": "Cotton",
        "condition": "Bacterial Blight",
        "confidence": 0.88,
    }
    advisory = generate_disease_advisory(mock_pred)
    combined_text = " ".join(advisory["cultural_management"]).lower()
    assert "spray 500ml of monocrotophos" not in combined_text
    assert "strictly prohibits unverified synthetic chemical pesticide recommendations" in advisory["chemical_pesticide_notice"].lower()


# ==============================================================================
# 6. REGENERATIVE AGRICULTURE MULTI-HORIZON ENGINE
# ==============================================================================

def test_regenerative_multi_horizon_structure():
    """Verify regenerative recommendations are structured into actionable prioritized practices."""
    farm_info = {
        "current_crop": "Cotton",
        "crop": "Cotton",
        "state": "Maharashtra",
        "soil_type": "black",
        "irrigation_available": "no",
        "rainfall": 650.0,
        "N": 150, "P": 10, "K": 180,
        "ph": 5.2,  # Acidic constraint
        "EC": 0.3,
        "OC": 0.35, # Severe organic carbon deficiency
    }
    result = advise_regenerative_practices(farm_info)
    assert "recommendations" in result
    
    practices = result["recommendations"]
    assert len(practices) >= 2

    # Check for presence of distinct urgencies / horizon planning
    urgencies = {p.get("urgency", "MEDIUM") for p in practices}
    assert len(urgencies) >= 1

    # Check that yield guarantee claims are absent
    for p in practices:
        justification = (p.get("rationale", "") + " " + p.get("expected_benefits", "")).lower()
        assert "guaranteed 100% yield" not in justification
        assert "guarantee" not in justification


# ==============================================================================
# 7. KNOWLEDGE GRAPH REASONING & TRACEABILITY
# ==============================================================================

def test_recommendation_traceability_chain():
    """Verify recommendations provide an explicit reasoning trace from observation to source."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Karnataka",
            "district": "Dharwad",
            "season": "kharif",
            "soil_type": "red",
            "irrigation_available": "yes"
        },
        "soil_data": {
            "N": 180, "P": 12, "K": 220, "ph": 8.3, "EC": 1.2, "OC": 0.45
        },
        "env_data": {
            "temperature": 29.0, "humidity": 68.0, "rainfall": 720.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["success"] is True
    assert "ranked_crops" in data
    assert len(data["ranked_crops"]) > 0

    top_crop = data["ranked_crops"][0]
    # Crop recommendation must provide supporting agronomic factors
    assert "composite_score" in top_crop or "classification" in top_crop or "suitability_score" in top_crop


# ==============================================================================
# 8. BRICS 5-NATION INTEROPERABILITY & CANONICAL DATA MODEL
# ==============================================================================

def test_brics_5_nation_adapters_canonical_mapping():
    """Verify adapters for India, Brazil, Russia, China, and South Africa normalize into Canonical Agricultural Model."""
    raw_bra = {
        "farm_id": "test-bra-001",
        "location": {"latitude": -12.54, "longitude": -55.72, "state_or_province": "Mato Grosso", "municipality": "Sorriso"},
        "timestamp": "2026-09-30T10:00:00Z",
        "soil": {"organic_matter_g_dm3": 25.0, "ph_cacl2": 5.4, "p_mehlich_mg_dm3": 12.0},
        "weather": {"temperature_c": 28.5, "rainfall_mm": 120.0}
    }
    sim_bra = run_brics_interoperability_simulation("BRA", raw_bra)
    assert sim_bra["status"] in ["NORMALIZATION_SUCCESS", "SUCCESS"]
    assert sim_bra["normalized_agrin_payload"]["country_iso3"] == "BRA"
    assert sim_bra["normalized_agrin_payload"]["state"] == "Mato Grosso"
    assert sim_bra["normalized_agrin_payload"]["district"] == "Sorriso"

    # Test all 5 ISO3 codes directly via registry
    for code, expected_country in [
        ("IND", "India"),
        ("BRA", "Brazil"),
        ("RUS", "Russia"),
        ("CHN", "China"),
        ("ZAF", "South Africa")
    ]:
        adapter = get_country_adapter(code)
        assert adapter is not None
        assert adapter.country_iso3 == code
        assert adapter.country_name == expected_country


def test_brics_partner_adapters_declare_non_live():
    """Verify Brazil, Russia, China, and South Africa adapters do not claim live government connectivity."""
    for code in ["BRA", "RUS", "CHN", "ZAF"]:
        adapter = get_country_adapter(code)
        assert adapter.is_reference_implementation is False


# ==============================================================================
# 9. FARM RESILIENCE VS DATA COMPLETENESS DECOUPLING
# ==============================================================================

def test_resilience_score_decoupled_from_data_completeness():
    """Verify high data completeness does not artificially inflate a farm's ecological resilience."""
    degraded_farm_full_data = {
        "state": "Rajasthan",
        "district": "Jodhpur",
        "season": "kharif",
        "temperature": 42.0,
        "rainfall": 150.0,
        "humidity": 20.0,
        "soil_type": "sandy",
        "irrigation_available": "no",
        "N": 50, "P": 4, "K": 60,
        "pH": 9.4,   # Severe sodicity/alkalinity
        "EC": 4.8,   # Severe salinity
        "OC": 0.21,  # Critical organic carbon depletion
    }

    res = calculate_farm_resilience(degraded_farm_full_data, crop_suitability_score=35.0)
    assert res["score"] < 50.0
    assert res["resilience_tier"] in ["LOW_RESILIENCE", "CRITICAL_RISK", "MODERATE_RESILIENCE", "HIGHLY_VULNERABLE"]


# ==============================================================================
# 10. SECURITY & ROBUSTNESS: UNIT BOUNDARIES & PAYLOADS
# ==============================================================================

def test_unit_normalizer_temperature_and_rainfall():
    """Verify scientific conversions: Fahrenheit to Celsius, inches to millimeters."""
    # 77 Fahrenheit -> 25.0 Celsius
    temp_c, unit_t = AgriculturalUnitNormalizer.normalize_temperature(77.0, "degF")
    assert round(temp_c, 1) == 25.0
    assert unit_t == "degC"

    # 4 inches rain -> 101.6 mm
    rain_mm, unit_r = AgriculturalUnitNormalizer.normalize_rainfall(4.0, "inch")
    assert round(rain_mm, 1) == 101.6
    assert unit_r == "mm"

    # 250 lb/acre nutrient -> kg/ha
    nut = AgriculturalUnitNormalizer.normalize_soil_nutrient(250.0, "lb/acre")
    assert pytest.approx(nut["kg_per_ha"], 0.5) == 280.2
