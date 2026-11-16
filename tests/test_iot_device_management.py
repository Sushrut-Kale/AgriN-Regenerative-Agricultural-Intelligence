"""
AgriN / AgriSense IoT — Automated Test Suite
============================================
Comprehensive tests for:
- Device registration & authentication
- Telemetry ingestion & validation
- Strict provenance enforcement (SENSOR_MEASURED vs SYNTHETIC vs UNAVAILABLE)
- Out-of-bounds sensor reading rejection
- Duplicate telemetry detection
- Device heartbeat & online status
- Field management CRUD
- Telemetry history & latest reading retrieval
- End-to-end telemetry-to-intelligence execution & irrigation advisory
"""

import pytest
import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.db import get_db, SessionLocal, init_db
from backend.app.database.iot_models import DeviceStatusEnum, DataSourceProvenance
from backend.app.services.agrin_intelligence import run_intelligence_from_telemetry
from backend.app.services.irrigation_intelligence import compute_irrigation_advisory

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure all tables including IoT tables exist."""
    init_db()
    yield


@pytest.fixture
def test_farm_and_device():
    """Creates a fresh test device for telemetry tests."""
    farm_id = f"test-farm-{uuid.uuid4().hex[:8]}"
    dev_name = f"AgriSense-Test-{uuid.uuid4().hex[:6]}"

    resp = client.post("/api/devices/register", json={
        "farm_id": farm_id,
        "name": dev_name,
        "hardware_profile": "ESP32-DevKit-V1-Standard",
        "firmware_version": "1.0.0"
    })
    assert resp.status_code == 201
    data = resp.json()
    return {
        "farm_id": farm_id,
        "device_id": data["device_id"],
        "api_key": data.get("api_key", "test-key"),
        "name": dev_name
    }


# =============================================================================
# 1. Device Registration Tests
# =============================================================================

def test_device_registration_success():
    payload = {
        "farm_id": "farm-parbhani-01",
        "name": f"AgriSense-Node-{uuid.uuid4().hex[:6]}",
        "hardware_profile": "ESP32-DevKit-V1-Standard",
        "firmware_version": "1.0.0",
        "wifi_ssid": "FarmNet-2G"
    }
    response = client.post("/api/devices/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "device_id" in data
    assert data["name"] == payload["name"]
    assert data["status"] in ("ONLINE", "UNREGISTERED", "OFFLINE")


def test_device_registration_missing_required_fields():
    # Missing farm_id and name
    response = client.post("/api/devices/register", json={"firmware_version": "1.0.0"})
    assert response.status_code == 422


# =============================================================================
# 2. Field Management Tests
# =============================================================================

def test_field_creation_and_listing():
    farm_id = f"farm-field-test-{uuid.uuid4().hex[:6]}"
    field_payload = {
        "farm_id": farm_id,
        "name": "North Cotton Acre",
        "area_hectares": 2.5,
        "location_lat": 19.26,
        "location_lon": 76.78,
        "soil_type": "black",
        "irrigation_type": "drip"
    }
    create_resp = client.post("/api/fields", json=field_payload)
    assert create_resp.status_code == 201
    field_data = create_resp.json()
    assert field_data["name"] == "North Cotton Acre"
    assert field_data["field_id"] is not None

    # List fields
    list_resp = client.get(f"/api/fields/{farm_id}")
    assert list_resp.status_code == 200
    fields = list_resp.json()
    assert len(fields) >= 1
    assert any(f["field_id"] == field_data["field_id"] for f in fields)


# =============================================================================
# 3. Telemetry Ingestion Tests
# =============================================================================

def test_telemetry_ingest_valid_measured(test_farm_and_device):
    dev = test_farm_and_device
    payload = {
        "device_id": dev["device_id"],
        "farm_id": dev["farm_id"],
        "sequence_number": 1,
        "firmware_version": "1.0.0",
        "is_synthetic": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "measurements": [
            {
                "sensor_type": "SOIL_MOISTURE",
                "parameter_name": "soil_moisture",
                "calibrated_value": 38.5,
                "unit": "%",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "sensor_id": "probe-m-01",
                "is_valid": True
            },
            {
                "sensor_type": "SOIL_TEMP",
                "parameter_name": "soil_temperature",
                "calibrated_value": 24.2,
                "unit": "celsius",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "sensor_id": "probe-t-01",
                "is_valid": True
            },
            {
                "sensor_type": "SOIL_PH",
                "parameter_name": "soil_ph",
                "calibrated_value": 7.1,
                "unit": "scale",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "sensor_id": "probe-ph-01",
                "is_valid": True
            },
            {
                "sensor_type": "SOIL_EC",
                "parameter_name": "soil_ec",
                "calibrated_value": 0.65,
                "unit": "dS/m",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "sensor_id": "probe-ec-01",
                "is_valid": True
            }
        ],
        "device_diagnostics": {
            "battery_voltage": 3.92,
            "battery_percent": 84.0,
            "signal_rssi": -65,
            "uptime_seconds": 3600
        }
    }
    resp = client.post("/api/telemetry/ingest", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] in ("SUCCESS", "PROCESSED")
    assert data["measurements_saved"] == 4


def test_telemetry_ingest_synthetic_flagged(test_farm_and_device):
    dev = test_farm_and_device
    payload = {
        "device_id": dev["device_id"],
        "farm_id": dev["farm_id"],
        "sequence_number": 2,
        "is_synthetic": True,  # Explicit synthetic test
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "measurements": [
            {
                "sensor_type": "SOIL_MOISTURE",
                "parameter_name": "soil_moisture",
                "calibrated_value": 44.0,
                "unit": "%",
                "quality": "GOOD",
                "data_source": "SYNTHETIC",
                "is_valid": True
            }
        ]
    }
    resp = client.post("/api/telemetry/ingest", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] in ("SUCCESS", "PROCESSED")


def test_telemetry_duplicate_detection(test_farm_and_device):
    dev = test_farm_and_device
    timestamp_str = datetime.now(timezone.utc).isoformat()
    payload = {
        "device_id": dev["device_id"],
        "farm_id": dev["farm_id"],
        "sequence_number": 9999,
        "timestamp": timestamp_str,
        "measurements": [
            {
                "sensor_type": "SOIL_MOISTURE",
                "parameter_name": "soil_moisture",
                "calibrated_value": 35.0,
                "unit": "%",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "is_valid": True
            }
        ]
    }
    # First post succeeds
    resp1 = client.post("/api/telemetry/ingest", json=payload)
    assert resp1.status_code == 201

    # Exact duplicate post returns DUPLICATE status
    resp2 = client.post("/api/telemetry/ingest", json=payload)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["status"] == "DUPLICATE"


def test_telemetry_impossible_sensor_value_rejected(test_farm_and_device):
    dev = test_farm_and_device
    # Impossible pH (e.g. 25.0) must be rejected by Pydantic validator
    invalid_payload = {
        "device_id": dev["device_id"],
        "farm_id": dev["farm_id"],
        "sequence_number": 55,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "measurements": [
            {
                "sensor_type": "SOIL_PH",
                "parameter_name": "soil_ph",
                "calibrated_value": 25.0,  # Physically impossible (max is 10.0 in range check)
                "unit": "scale",
                "quality": "GOOD",
                "data_source": "SENSOR_MEASURED",
                "is_valid": True
            }
        ]
    }
    resp = client.post("/api/telemetry/ingest", json=invalid_payload)
    assert resp.status_code == 422


# =============================================================================
# 4. Device Heartbeat & Status Tests
# =============================================================================

def test_device_heartbeat_and_status(test_farm_and_device):
    dev = test_farm_and_device
    heartbeat_payload = {
        "battery_voltage": 3.85,
        "battery_percent": 80.0,
        "signal_rssi": -68,
        "uptime_seconds": 7200,
        "free_memory_bytes": 178000,
        "firmware_version": "1.0.0"
    }
    hb_resp = client.post(f"/api/devices/{dev['device_id']}/heartbeat", json=heartbeat_payload)
    assert hb_resp.status_code == 201
    hb_data = hb_resp.json()
    assert hb_data["device_id"] == dev["device_id"]

    # Retrieve updated device status
    status_resp = client.get(f"/api/devices/{dev['device_id']}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["device_id"] == dev["device_id"]
    assert status_data["status"] == "ONLINE"
    assert status_data["battery_percent"] == 80.0


# =============================================================================
# 5. Telemetry History & Latest Retrieval
# =============================================================================

def test_telemetry_history_and_latest(test_farm_and_device):
    dev = test_farm_and_device
    # Get latest
    latest_resp = client.get(f"/api/telemetry/{dev['device_id']}/latest")
    assert latest_resp.status_code == 200
    latest_data = latest_resp.json()
    assert latest_data["device_id"] == dev["device_id"]

    # Get history
    hist_resp = client.get(f"/api/telemetry/{dev['device_id']}/history?page=1&page_size=10")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["device_id"] == dev["device_id"]
    assert "records" in hist_data


# =============================================================================
# 6. Agronomic Irrigation Intelligence Tests
# =============================================================================

def test_irrigation_intelligence_optimal_moisture():
    adv = compute_irrigation_advisory(
        soil_moisture_pct=36.0,
        soil_type="black",
        crop="cotton",
        forecast_rain_mm_next_48h=0.0
    )
    assert adv["status"] == "CALCULATED"
    assert adv["irrigation_needed"] is False
    assert adv["moisture_condition"] in ("OPTIMAL", "SATURATED")


def test_irrigation_intelligence_depleted_moisture():
    adv = compute_irrigation_advisory(
        soil_moisture_pct=21.0,
        soil_type="black",
        crop="cotton",
        forecast_rain_mm_next_48h=0.0
    )
    assert adv["status"] == "CALCULATED"
    assert adv["irrigation_needed"] is True
    assert adv["recommended_amount_mm"] > 0


def test_irrigation_intelligence_unavailable_sensor():
    adv = compute_irrigation_advisory(
        soil_moisture_pct=None,
        soil_type="black"
    )
    assert adv["status"] == "UNAVAILABLE"
    assert adv["irrigation_needed"] is False
    assert "zero data fabrication" in adv["rationale"].lower()


# =============================================================================
# 7. End-to-End Telemetry-to-Intelligence Execution
# =============================================================================

@pytest.mark.asyncio
async def test_run_intelligence_from_telemetry_e2e():
    telemetry_measurements = [
        {
            "sensor_type": "SOIL_MOISTURE",
            "parameter_name": "soil_moisture",
            "calibrated_value": 38.0,
            "unit": "%",
            "quality": "GOOD",
            "data_source": "SENSOR_MEASURED",
            "is_valid": True
        },
        {
            "sensor_type": "SOIL_TEMP",
            "parameter_name": "soil_temperature",
            "calibrated_value": 25.5,
            "unit": "celsius",
            "quality": "GOOD",
            "data_source": "SENSOR_MEASURED",
            "is_valid": True
        },
        {
            "sensor_type": "SOIL_PH",
            "parameter_name": "soil_ph",
            "calibrated_value": 7.2,
            "unit": "scale",
            "quality": "GOOD",
            "data_source": "SENSOR_MEASURED",
            "is_valid": True
        },
        {
            "sensor_type": "SOIL_EC",
            "parameter_name": "soil_ec",
            "calibrated_value": 0.55,
            "unit": "dS/m",
            "quality": "GOOD",
            "data_source": "SENSOR_MEASURED",
            "is_valid": True
        }
    ]

    res = await run_intelligence_from_telemetry(
        device_id="test-dev-001",
        field_id="test-fld-001",
        telemetry_measurements=telemetry_measurements,
        device_location=(19.26, 76.78),
        district="Parbhani",
        state="Maharashtra",
        soil_type="black",
        target_crop="cotton",
        is_synthetic=False
    )

    assert res["status"] == "SUCCESS"
    assert "telemetry_confidence_report" in res
    assert "irrigation_intelligence" in res
    assert "agricultural_intelligence" in res

    # Verify provenance report has measured vs unavailable
    conf = res["telemetry_confidence_report"]
    assert "field_provenances" in conf
    assert conf["field_provenances"]["soil_ph"]["source"] == "SENSOR_MEASURED"
    assert conf["field_provenances"]["nitrogen_kg_ha"]["source"] == "UNAVAILABLE"
