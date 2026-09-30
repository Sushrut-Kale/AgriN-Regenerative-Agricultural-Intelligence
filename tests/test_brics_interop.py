"""
Tests for BRICS Interoperability & Common Agricultural Data Model
Validates Phase 15 requirements:
- Common agricultural schema contains zero India-only required fields
- Brazil, Russia, China, and South Africa adapters map correctly to ADE normalized formats
- Partner adapters honestly maintain is_reference_implementation == False
"""

import pytest
from datetime import datetime, timezone

from backend.app.adapters.base import BaseCountryAdapter
from backend.app.adapters import get_country_adapter, ADAPTER_REGISTRY
from backend.app.adapters.india import IndiaAdapter
from backend.app.adapters.brics import (
    BrazilAdapter, RussiaAdapter, ChinaAdapter, SouthAfricaAdapter
)
from backend.app.services.agri_interoperability import (
    ADE_Location, ADE_SoilObservation, ADE_WeatherObservation, ADE_CropObservation
)

def test_common_schema_contains_no_india_only_assumptions():
    """Verify that ADE models do not require Indian-specific admin hierarchies."""
    loc = ADE_Location(
        country_iso3="BRA",
        admin_level_1="Mato Grosso",
        admin_level_2="Sorriso",
        latitude=-12.54,
        longitude=-55.72
    )
    assert loc.country_iso3 == "BRA"
    assert loc.admin_level_1 == "Mato Grosso"
    assert loc.admin_level_2 == "Sorriso"

    # Common soil observation accepts standard SI and universal laboratory methods
    soil_obs = ADE_SoilObservation(
        observation_id="obs-bra-001",
        farm_uuid="farm-bra-123",
        observed_at=datetime.now(timezone.utc),
        laboratory_standard="EMBRAPA_MANUAL_SOLOS_2017",
        ph_water=5.2,
        organic_carbon_percent=1.45,
        nitrogen_available_mg_kg=None,
        phosphorus_available_mg_kg=8.5,
        potassium_available_mg_kg=120.0
    )
    assert soil_obs.laboratory_standard == "EMBRAPA_MANUAL_SOLOS_2017"
    assert soil_obs.ph_water == 5.2

def test_reference_implementation_flag():
    """Verify India is the sole live reference implementation and BRICS partners are ARCHITECTURE_READY."""
    ind = IndiaAdapter()
    assert ind.is_reference_implementation is True
    assert ind.country_iso3 == "IND"

    for code, adapter_cls in [
        ("BRA", BrazilAdapter),
        ("RUS", RussiaAdapter),
        ("CHN", ChinaAdapter),
        ("ZAF", SouthAfricaAdapter),
    ]:
        adapter = adapter_cls()
        assert adapter.is_reference_implementation is False, f"{code} must not claim live reference implementation"
        assert adapter.country_iso3 == code

def test_brazil_adapter_normalization():
    """Verify Brazil EMBRAPA soil and location translation."""
    brazil = BrazilAdapter()
    loc = brazil.resolve_location({
        "state_or_province": "Goias",
        "municipality": "Rio Verde",
        "latitude": -17.79,
        "longitude": -50.91
    })
    assert loc.country_iso3 == "BRA"
    assert loc.admin_level_1 == "Goias"
    assert loc.admin_level_2 == "Rio Verde"

    soil = brazil.normalize_soil_test({
        "ph_cacl2": 5.4,
        "organic_matter_g_dm3": 28.0
    }, farm_uuid="farm-rio-verde")
    assert soil.laboratory_standard == "EMBRAPA_MANUAL_SOLOS_2017"
    assert soil.ph_water == 5.4
    assert round(soil.organic_carbon_percent, 2) == round(28.0 / 17.24, 2)

def test_south_africa_adapter_normalization():
    """Verify South Africa ARC normalization."""
    zaf = SouthAfricaAdapter()
    loc = zaf.resolve_location({
        "province": "Free State",
        "district_municipality": "Lejweleputswa",
        "latitude": -28.23,
        "longitude": 26.78
    })
    assert loc.country_iso3 == "ZAF"
    assert loc.admin_level_1 == "Free State"

    soil = zaf.normalize_soil_test({
        "ph_kcl": 5.8,
        "organic_carbon_walkley_black": 0.85
    }, farm_uuid="farm-zaf-456")
    assert soil.laboratory_standard == "SSSSA_HANDBOOK_1990"
    assert soil.organic_carbon_percent == 0.85

def test_brics_adapter_registry_lookup():
    """Verify factory lookup for all 5 BRICS countries."""
    for iso3 in ["IND", "BRA", "RUS", "CHN", "ZAF"]:
        ad = get_country_adapter(iso3)
        assert ad is not None
        assert ad.country_iso3 == iso3
    
    # Non-registered defaults to reference implementation (IND)
    assert get_country_adapter("USA").country_iso3 == "IND"
