"""
AgriN — IoT Database Models
============================
SQLAlchemy ORM tables for device management, telemetry, sensor configuration,
and heartbeats. Designed to coexist with existing FarmFriend tables in db.py.
All new tables use UUID primary keys.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    Integer, Text, JSON, Enum, ForeignKey, BigInteger
)
from sqlalchemy.orm import relationship

# Re-use the same Base and engine from db.py so create_all picks up everything
from backend.app.database.db import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class DeviceStatusEnum(str, PyEnum):
    ONLINE       = "ONLINE"
    OFFLINE      = "OFFLINE"
    DEGRADED     = "DEGRADED"
    UNREGISTERED = "UNREGISTERED"


class SensorTypeEnum(str, PyEnum):
    SOIL_MOISTURE      = "SOIL_MOISTURE"
    SOIL_TEMP          = "SOIL_TEMP"
    SOIL_PH            = "SOIL_PH"
    SOIL_EC            = "SOIL_EC"
    NITROGEN           = "NITROGEN"
    PHOSPHORUS         = "PHOSPHORUS"
    POTASSIUM          = "POTASSIUM"
    AMBIENT_TEMP       = "AMBIENT_TEMP"
    AMBIENT_HUMIDITY   = "AMBIENT_HUMIDITY"


class SensorInterfaceEnum(str, PyEnum):
    ADC    = "ADC"
    OneWire = "OneWire"
    RS485  = "RS485"
    I2C    = "I2C"
    SPI    = "SPI"


class MeasurementQualityEnum(str, PyEnum):
    GOOD     = "GOOD"
    DEGRADED = "DEGRADED"
    INVALID  = "INVALID"
    MISSING  = "MISSING"


class DataSourceEnum(str, PyEnum):
    SENSOR_MEASURED  = "SENSOR_MEASURED"
    CALCULATED       = "CALCULATED"
    ML_ESTIMATED     = "ML_ESTIMATED"
    EXTERNAL         = "EXTERNAL"
    FARMER_ENTERED   = "FARMER_ENTERED"
    SYNTHETIC        = "SYNTHETIC"
    UNAVAILABLE      = "UNAVAILABLE"

# Alias for canonical naming
DataSourceProvenance = DataSourceEnum


class ProcessingStatusEnum(str, PyEnum):
    PENDING   = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED    = "FAILED"
    DUPLICATE = "DUPLICATE"


# ── Helper ────────────────────────────────────────────────────────────────────

def _uuid():
    return str(uuid.uuid4())


# ── Tables ────────────────────────────────────────────────────────────────────

class Field(Base):
    """Agricultural field / plot."""
    __tablename__ = "iot_fields"

    field_id        = Column(String(36), primary_key=True, default=_uuid)
    farm_id         = Column(String(36), nullable=False, index=True)
    name            = Column(String(255), nullable=False)
    area_hectares   = Column(Float, nullable=True)
    location_lat    = Column(Float, nullable=True)
    location_lon    = Column(Float, nullable=True)
    soil_type       = Column(String(100), nullable=True)
    irrigation_type = Column(String(100), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relationships
    devices         = relationship("Device", back_populates="field", lazy="select")
    telemetry       = relationship("TelemetryRecord", back_populates="field", lazy="select")


class Device(Base):
    """IoT device (ESP32 node) registered on the platform."""
    __tablename__ = "iot_devices"

    device_id        = Column(String(36), primary_key=True, default=_uuid)
    farm_id          = Column(String(36), nullable=False, index=True)
    field_id         = Column(String(36), ForeignKey("iot_fields.field_id"), nullable=True, index=True)
    name             = Column(String(255), nullable=False)
    description      = Column(Text, nullable=True)
    firmware_version = Column(String(50), nullable=True)
    hardware_profile = Column(String(100), nullable=True)
    wifi_ssid        = Column(String(100), nullable=True)
    ip_address       = Column(String(45), nullable=True)
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    last_seen_at     = Column(DateTime, nullable=True)
    battery_voltage  = Column(Float, nullable=True)
    battery_percent  = Column(Float, nullable=True)
    signal_rssi      = Column(Integer, nullable=True)
    signal_quality   = Column(Float, nullable=True)
    status           = Column(
        Enum(DeviceStatusEnum, name="device_status_enum"),
        default=DeviceStatusEnum.UNREGISTERED,
        nullable=False
    )

    # Relationships
    field            = relationship("Field", back_populates="devices")
    sensors          = relationship("SensorConfig", back_populates="device", lazy="select")
    telemetry        = relationship("TelemetryRecord", back_populates="device", lazy="select")
    heartbeats       = relationship("DeviceHeartbeat", back_populates="device", lazy="select")
    measurements     = relationship("SensorMeasurement", back_populates="device", lazy="select")


class SensorConfig(Base):
    """Configuration and calibration parameters for a sensor attached to a device."""
    __tablename__ = "iot_sensor_configs"

    sensor_id           = Column(String(36), primary_key=True, default=_uuid)
    device_id           = Column(String(36), ForeignKey("iot_devices.device_id"), nullable=False, index=True)
    sensor_type         = Column(
        Enum(SensorTypeEnum, name="sensor_type_enum"),
        nullable=False
    )
    interface           = Column(
        Enum(SensorInterfaceEnum, name="sensor_interface_enum"),
        nullable=False
    )
    pin_config          = Column(JSON, nullable=True)
    calibration_params  = Column(JSON, nullable=True)
    calibration_version = Column(String(50), nullable=True)
    is_active           = Column(Boolean, default=True)
    last_calibrated_at  = Column(DateTime, nullable=True)

    device              = relationship("Device", back_populates="sensors")


class TelemetryRecord(Base):
    """One telemetry payload sent by a device."""
    __tablename__ = "iot_telemetry_records"

    telemetry_id      = Column(String(36), primary_key=True, default=_uuid)
    device_id         = Column(String(36), ForeignKey("iot_devices.device_id"), nullable=False, index=True)
    farm_id           = Column(String(36), nullable=False, index=True)
    field_id          = Column(String(36), ForeignKey("iot_fields.field_id"), nullable=True, index=True)
    timestamp         = Column(DateTime, nullable=False, index=True)
    received_at       = Column(DateTime, default=datetime.utcnow)
    payload_hash      = Column(String(64), nullable=True, index=True)   # SHA-256 hex for dedup
    firmware_version  = Column(String(50), nullable=True)
    sequence_number   = Column(BigInteger, nullable=True)
    measurements      = Column(JSON, nullable=True)   # raw array from device
    device_diagnostics = Column(JSON, nullable=True)  # battery, signal, uptime, free_memory
    processing_status = Column(
        Enum(ProcessingStatusEnum, name="processing_status_enum"),
        default=ProcessingStatusEnum.PENDING,
        nullable=False
    )

    device            = relationship("Device", back_populates="telemetry")
    field             = relationship("Field", back_populates="telemetry")
    sensor_measurements = relationship("SensorMeasurement", back_populates="telemetry", lazy="select")


class SensorMeasurement(Base):
    """Normalised, per-parameter measurement extracted from a telemetry record."""
    __tablename__ = "iot_sensor_measurements"

    measurement_id      = Column(String(36), primary_key=True, default=_uuid)
    telemetry_id        = Column(String(36), ForeignKey("iot_telemetry_records.telemetry_id"), nullable=False, index=True)
    device_id           = Column(String(36), ForeignKey("iot_devices.device_id"), nullable=False, index=True)
    sensor_type         = Column(String(50), nullable=False, index=True)
    parameter_name      = Column(String(100), nullable=False)
    raw_value           = Column(Float, nullable=True)
    calibrated_value    = Column(Float, nullable=True)
    unit                = Column(String(50), nullable=True)
    quality             = Column(
        Enum(MeasurementQualityEnum, name="measurement_quality_enum"),
        default=MeasurementQualityEnum.GOOD
    )
    data_source         = Column(
        Enum(DataSourceEnum, name="data_source_enum"),
        default=DataSourceEnum.SENSOR_MEASURED
    )
    is_valid            = Column(Boolean, default=True)
    error_code          = Column(String(50), nullable=True)
    calibration_version = Column(String(50), nullable=True)
    timestamp           = Column(DateTime, nullable=False, index=True)

    telemetry           = relationship("TelemetryRecord", back_populates="sensor_measurements")
    device              = relationship("Device", back_populates="measurements")


class DeviceHeartbeat(Base):
    """Periodic keep-alive signal from a device."""
    __tablename__ = "iot_device_heartbeats"

    heartbeat_id      = Column(String(36), primary_key=True, default=_uuid)
    device_id         = Column(String(36), ForeignKey("iot_devices.device_id"), nullable=False, index=True)
    timestamp         = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    battery_voltage   = Column(Float, nullable=True)
    signal_rssi       = Column(Integer, nullable=True)
    firmware_version  = Column(String(50), nullable=True)
    uptime_seconds    = Column(BigInteger, nullable=True)
    free_memory_bytes = Column(BigInteger, nullable=True)
    sensor_status     = Column(JSON, nullable=True)   # {sensor_type: "ok"|"error"|"missing"}

    device            = relationship("Device", back_populates="heartbeats")
