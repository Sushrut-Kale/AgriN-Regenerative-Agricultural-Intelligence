"""
AgriN — IoT Pydantic Schemas
==============================
Strict request/response models for device management, telemetry ingestion,
heartbeat, and field management endpoints.

Sensor value ranges are enforced per agronomic constraints; impossible values
are rejected at the API boundary.
"""

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums (mirror iot_models.py for schema layer) ─────────────────────────────

class DeviceStatus(str, Enum):
    ONLINE       = "ONLINE"
    OFFLINE      = "OFFLINE"
    DEGRADED     = "DEGRADED"
    UNREGISTERED = "UNREGISTERED"


class SensorType(str, Enum):
    SOIL_MOISTURE    = "SOIL_MOISTURE"
    SOIL_TEMP        = "SOIL_TEMP"
    SOIL_PH          = "SOIL_PH"
    SOIL_EC          = "SOIL_EC"
    NITROGEN         = "NITROGEN"
    PHOSPHORUS       = "PHOSPHORUS"
    POTASSIUM        = "POTASSIUM"
    AMBIENT_TEMP     = "AMBIENT_TEMP"
    AMBIENT_HUMIDITY = "AMBIENT_HUMIDITY"


class SensorInterface(str, Enum):
    ADC     = "ADC"
    OneWire = "OneWire"
    RS485   = "RS485"
    I2C     = "I2C"
    SPI     = "SPI"


class MeasurementQuality(str, Enum):
    GOOD     = "GOOD"
    DEGRADED = "DEGRADED"
    INVALID  = "INVALID"
    MISSING  = "MISSING"


class DataSource(str, Enum):
    SENSOR_MEASURED = "SENSOR_MEASURED"
    CALCULATED      = "CALCULATED"
    ML_ESTIMATED    = "ML_ESTIMATED"
    EXTERNAL        = "EXTERNAL"
    FARMER_ENTERED  = "FARMER_ENTERED"
    SYNTHETIC       = "SYNTHETIC"
    UNAVAILABLE     = "UNAVAILABLE"


class ProcessingStatus(str, Enum):
    PENDING   = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED    = "FAILED"
    DUPLICATE = "DUPLICATE"


# ── Sensor value ranges for strict validation ──────────────────────────────────
# (parameter_name → (min, max))
SENSOR_VALID_RANGES: Dict[str, tuple] = {
    "soil_moisture":    (0.0,  100.0),   # volumetric water content %
    "soil_temperature": (-10.0, 60.0),   # °C
    "soil_ph":          (3.0,  10.0),
    "soil_ec":          (0.0,  20.0),    # dS/m
    "nitrogen":         (0.0,  800.0),   # kg/ha
    "phosphorus":       (0.0,  300.0),
    "potassium":        (0.0,  1200.0),
    "temperature":      (-20.0, 60.0),   # °C ambient
    "humidity":         (0.0,  100.0),   # % RH
}


# ── Device Registration ────────────────────────────────────────────────────────

class DeviceRegistrationRequest(BaseModel):
    farm_id:          str  = Field(..., description="Farm/session UUID this device belongs to")
    field_id:         Optional[str] = Field(None, description="Field UUID (if already created)")
    name:             str  = Field(..., min_length=1, max_length=255)
    description:      Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_profile: Optional[str] = None
    wifi_ssid:        Optional[str] = None
    ip_address:       Optional[str] = None


class DeviceRegistrationResponse(BaseModel):
    device_id:   str
    farm_id:     str
    field_id:    Optional[str]
    name:        str
    status:      DeviceStatus
    created_at:  datetime
    message:     str = "Device registered successfully"


# ── Field ──────────────────────────────────────────────────────────────────────

class FieldCreateRequest(BaseModel):
    farm_id:        str   = Field(..., description="Farm/session UUID")
    name:           str   = Field(..., min_length=1, max_length=255)
    area_hectares:  Optional[float] = Field(None, ge=0.01, le=100_000)
    location_lat:   Optional[float] = Field(None, ge=-90.0,  le=90.0)
    location_lon:   Optional[float] = Field(None, ge=-180.0, le=180.0)
    soil_type:      Optional[str] = None
    irrigation_type: Optional[str] = None


class FieldResponse(BaseModel):
    field_id:       str
    farm_id:        str
    name:           str
    area_hectares:  Optional[float]
    location_lat:   Optional[float]
    location_lon:   Optional[float]
    soil_type:      Optional[str]
    irrigation_type: Optional[str]
    created_at:     datetime

    class Config:
        from_attributes = True


# ── Sensor Config ──────────────────────────────────────────────────────────────

class SensorConfigSchema(BaseModel):
    sensor_id:          str
    device_id:          str
    sensor_type:        SensorType
    interface:          SensorInterface
    pin_config:         Optional[Dict[str, Any]] = None
    calibration_params: Optional[Dict[str, Any]] = None
    calibration_version: Optional[str] = None
    is_active:          bool
    last_calibrated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Sensor Measurement ─────────────────────────────────────────────────────────

class SensorMeasurementSchema(BaseModel):
    """
    Per-parameter measurement.
    Provenance rules:
      - SENSOR_MEASURED may not coexist with SYNTHETIC in the same telemetry record.
      - raw_value is required when data_source == SENSOR_MEASURED.
    """
    sensor_type:        SensorType
    parameter_name:     str
    raw_value:          Optional[float] = None
    calibrated_value:   Optional[float] = None
    unit:               Optional[str]   = None
    quality:            MeasurementQuality = MeasurementQuality.GOOD
    data_source:        DataSource         = DataSource.SENSOR_MEASURED
    is_valid:           bool               = True
    error_code:         Optional[str]      = None
    calibration_version: Optional[str]     = None
    timestamp:          Optional[datetime] = None

    @field_validator("calibrated_value")
    @classmethod
    def validate_range(cls, v: Optional[float], info) -> Optional[float]:
        if v is None:
            return v
        param = info.data.get("parameter_name", "")
        if param in SENSOR_VALID_RANGES:
            lo, hi = SENSOR_VALID_RANGES[param]
            if not (lo <= v <= hi):
                raise ValueError(
                    f"calibrated_value {v} out of valid range [{lo}, {hi}] for '{param}'"
                )
        return v

    @field_validator("raw_value")
    @classmethod
    def validate_raw_range(cls, v: Optional[float], info) -> Optional[float]:
        if v is None:
            return v
        param = info.data.get("parameter_name", "")
        if param in SENSOR_VALID_RANGES:
            lo, hi = SENSOR_VALID_RANGES[param]
            # Allow ±20 % tolerance on raw value (before calibration)
            margin = (hi - lo) * 0.20
            if not ((lo - margin) <= v <= (hi + margin)):
                raise ValueError(
                    f"raw_value {v} implausible for '{param}' (expected roughly [{lo}, {hi}])"
                )
        return v


# ── Device Diagnostics ─────────────────────────────────────────────────────────

class DeviceDiagnosticsSchema(BaseModel):
    battery_voltage:   Optional[float] = Field(None, ge=0.0, le=5.0)
    battery_percent:   Optional[float] = Field(None, ge=0.0, le=100.0)
    signal_rssi:       Optional[int]   = Field(None, ge=-120, le=0)
    signal_quality:    Optional[float] = Field(None, ge=0.0, le=100.0)
    uptime_seconds:    Optional[int]   = None
    free_memory_bytes: Optional[int]   = None


# ── Telemetry Ingestion ────────────────────────────────────────────────────────

class TelemetryIngestRequest(BaseModel):
    """
    JSON payload sent by the ESP32 to POST /api/telemetry/ingest.
    """
    device_id:        str
    farm_id:          str
    field_id:         Optional[str]  = None
    timestamp:        datetime
    firmware_version: Optional[str]  = None
    sequence_number:  Optional[int]  = Field(None, ge=0)
    measurements:     List[SensorMeasurementSchema] = Field(..., min_length=1)
    device_diagnostics: Optional[DeviceDiagnosticsSchema] = None

    @model_validator(mode="after")
    def no_mixed_provenance(self):
        """SENSOR_MEASURED and SYNTHETIC must never coexist in one payload."""
        sources = {m.data_source for m in self.measurements}
        if DataSource.SENSOR_MEASURED in sources and DataSource.SYNTHETIC in sources:
            raise ValueError(
                "Telemetry payload must not mix SENSOR_MEASURED and SYNTHETIC provenance."
            )
        return self

    def compute_hash(self) -> str:
        """Deterministic SHA-256 for deduplication."""
        payload = {
            "device_id":       self.device_id,
            "timestamp":       self.timestamp.isoformat(),
            "sequence_number": self.sequence_number,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()


class TelemetryIngestResponse(BaseModel):
    telemetry_id:       str
    device_id:          str
    status:             ProcessingStatus
    measurements_saved: int
    duplicate:          bool = False
    message:            str


# ── Heartbeat ──────────────────────────────────────────────────────────────────

class DeviceHeartbeatRequest(BaseModel):
    battery_voltage:   Optional[float] = Field(None, ge=0.0, le=5.0)
    battery_percent:   Optional[float] = Field(None, ge=0.0, le=100.0)
    signal_rssi:       Optional[int]   = Field(None, ge=-120, le=0)
    firmware_version:  Optional[str]   = None
    uptime_seconds:    Optional[int]   = Field(None, ge=0)
    free_memory_bytes: Optional[int]   = Field(None, ge=0)
    sensor_status:     Optional[Dict[str, str]] = None  # {sensor_type: "ok"|"error"|"missing"}
    timestamp:         Optional[datetime]       = None


class DeviceHeartbeatResponse(BaseModel):
    heartbeat_id: str
    device_id:    str
    timestamp:    datetime
    message:      str = "Heartbeat recorded"


# ── Device Status ──────────────────────────────────────────────────────────────

class DeviceStatusResponse(BaseModel):
    device_id:        str
    farm_id:          str
    field_id:         Optional[str]
    name:             str
    status:           DeviceStatus
    is_active:        bool
    firmware_version: Optional[str]
    hardware_profile: Optional[str]
    ip_address:       Optional[str]
    battery_voltage:  Optional[float]
    battery_percent:  Optional[float]
    signal_rssi:      Optional[int]
    signal_quality:   Optional[float]
    created_at:       datetime
    last_seen_at:     Optional[datetime]
    sensor_count:     int = 0

    class Config:
        from_attributes = True


class DeviceStatusUpdateRequest(BaseModel):
    status:           DeviceStatus
    is_active:        Optional[bool]  = None
    firmware_version: Optional[str]   = None
    ip_address:       Optional[str]   = None


# ── Telemetry History ──────────────────────────────────────────────────────────

class TelemetryRecordSchema(BaseModel):
    telemetry_id:       str
    device_id:          str
    farm_id:            str
    field_id:           Optional[str]
    timestamp:          datetime
    received_at:        datetime
    firmware_version:   Optional[str]
    sequence_number:    Optional[int]
    processing_status:  ProcessingStatus
    measurements:       Optional[List[Dict[str, Any]]]
    device_diagnostics: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class TelemetryHistoryResponse(BaseModel):
    device_id:   str
    total:       int
    page:        int
    page_size:   int
    records:     List[TelemetryRecordSchema]


class LatestTelemetryResponse(BaseModel):
    device_id:    str
    telemetry_id: Optional[str]
    timestamp:    Optional[datetime]
    measurements: Optional[List[Dict[str, Any]]]
    device_diagnostics: Optional[Dict[str, Any]]
    message:      str = "OK"
