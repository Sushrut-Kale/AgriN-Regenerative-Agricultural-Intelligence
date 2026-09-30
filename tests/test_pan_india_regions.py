"""
AgriN — Pan-India Regional Architecture Verification Test Suite
================================================================
Verifies that the software architecture is fully Pan-India and location-aware,
demonstrating operational stability across distinct Indian states, agro-climatic zones,
and weather profiles without Maharashtra lock-in.

Test Scenarios:
  1. Maharashtra (Preserved backward compatibility)
  2. Punjab (Trans-Gangetic Plain — Canal/Tube-well irrigated cereal/pulse)
  3. Rajasthan (Western Dry Region — Arid/Desert pulse adaptation)
  4. Kerala (West Coast Plains & Ghats — High precipitation coastal plantation)
  5. Tamil Nadu (East Coast Plains & Hills — Cauvery Delta / Southern climate)
  6. Assam (Eastern Himalayan Region — High humidity / valley monsoon)
  7. Karnataka (Southern Plateau & Hills — Deccan red/black soil transition)
  8. Geolocation resolution from raw GPS coordinates
  9. Pan-India reference data API coverage
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.services.geo_service import (
    get_all_states, get_districts_for_state, find_district_by_name,
    find_nearest_district, get_crop_seasons_for_region
)
from backend.app.services.weather_service import fetch_live_weather

client = TestClient(app)


# ── 1. MAHARASHTRA — Backward Compatibility ────────────────────────────────────

def test_maharashtra_backward_compatibility():
    """Verify existing Maharashtra workflow operates without regression."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Maharashtra",
            "district": "Parbhani",
            "season": "kharif",
            "soil_type": "black",
            "irrigation_available": "no"
        },
        "soil_data": {
            "N": 280, "P": 18, "K": 310, "ph": 6.8, "EC": 0.42, "OC": 0.62,
            "S": 14, "Zn": 0.55, "Fe": 5.2, "Cu": 0.45, "Mn": 4.8, "B": 0.48
        },
        "env_data": {
            "temperature": 28.0, "humidity": 65.0, "rainfall": 700.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["ranked_crops"]) > 0
    # Top crop should be suitable
    top = data["ranked_crops"][0]
    assert top["final_score"] > 50


# ── 2. PUNJAB — Trans-Gangetic Plain Scenario ──────────────────────────────────

def test_punjab_trans_gangetic_plain():
    """Verify Punjab farm (Ludhiana) in Trans-Gangetic Plain ACZ."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Punjab",
            "district": "Ludhiana",
            "sub_district": "Ludhiana West",
            "season": "kharif",
            "soil_type": "alluvial",
            "irrigation_available": "yes",
            "water_source": "tubewell"
        },
        "soil_data": {
            "N": 240, "P": 25, "K": 220, "ph": 7.4, "EC": 0.35, "OC": 0.55
        },
        "env_data": {
            "temperature": 31.0, "humidity": 68.0, "rainfall": 650.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    crops = [c["crop"] for c in data["ranked_crops"]]
    assert "rice" in crops or "maize" in crops or "cotton" in crops


# ── 3. RAJASTHAN — Western Dry Region Scenario ─────────────────────────────────

def test_rajasthan_western_dry_region():
    """Verify Rajasthan farm (Jodhpur) in Western Dry Region with arid climate."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Rajasthan",
            "district": "Jodhpur",
            "sub_district": "Luni",
            "season": "kharif",
            "soil_type": "sandy",
            "irrigation_available": "no"
        },
        "soil_data": {
            "N": 120, "P": 12, "K": 180, "ph": 8.0, "EC": 0.65, "OC": 0.28
        },
        "env_data": {
            "temperature": 33.0, "humidity": 40.0, "rainfall": 320.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    # Drought-hardy legume should rank prominently in low rainfall
    top_crops = [c["crop"] for c in data["ranked_crops"][:5]]
    assert any(c in top_crops for c in ["mothbeans", "mungbean", "chickpea", "pomegranate"])


# ── 4. KERALA — High-Rainfall West Coast Scenario ──────────────────────────────

def test_kerala_west_coast_ghats():
    """Verify Kerala farm (Kochi / Palakkad) under high monsoon rainfall (2600mm)."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Kerala",
            "district": "Kochi",
            "sub_district": "Aluva",
            "season": "kharif",
            "soil_type": "laterite",
            "irrigation_available": "yes",
            "drainage": "good"
        },
        "soil_data": {
            "N": 200, "P": 22, "K": 260, "ph": 5.6, "EC": 0.20, "OC": 1.10
        },
        "env_data": {
            "temperature": 27.5, "humidity": 85.0, "rainfall": 2800.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    top_crops = [c["crop"] for c in data["ranked_crops"][:5]]
    # Heavy rainfall tolerant crops (rice, coconut, banana) should perform well
    assert any(c in top_crops for c in ["rice", "coconut", "banana", "coffee"])


# ── 5. TAMIL NADU — East Coast Plains Scenario ─────────────────────────────────

def test_tamil_nadu_east_coast_plains():
    """Verify Tamil Nadu farm (Thanjavur) in Cauvery Delta."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Tamil Nadu",
            "district": "Thanjavur",
            "season": "kharif",
            "soil_type": "alluvial",
            "irrigation_available": "yes",
            "water_source": "canal"
        },
        "soil_data": {
            "N": 260, "P": 24, "K": 290, "ph": 7.0, "EC": 0.40, "OC": 0.70
        },
        "env_data": {
            "temperature": 29.5, "humidity": 75.0, "rainfall": 1050.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    top_crop = data["ranked_crops"][0]
    assert top_crop["final_score"] > 40
    assert top_crop["classification"] in ("Moderately Suitable", "Suitable", "Highly Suitable")


# ── 6. ASSAM — Eastern Himalayan Region Scenario ───────────────────────────────

def test_assam_eastern_himalayan_region():
    """Verify Assam farm (Kamrup) under humid subtropical conditions."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Assam",
            "district": "Kamrup",
            "season": "kharif",
            "soil_type": "alluvial",
            "irrigation_available": "no"
        },
        "soil_data": {
            "N": 210, "P": 20, "K": 200, "ph": 5.8, "EC": 0.25, "OC": 0.95
        },
        "env_data": {
            "temperature": 25.0, "humidity": 82.0, "rainfall": 1800.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    crops = [c["crop"] for c in data["ranked_crops"][:5]]
    assert any(c in crops for c in ["rice", "jute", "banana"])


# ── 7. KARNATAKA — Southern Plateau & Hills Scenario ───────────────────────────

def test_karnataka_southern_plateau():
    """Verify Karnataka farm (Dharwad) in transitional Deccan zone."""
    payload = {
        "farm_data": {
            "country": "India",
            "state": "Karnataka",
            "district": "Dharwad",
            "season": "kharif",
            "soil_type": "black",
            "irrigation_available": "yes"
        },
        "soil_data": {
            "N": 250, "P": 22, "K": 280, "ph": 7.2, "EC": 0.38, "OC": 0.65
        },
        "env_data": {
            "temperature": 26.5, "humidity": 62.0, "rainfall": 780.0
        }
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["ranked_crops"]) >= 5


# ── 8. GPS / COORDINATE RESOLUTION & WEATHER ──────────────────────────────────

def test_gps_coordinate_resolution_and_weather():
    """Verify automatic geolocation resolution from raw coordinates (Ludhiana, Punjab)."""
    # Coordinates of Ludhiana, Punjab
    lat, lon = 30.90, 75.85
    nearest_d, state = find_nearest_district(lat, lon)
    assert state == "Punjab"
    assert "Ludhiana" in nearest_d["name"]

    # Weather fetch with coordinates
    weather = fetch_live_weather(lat=lat, lon=lon)
    assert weather["state"] == "Punjab"
    assert "Ludhiana" in weather["district"]
    assert "coordinates" in weather
    assert weather["coordinates"]["lat"] == lat


# ── 9. REFERENCE DATA API COVERS ALL 36 STATES & UNION TERRITORIES ────────────

def test_all_states_reference_data():
    """Verify /api/reference-data supplies states and filters districts dynamically."""
    # 1. Default request
    res = client.get("/api/reference-data")
    assert res.status_code == 200
    data = res.json()
    assert "states" in data
    assert len(data["states"]) == 36  # 28 states + 8 UTs

    # 2. State-filtered request (Rajasthan)
    res_rj = client.get("/api/reference-data?state=Rajasthan")
    assert res_rj.status_code == 200
    data_rj = res_rj.json()
    assert data_rj["selected_state"] == "Rajasthan"
    district_names = [d["name"] for d in data_rj["districts"]]
    assert any("Jaipur" in d or "Jodhpur" in d for d in district_names)

    # 3. State-filtered request (Kerala)
    res_kl = client.get("/api/reference-data?state=Kerala")
    assert res_kl.status_code == 200
    data_kl = res_kl.json()
    assert data_kl["selected_state"] == "Kerala"
    kl_districts = [d["name"] for d in data_kl["districts"]]
    assert any("Kochi" in d or "Thiruvananthapuram" in d for d in kl_districts)
