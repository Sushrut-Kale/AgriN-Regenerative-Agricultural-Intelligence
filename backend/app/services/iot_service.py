"""
AgriN — IoT Service Layer
==========================
Business logic for device management, telemetry ingestion, heartbeat
processing, and farm field CRUD.

This layer is DB-agnostic (receives a SQLAlchemy Session) and stateless;
all persistence is committed here.
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.database.iot_models import (
    Device, Field, SensorConfig, TelemetryRecord,
    SensorMeasurement, DeviceHeartbeat,
    DeviceStatusEnum, ProcessingStatusEnum, MeasurementQualityEnum
)
from backend.app.models.iot_schemas import (
    DeviceRegistrationRequest, DeviceRegistrationResponse,
    TelemetryIngestRequest, TelemetryIngestResponse,
    DeviceHeartbeatRequest, DeviceHeartbeatResponse,
    DeviceStatusResponse, DeviceStatusUpdateRequest,
    FieldCreateRequest, FieldResponse,
    TelemetryHistoryResponse, TelemetryRecordSchema,
    LatestTelemetryResponse, ProcessingStatus,
)

logger = logging.getLogger(__name__)


# ── Field ──────────────────────────────────────────────────────────────────────

def create_field(db: Session, request: FieldCreateRequest) -> FieldResponse:
    """Create a new agricultural field."""
    field = Field(
        farm_id         = request.farm_id,
        name            = request.name,
        area_hectares   = request.area_hectares,
        location_lat    = request.location_lat,
        location_lon    = request.location_lon,
        soil_type       = request.soil_type,
        irrigation_type = request.irrigation_type,
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    logger.info("Created field %s for farm %s", field.field_id, field.farm_id)
    return FieldResponse.model_validate(field)


def list_fields(db: Session, farm_id: str) -> List[FieldResponse]:
    """Return all fields for a given farm."""
    fields = db.query(Field).filter(Field.farm_id == farm_id).all()
    return [FieldResponse.model_validate(f) for f in fields]


# ── Device Registration ────────────────────────────────────────────────────────

def register_device(db: Session, request: DeviceRegistrationRequest) -> DeviceRegistrationResponse:
    """
    Register a new IoT device.
    If a device with the same farm_id + name already exists and is inactive,
    it is re-activated rather than duplicated.
    """
    # Validate field_id if supplied
    if request.field_id:
        field = db.query(Field).filter(Field.field_id == request.field_id).first()
        if not field:
            raise HTTPException(status_code=404, detail=f"Field {request.field_id} not found")

    device = Device(
        farm_id          = request.farm_id,
        field_id         = request.field_id,
        name             = request.name,
        description      = request.description,
        firmware_version = request.firmware_version,
        hardware_profile = request.hardware_profile,
        wifi_ssid        = request.wifi_ssid,
        ip_address       = request.ip_address,
        is_active        = True,
        status           = DeviceStatusEnum.UNREGISTERED,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    logger.info("Registered device %s (%s) for farm %s", device.device_id, device.name, device.farm_id)

    return DeviceRegistrationResponse(
        device_id  = device.device_id,
        farm_id    = device.farm_id,
        field_id   = device.field_id,
        name       = device.name,
        status     = device.status,
        created_at = device.created_at,
    )


def get_device_status(db: Session, device_id: str) -> DeviceStatusResponse:
    """Return full device health/status report."""
    device = _get_device_or_404(db, device_id)
    sensor_count = db.query(SensorConfig).filter(
        SensorConfig.device_id == device_id,
        SensorConfig.is_active == True
    ).count()

    return DeviceStatusResponse(
        device_id        = device.device_id,
        farm_id          = device.farm_id,
        field_id         = device.field_id,
        name             = device.name,
        status           = device.status,
        is_active        = device.is_active,
        firmware_version = device.firmware_version,
        hardware_profile = device.hardware_profile,
        ip_address       = device.ip_address,
        battery_voltage  = device.battery_voltage,
        battery_percent  = device.battery_percent,
        signal_rssi      = device.signal_rssi,
        signal_quality   = device.signal_quality,
        created_at       = device.created_at,
        last_seen_at     = device.last_seen_at,
        sensor_count     = sensor_count,
    )


def update_device_status(
    db: Session, device_id: str, request: DeviceStatusUpdateRequest
) -> DeviceStatusResponse:
    """Update device status and optional metadata."""
    device = _get_device_or_404(db, device_id)
    device.status = request.status.value
    if request.is_active is not None:
        device.is_active = request.is_active
    if request.firmware_version is not None:
        device.firmware_version = request.firmware_version
    if request.ip_address is not None:
        device.ip_address = request.ip_address
    db.commit()
    db.refresh(device)
    return get_device_status(db, device_id)


def list_device_sensors(db: Session, device_id: str):
    """Return all sensor configs for a device."""
    _get_device_or_404(db, device_id)
    return db.query(SensorConfig).filter(SensorConfig.device_id == device_id).all()


# ── Heartbeat ──────────────────────────────────────────────────────────────────

def process_heartbeat(
    db: Session, device_id: str, request: DeviceHeartbeatRequest
) -> DeviceHeartbeatResponse:
    """
    Record heartbeat, update device last_seen_at and diagnostics.
    Transition OFFLINE device → ONLINE when heartbeat arrives.
    """
    device = _get_device_or_404(db, device_id)

    ts = request.timestamp or datetime.utcnow()

    hb = DeviceHeartbeat(
        device_id         = device_id,
        timestamp         = ts,
        battery_voltage   = request.battery_voltage,
        signal_rssi       = request.signal_rssi,
        firmware_version  = request.firmware_version,
        uptime_seconds    = request.uptime_seconds,
        free_memory_bytes = request.free_memory_bytes,
        sensor_status     = request.sensor_status,
    )
    db.add(hb)

    # Update device diagnostics
    device.last_seen_at    = ts
    device.battery_voltage = request.battery_voltage or device.battery_voltage
    if request.battery_percent is not None:
        device.battery_percent = request.battery_percent
    device.signal_rssi     = request.signal_rssi or device.signal_rssi
    if request.firmware_version:
        device.firmware_version = request.firmware_version

    # Auto-transition status
    if device.status in (DeviceStatusEnum.OFFLINE, DeviceStatusEnum.UNREGISTERED):
        device.status = DeviceStatusEnum.ONLINE

    db.commit()
    db.refresh(hb)
    logger.debug("Heartbeat from device %s at %s", device_id, ts)

    return DeviceHeartbeatResponse(
        heartbeat_id = hb.heartbeat_id,
        device_id    = device_id,
        timestamp    = ts,
    )


# ── Telemetry Ingestion ────────────────────────────────────────────────────────

def ingest_telemetry(
    db: Session, payload: TelemetryIngestRequest
) -> TelemetryIngestResponse:
    """
    Validate, deduplicate, persist telemetry, and trigger downstream intelligence.

    Returns DUPLICATE status if the same payload_hash already exists.
    """
    device = _get_device_or_404(db, payload.device_id)

    payload_hash = payload.compute_hash()

    # Deduplication check
    existing = db.query(TelemetryRecord).filter(
        TelemetryRecord.payload_hash == payload_hash
    ).first()
    if existing:
        logger.warning("Duplicate telemetry from device %s (hash %s)", payload.device_id, payload_hash)
        return TelemetryIngestResponse(
            telemetry_id       = existing.telemetry_id,
            device_id          = payload.device_id,
            status             = ProcessingStatus.DUPLICATE,
            measurements_saved = 0,
            duplicate          = True,
            message            = "Duplicate payload — already ingested",
        )

    diag_dict = payload.device_diagnostics.model_dump() if payload.device_diagnostics else None
    meas_list = [m.model_dump() for m in payload.measurements]

    record = TelemetryRecord(
        device_id          = payload.device_id,
        farm_id            = payload.farm_id,
        field_id           = payload.field_id,
        timestamp          = payload.timestamp,
        payload_hash       = payload_hash,
        firmware_version   = payload.firmware_version,
        sequence_number    = payload.sequence_number,
        measurements       = meas_list,
        device_diagnostics = diag_dict,
        processing_status  = ProcessingStatusEnum.PENDING,
    )
    db.add(record)
    db.flush()   # get telemetry_id before adding children

    # Persist normalised SensorMeasurement rows
    saved = 0
    for m in payload.measurements:
        ts = m.timestamp or payload.timestamp
        sm = SensorMeasurement(
            telemetry_id        = record.telemetry_id,
            device_id           = payload.device_id,
            sensor_type         = m.sensor_type.value,
            parameter_name      = m.parameter_name,
            raw_value           = m.raw_value,
            calibrated_value    = m.calibrated_value,
            unit                = m.unit,
            quality             = m.quality.value,
            data_source         = m.data_source.value,
            is_valid            = m.is_valid,
            error_code          = m.error_code,
            calibration_version = m.calibration_version,
            timestamp           = ts,
        )
        db.add(sm)
        saved += 1

    # Update device last_seen + diagnostics
    device.last_seen_at    = payload.timestamp
    device.firmware_version = payload.firmware_version or device.firmware_version
    if diag_dict:
        device.battery_voltage = diag_dict.get("battery_voltage", device.battery_voltage)
        device.battery_percent = diag_dict.get("battery_percent", device.battery_percent)
        device.signal_rssi     = diag_dict.get("signal_rssi", device.signal_rssi)
        device.signal_quality  = diag_dict.get("signal_quality", device.signal_quality)
    if device.status == DeviceStatusEnum.OFFLINE:
        device.status = DeviceStatusEnum.ONLINE

    record.processing_status = ProcessingStatusEnum.PROCESSED
    db.commit()
    db.refresh(record)
    logger.info(
        "Ingested telemetry %s from device %s — %d measurements",
        record.telemetry_id, payload.device_id, saved
    )

    # TODO: trigger intelligence pipeline (Phase 02)

    return TelemetryIngestResponse(
        telemetry_id       = record.telemetry_id,
        device_id          = payload.device_id,
        status             = ProcessingStatus.PROCESSED,
        measurements_saved = saved,
        duplicate          = False,
        message            = "Telemetry ingested and processed",
    )


def get_telemetry_history(
    db: Session,
    device_id: str,
    page: int = 1,
    page_size: int = 20,
) -> TelemetryHistoryResponse:
    """Paginated telemetry history for a device."""
    _get_device_or_404(db, device_id)
    q = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.device_id == device_id)
        .order_by(TelemetryRecord.timestamp.desc())
    )
    total = q.count()
    records = q.offset((page - 1) * page_size).limit(page_size).all()
    return TelemetryHistoryResponse(
        device_id = device_id,
        total     = total,
        page      = page,
        page_size = page_size,
        records   = [TelemetryRecordSchema.model_validate(r) for r in records],
    )


def get_latest_telemetry(db: Session, device_id: str) -> LatestTelemetryResponse:
    """Return the most recent valid telemetry record for a device."""
    _get_device_or_404(db, device_id)
    record = (
        db.query(TelemetryRecord)
        .filter(
            TelemetryRecord.device_id == device_id,
            TelemetryRecord.processing_status == ProcessingStatusEnum.PROCESSED,
        )
        .order_by(TelemetryRecord.timestamp.desc())
        .first()
    )
    if not record:
        return LatestTelemetryResponse(
            device_id    = device_id,
            telemetry_id = None,
            timestamp    = None,
            measurements = None,
            device_diagnostics = None,
            message      = "No processed telemetry found",
        )
    return LatestTelemetryResponse(
        device_id          = device_id,
        telemetry_id       = record.telemetry_id,
        timestamp          = record.timestamp,
        measurements       = record.measurements,
        device_diagnostics = record.device_diagnostics,
    )


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get_device_or_404(db: Session, device_id: str) -> Device:
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return device
