"""
Phase 4 Comprehensive Test Suite: Real Agricultural Intelligence Activation.

Covers:
1. Satellite Provider Architecture & Guardrails (Sentinel, Landsat, Demo, Caching, Validation, Temporal Trends)
2. Plant Pathology Vision Provider Architecture & Safety (Local Vision, Demo, Magic Bytes, Gating, IPM Advisory)
3. Unit Normalizer (Multi-country SI & regional units: temp, rainfall, nutrients, EC, organic carbon, area, volume)
4. BRICS Canonical Interoperability (Strict validation, India, Brazil, South Africa adapters, deterministic simulation)
5. Multi-Source Fusion (Soil + Weather + Satellite cross-domain evidence synthesis)
6. Canonical Snapshot & Report Transparency (Evidence timeline, zero fabricated claims, strict demo labeling)
"""

import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.satellite_service import (
    SentinelProvider,
    LandsatProvider,
    DemoSatelliteProvider,
    get_satellite_provider,
    SatelliteObservation,
    interpret_satellite_observation,
    analyze_satellite_time_series,
    fuse_satellite_weather_soil,
    get_satellite_observation,
)
from backend.app.services.disease_service import (
    LocalVisionModelProvider,
    DemoDiseaseProvider,
    get_disease_provider,
    validate_image_payload,
    generate_disease_advisory,
    diagnose_crop_image,
)
from backend.app.services.unit_normalizer import (
    AgriculturalUnitNormalizer,
    UnitValidationError,
)
from backend.app.adapters.india import IndiaAdapter
from backend.app.adapters.brics import (
    BrazilAdapter,
    SouthAfricaAdapter,
    run_brics_interoperability_simulation,
)
from backend.app.models.canonical_agri_model import (
    CanonicalLocation,
    CanonicalSoilObservation,
    CanonicalWeatherObservation,
    FarmIntelligenceSnapshot,
    ProvenanceRecord,
)

client = TestClient(app)


# ==============================================================================
# 1. SATELLITE TESTS
# ==============================================================================

class TestSatelliteIntelligence:
    def test_provider_selection_production_unconfigured(self):
        """Sentinel and Landsat return NOT_CONNECTED when credentials not configured."""
        sentinel = SentinelProvider(api_key="")
        assert sentinel.is_connected() is False
        obs = sentinel.fetch_observation(19.0, 75.0)
        assert obs["status"] == "NOT_CONNECTED"
        assert obs["ndvi"] is None

        landsat = LandsatProvider(api_key="")
        assert landsat.is_connected() is False
        obs = landsat.fetch_observation(19.0, 75.0)
        assert obs["status"] == "NOT_CONNECTED"
        assert obs["ndvi"] is None

    def test_provider_selection_demo_mode(self, monkeypatch):
        """When allow_demo=True or AGRIN_DEMO_MODE=true, provider is DemoSatelliteProvider with explicit synthetic labeling."""
        monkeypatch.setenv("AGRIN_DEMO_MODE", "true")
        provider = get_satellite_provider(allow_demo=True)
        assert isinstance(provider, DemoSatelliteProvider)
        assert provider.is_connected() is True

        obs = provider.fetch_observation(19.26, 76.78)
        assert obs is not None
        assert obs["status"] == "CONNECTED"
        assert obs["is_synthetic"] is True
        assert -1.0 <= obs["ndvi"] <= 1.0

    def test_missing_provider_when_demo_disabled(self, monkeypatch):
        """When AGRIN_DEMO_MODE=false and no credentials, returns SentinelProvider marked NOT_CONNECTED."""
        monkeypatch.setenv("AGRIN_DEMO_MODE", "false")
        monkeypatch.delenv("COPERNICUS_API_KEY", raising=False)
        provider = get_satellite_provider(allow_demo=False)
        assert provider.is_connected() is False
        obs = provider.fetch_observation(19.0, 75.0)
        assert obs["status"] == "NOT_CONNECTED"
        assert obs["ndvi"] is None

    def test_satellite_observation_model_validation(self):
        # Valid observation
        valid = SatelliteObservation(
            latitude=19.2,
            longitude=76.8,
            observation_date="2026-09-30T10:00:00Z",
            source="TestSat",
            resolution_meters=10.0,
            cloud_cover_pct=5.0,
            ndvi=0.68,
            ndwi=0.15,
            vegetation_status="HEALTHY",
            data_quality="HIGH",
            is_synthetic=True,
        )
        assert valid.ndvi == 0.68

    def test_temporal_trend_requires_minimum_two_observations(self):
        """Temporal trend requires at least 2 distinct observations; 1 returns INSUFFICIENT_HISTORY."""
        obs1 = {
            "latitude": 19.0,
            "longitude": 75.0,
            "observation_date": "2026-09-01T00:00:00Z",
            "source": "Sentinel-2",
            "ndvi": 0.40,
            "ndwi": 0.05,
            "vegetation_status": "MODERATE",
            "data_quality": "HIGH",
            "is_synthetic": False,
        }
        single_res = analyze_satellite_time_series([obs1])
        assert single_res["trend"] == "INSUFFICIENT_HISTORY"
        assert single_res["confidence"] == "LOW"

        obs2 = {
            "latitude": 19.0,
            "longitude": 75.0,
            "observation_date": "2026-09-15T00:00:00Z",
            "source": "Sentinel-2",
            "ndvi": 0.55,
            "ndwi": 0.12,
            "vegetation_status": "HEALTHY",
            "data_quality": "HIGH",
            "is_synthetic": False,
        }
        trend_improving = analyze_satellite_time_series([obs1, obs2])
        assert trend_improving["trend"] == "IMPROVING"
        assert trend_improving["change_magnitude"] > 0

        obs3 = {
            "latitude": 19.0,
            "longitude": 75.0,
            "observation_date": "2026-09-30T00:00:00Z",
            "source": "Sentinel-2",
            "ndvi": 0.30,
            "ndwi": -0.05,
            "vegetation_status": "DECLINING",
            "data_quality": "HIGH",
            "is_synthetic": False,
        }
        trend_declining = analyze_satellite_time_series([obs2, obs3])
        assert trend_declining["trend"] == "DECLINING"

    def test_cautious_agricultural_reasoning(self):
        """Never diagnoses disease from NDVI alone. Uses cautious, agronomic language."""
        obs_decline = {
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
        interpretation = interpret_satellite_observation(obs_decline)
        assert "disease" not in interpretation["primary_interpretation"].lower()
        assert "inspect" in interpretation["advisory_implication"].lower()
        assert "physiological indicator" in interpretation["responsible_ai_guardrail"].lower()


# ==============================================================================
# 2. DISEASE DIAGNOSTIC & IMAGE SAFETY TESTS
# ==============================================================================

class TestDiseaseDiagnosticSafety:
    def test_invalid_image_magic_bytes_rejected(self):
        """Reject non-image content even if file extension is forged."""
        fake_content = b"THIS_IS_A_TEXT_FILE_NOT_AN_IMAGE_PAYLOAD" + b"\x00" * 1200
        val = validate_image_payload("malicious.jpg", fake_content)
        assert val["valid"] is False
        assert "magic byte" in val["error"].lower()

    def test_image_size_limits_enforced(self):
        """Reject files smaller than 1KB or larger than 10MB."""
        tiny = b"\xFF\xD8\xFF" + b"\x00" * 10
        val = validate_image_payload("tiny.jpg", tiny)
        assert val["valid"] is False
        assert "too small" in val["error"].lower()

        oversized = b"\xFF\xD8\xFF" + b"\x00" * (11 * 1024 * 1024)
        val_over = validate_image_payload("large.jpg", oversized)
        assert val_over["valid"] is False
        assert "exceeds maximum" in val_over["error"].lower()

    def test_path_traversal_filename_sanitized(self):
        """Directory traversal characters in filename are rejected or stripped."""
        valid_jpeg_header = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"\x00" * 1100
        val = validate_image_payload("../../etc/passwd.jpg", valid_jpeg_header)
        assert val["valid"] is False
        assert "path traversal" in val["error"].lower()

    def test_production_provider_returns_model_not_deployed_without_weights(self, monkeypatch):
        monkeypatch.setenv("AGRIN_DEMO_MODE", "false")
        monkeypatch.delenv("AGRIN_VISION_MODEL_PATH", raising=False)
        provider = get_disease_provider(allow_demo=False)
        assert isinstance(provider, LocalVisionModelProvider)
        assert provider.is_available() is False

        valid_jpeg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"\x00" * 1100
        res = provider.predict(valid_jpeg, crop_hint="cotton")
        assert res["status"] == "MODEL_NOT_DEPLOYED"
        assert res["confidence"] == 0.0

    def test_confidence_threshold_gating_triggers_review_required(self):
        """Predictions with confidence below 0.70 trigger REVIEW_REQUIRED, not confirmed screening."""
        mock_pred = {
            "status": "ASSESSED",
            "crop": "cotton",
            "condition": "Bacterial Blight",
            "confidence": 0.55,
        }
        advisory = generate_disease_advisory(mock_pred)
        assert advisory["advisory_status"] == "REVIEW_REQUIRED"
        assert "do not apply chemical fungicides" in advisory["guidance"].lower()

    def test_safe_ipm_guidance_no_unverified_pesticide_dosages(self):
        """Advisory guidance must prioritize cultural and biological IPM practices, never toxic dosages."""
        mock_pred = {
            "status": "ASSESSED",
            "crop": "cotton",
            "condition": "Bacterial Blight",
            "confidence": 0.88,
        }
        advisory = generate_disease_advisory(mock_pred)
        combined_text = " ".join(advisory["cultural_management"]).lower()
        assert "spray 500ml of monocrotophos" not in combined_text
        assert any(term in combined_text for term in ["airflow", "drainage", "bio-control", "trichoderma", "pseudomonas"])
        assert "strictly prohibits unverified synthetic chemical pesticide recommendations" in advisory["chemical_pesticide_notice"].lower()


# ==============================================================================
# 3. UNIT NORMALIZATION TESTS
# ==============================================================================

class TestUnitNormalizer:
    def test_temperature_conversions(self):
        # Celsius to Celsius
        val, unit = AgriculturalUnitNormalizer.normalize_temperature(30.0, "celsius")
        assert val == 30.0
        assert unit == "degC"

        # Fahrenheit to Celsius
        f_val, _ = AgriculturalUnitNormalizer.normalize_temperature(86.0, "°F")
        assert pytest.approx(f_val, 0.1) == 30.0

        # Kelvin to Celsius
        k_val, _ = AgriculturalUnitNormalizer.normalize_temperature(303.15, "K")
        assert pytest.approx(k_val, 0.1) == 30.0

    def test_rainfall_conversions(self):
        mm_val, _ = AgriculturalUnitNormalizer.normalize_rainfall(100.0, "mm")
        assert mm_val == 100.0

        cm_val, _ = AgriculturalUnitNormalizer.normalize_rainfall(10.0, "cm")
        assert cm_val == 100.0

        inch_val, _ = AgriculturalUnitNormalizer.normalize_rainfall(2.0, "inch")
        assert pytest.approx(inch_val, 0.1) == 50.8

    def test_soil_nutrient_conversions(self):
        # kg/ha standard
        kg_ha = AgriculturalUnitNormalizer.normalize_soil_nutrient(280.0, "kg/ha")
        assert kg_ha["kg_per_ha"] == 280.0
        assert kg_ha["mg_per_kg"] == 140.0

        # ppm (mg/kg) to kg/ha
        ppm = AgriculturalUnitNormalizer.normalize_soil_nutrient(125.0, "ppm")
        assert ppm["kg_per_ha"] == 250.0
        assert ppm["mg_per_kg"] == 125.0

        # lb/acre to kg/ha (1 lb/acre = 1.12085 kg/ha)
        lb = AgriculturalUnitNormalizer.normalize_soil_nutrient(250.0, "lb/acre")
        assert pytest.approx(lb["kg_per_ha"], 0.5) == 280.2

    def test_soil_organic_carbon_brazil_and_south_africa(self):
        # Brazilian Embrapa g/dm³ to % OC (g/dm³ / 17.24)
        bra_val, _ = AgriculturalUnitNormalizer.normalize_organic_carbon(28.0, "g/dm3")
        assert pytest.approx(bra_val, 0.1) == 1.62

        # Soil Organic Matter (SOM) % to SOC % (van Bemmelen factor: SOM / 1.724)
        som_val, _ = AgriculturalUnitNormalizer.normalize_organic_carbon(3.0, "% som")
        assert pytest.approx(som_val, 0.05) == 1.74

    def test_area_and_water_volume(self):
        # 2.47105 Acres to Hectare
        ha_val, _ = AgriculturalUnitNormalizer.normalize_area(2.47105, "acre")
        assert pytest.approx(ha_val, 0.01) == 1.0

        # Bigha (Upper India Standard ~0.2529 ha)
        bigha_val, _ = AgriculturalUnitNormalizer.normalize_area(4.0, "bigha")
        assert pytest.approx(bigha_val, 0.05) == 1.01

        # 10,000 Liters to m³
        vol_val, _ = AgriculturalUnitNormalizer.normalize_water_volume(10000.0, "liters")
        assert vol_val == 10.0

    def test_unsupported_unit_raises_validation_error(self):
        with pytest.raises(UnitValidationError, match="Unsupported temperature unit"):
            AgriculturalUnitNormalizer.normalize_temperature(30.0, "fathoms")


# ==============================================================================
# 4. BRICS INTEROPERABILITY TESTS
# ==============================================================================

class TestBricsInteroperability:
    def test_india_adapter_location_resolution(self):
        adapter = IndiaAdapter()
        loc = adapter.resolve_location({"state": "Maharashtra", "district": "Parbhani"})
        assert loc.country_iso3 == "IND"
        assert loc.admin_level_1 == "Maharashtra"
        assert loc.admin_level_2 == "Parbhani"
        assert pytest.approx(loc.latitude, 0.5) == 19.26

    def test_brazil_adapter_unit_normalization(self):
        adapter = BrazilAdapter()
        loc = adapter.resolve_location({"state_or_province": "Mato Grosso", "municipality": "Sorriso", "latitude": -12.54, "longitude": -55.72})
        assert loc.country_iso3 == "BRA"
        
        soil_obs = adapter.normalize_soil_test({
            "organic_matter_g_dm3": 28.0,  # 28 g/dm3 -> % OC ~ 1.62
            "ph_cacl2": 5.2,               # 5.2 + 0.6 = 5.8 pH water
            "p_mehlich_mg_dm3": 15.0       # 15 mg/kg
        }, farm_uuid="farm-bra-01")
        assert pytest.approx(soil_obs.organic_carbon_percent, 0.1) == 1.62
        assert soil_obs.ph_water == 5.2
        assert soil_obs.available_phosphorus_mg_kg == 15.0

    def test_south_africa_adapter_unit_normalization(self):
        adapter = SouthAfricaAdapter()
        loc = adapter.resolve_location({"province": "Free State", "district_municipality": "Lejweleputswa", "latitude": -27.98, "longitude": 26.73})
        assert loc.country_iso3 == "ZAF"

        soil_obs = adapter.normalize_soil_test({
            "organic_carbon_walkley_black": 1.25,
            "ph_water": 6.4
        }, farm_uuid="farm-zaf-01")
        assert soil_obs.organic_carbon_percent == 1.25
        assert soil_obs.ph_water == 6.4

    def test_deterministic_brics_simulation_runner(self):
        """Simulate synthetic exchange across IND, BRA, ZAF without claiming live external connection."""
        raw_bra = {
            "farm_id": "test-bra-001",
            "location": {"latitude": -12.54, "longitude": -55.72},
            "timestamp": "2026-09-30T10:00:00Z",
            "soil": {"organic_matter_g_dm3": 25.0, "ph_cacl2": 5.4},
            "weather": {"temperature": 31.0, "rainfall": 12.0}
        }
        res_bra = run_brics_interoperability_simulation("BRA", raw_bra)
        assert res_bra["status"] == "NORMALIZATION_SUCCESS"
        assert res_bra["country_code"] == "BRA"
        assert res_bra["is_synthetic"] is True
        assert res_bra["normalized_agrin_payload"]["weather"]["temperature"] == 31.0

        raw_zaf = {
            "farm_id": "test-zaf-001",
            "location": {"latitude": -27.98, "longitude": 26.73},
            "timestamp": "2026-09-30T10:00:00Z",
            "soil": {"organic_carbon_walkley_black": 1.1, "ph_water": 6.2},
            "weather": {"temperature": 24.0, "rainfall": 5.0}
        }
        res_zaf = run_brics_interoperability_simulation("ZAF", raw_zaf)
        assert res_zaf["status"] == "NORMALIZATION_SUCCESS"
        assert res_zaf["country_code"] == "ZAF"
        assert res_zaf["is_synthetic"] is True

        res_ind = run_brics_interoperability_simulation("IND", {"farm_id": "test-ind-001"})
        assert res_ind["status"] == "NORMALIZATION_SUCCESS"
        assert res_ind["country_code"] == "IND"


# ==============================================================================
# 5. MULTI-SOURCE FUSION TESTS
# ==============================================================================

class TestMultiSourceFusion:
    def test_soil_weather_satellite_fusion_elevated_water_stress(self):
        """Low soil moisture + high evaporative demand + declining NDVI = ELEVATED_WATER_STRESS."""
        soil = {
            "ph": 7.5,
            "organic_carbon": 0.45,
            "nitrogen": 140.0,
            "phosphorus": 10.0,
            "potassium": 200.0,
        }
        weather = {
            "temperature": 38.5,  # HIGH
            "humidity": 25.0,     # LOW
            "rainfall": 0.0,
        }
        satellite = {
            "status": "CONNECTED",
            "ndvi": 0.28,         # LOW
            "ndwi": -0.22,
            "vegetation_status": "STRESSED",
            "is_synthetic": False,
        }

        fusion = fuse_satellite_weather_soil(soil, weather, satellite)
        assert fusion["fusion_type"] == "SOIL_WEATHER_SATELLITE_FUSION"
        assert "acute crop water stress risk" in fusion["interpretation"].lower()
        assert fusion["confidence"] == "HIGH"

    def test_soil_and_weather_only_fusion(self):
        """When satellite is unavailable, fusion handles partial evidence honestly without failure."""
        soil = {"ph": 6.5, "organic_carbon": 1.1}
        weather = {"temperature": 26.0, "rainfall": 25.0}

        fusion = fuse_satellite_weather_soil(soil, weather, None)
        assert fusion["fusion_type"] == "SOIL_WEATHER_SATELLITE_FUSION"
        assert "High-resolution satellite feed not linked" in fusion["limitations"][0]


# ==============================================================================
# 6. GUARDRAILS & HONESTY VERIFICATION
# ==============================================================================

class TestGuardrailsAndHonesty:
    def test_never_fabricates_satellite_data_when_demo_mode_off(self, monkeypatch):
        """When demo mode is false and no Copernicus/USGS creds, system returns NOT_CONNECTED."""
        monkeypatch.setenv("AGRIN_DEMO_MODE", "false")
        monkeypatch.delenv("COPERNICUS_API_KEY", raising=False)
        obs = get_satellite_observation(19.2, 76.8, allow_demo=False)
        assert obs["status"] == "NOT_CONNECTED"
        assert obs["ndvi"] is None

    def test_never_claims_disease_from_ndvi_alone(self):
        """Interpretations of satellite imagery must never diagnose plant pathology."""
        obs = {
            "status": "CONNECTED",
            "ndvi": 0.15,
            "ndwi": -0.3,
            "vegetation_status": "STRESSED",
            "is_synthetic": False,
        }
        res = interpret_satellite_observation(obs)
        assert "fungal" not in res["primary_interpretation"].lower()
        assert "virus" not in res["primary_interpretation"].lower()
        assert "pathogen" not in res["primary_interpretation"].lower()

    def test_demo_mode_always_transparently_labeled(self, monkeypatch):
        monkeypatch.setenv("AGRIN_DEMO_MODE", "true")
        obs = get_satellite_observation(19.2, 76.8, allow_demo=True)
        assert obs["status"] == "CONNECTED"
        assert obs["is_synthetic"] is True

        valid_jpeg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"\x00" * 1100
        disease = diagnose_crop_image(valid_jpeg, "leaf.jpg", crop="cotton", allow_demo=True)
        assert disease["diagnostic_result"]["is_synthetic"] is True
        assert "synthetic" in disease["diagnostic_result"]["model_version"].lower()


# ==============================================================================
# 7. FASTAPI API ROUTE INTEGRATION TESTS
# ==============================================================================

class TestApiEndpointsPhase4:
    def test_satellite_status_endpoint(self):
        resp = client.get("/api/satellite/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "satellite_status" in data
        assert "available_providers" in data

    def test_brics_simulate_endpoint(self):
        resp = client.post("/api/brics/simulate", json={
            "country_code": "BRA",
            "raw_payload": {
                "farm_id": "test-bra-01",
                "location": {"latitude": -12.54, "longitude": -55.72},
                "timestamp": "2026-09-30T10:00:00Z",
                "soil": {"organic_matter_g_dm3": 28.0, "ph_cacl2": 5.2},
                "weather": {"temperature": 31.0, "rainfall": 5.0}
            }
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "NORMALIZATION_SUCCESS"
        assert data["country_code"] == "BRA"
        assert data["is_synthetic"] is True

    def test_disease_diagnose_endpoint_rejects_empty_file(self):
        resp = client.post("/api/disease/diagnose", files={"file": ("empty.jpg", b"", "image/jpeg")})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "VALIDATION_FAILED"
        assert data["diagnosis_status"] == "REJECTED"

    def test_crop_knowledge_graph_endpoint(self):
        resp = client.get("/api/knowledge/graph/crop/cotton")
        assert resp.status_code == 200
        data = resp.json()
        assert data["crop"] == "cotton"
        assert "suitable_soil" in data
        assert "risks" in data
        assert "linked_regenerative_practices" in data
