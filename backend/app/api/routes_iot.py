"""
AgriN — IoT API Routes
========================
Endpoints for device registration, telemetry ingestion, heartbeat,
and field management.

All routes are prefixed with /api in main.py.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.db import get_db
from backend.app.models.iot_schemas import (
    DeviceRegistrationRequest, DeviceRegistrationResponse,
    DeviceStatusResponse, DeviceStatusUpdateRequest,
    DeviceHeartbeatRequest, DeviceHeartbeatResponse,
    TelemetryIngestRequest, TelemetryIngestResponse,
    TelemetryHistoryResponse, LatestTelemetryResponse,
    FieldCreateRequest, FieldResponse,
    SensorConfigSchema,
)
from backend.app.services import iot_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Device endpoints ──────────────────────────────────────────────────────────

@router.post(
    "/devices/register",
    response_model=DeviceRegistrationResponse,
    status_code=201,
    summary="Register a new IoT device",
    tags=["IoT — Devices"],
)
def register_device(
    request: DeviceRegistrationRequest,
    db: Session = Depends(get_db),
):
    """Register a new ESP32 / IoT device on the platform."""
    return iot_service.register_device(db, request)


@router.get(
    "/devices/{device_id}",
    response_model=DeviceStatusResponse,
    summary="Get device status",
    tags=["IoT — Devices"],
)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
):
    """Return full device health/status information."""
    return iot_service.get_device_status(db, device_id)


@router.put(
    "/devices/{device_id}/status",
    response_model=DeviceStatusResponse,
    summary="Update device status",
    tags=["IoT — Devices"],
)
def update_device_status(
    device_id: str,
    request: DeviceStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update the operational status of a device."""
    return iot_service.update_device_status(db, device_id, request)


@router.post(
    "/devices/{device_id}/heartbeat",
    response_model=DeviceHeartbeatResponse,
    status_code=201,
    summary="Receive device heartbeat",
    tags=["IoT — Devices"],
)
def receive_heartbeat(
    device_id: str,
    request: DeviceHeartbeatRequest,
    db: Session = Depends(get_db),
):
    """Record a periodic keep-alive heartbeat from an IoT device."""
    return iot_service.process_heartbeat(db, device_id, request)


@router.get(
    "/devices/{device_id}/sensors",
    response_model=List[SensorConfigSchema],
    summary="List sensor configs for a device",
    tags=["IoT — Devices"],
)
def list_device_sensors(
    device_id: str,
    db: Session = Depends(get_db),
):
    """Return all sensor configurations attached to a device."""
    sensors = iot_service.list_device_sensors(db, device_id)
    return [SensorConfigSchema.model_validate(s) for s in sensors]


# ── Telemetry endpoints ───────────────────────────────────────────────────────

@router.post(
    "/telemetry/ingest",
    response_model=TelemetryIngestResponse,
    status_code=201,
    summary="Ingest telemetry payload from device",
    tags=["IoT — Telemetry"],
)
def ingest_telemetry(
    payload: TelemetryIngestRequest,
    db: Session = Depends(get_db),
):
    """
    Primary ingestion endpoint for ESP32 sensor telemetry.
    Validates, deduplicates, persists, and queues for intelligence processing.
    """
    return iot_service.ingest_telemetry(db, payload)


@router.get(
    "/telemetry/{device_id}/history",
    response_model=TelemetryHistoryResponse,
    summary="Paginated telemetry history",
    tags=["IoT — Telemetry"],
)
def telemetry_history(
    device_id: str,
    page:      int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=200, description="Records per page"),
    db: Session = Depends(get_db),
):
    """Return paginated telemetry history for a device."""
    return iot_service.get_telemetry_history(db, device_id, page, page_size)


@router.get(
    "/telemetry/{device_id}/latest",
    response_model=LatestTelemetryResponse,
    summary="Latest telemetry reading",
    tags=["IoT — Telemetry"],
)
def latest_telemetry(
    device_id: str,
    db: Session = Depends(get_db),
):
    """Return the most recent valid telemetry record for a device."""
    return iot_service.get_latest_telemetry(db, device_id)


# ── Field endpoints ───────────────────────────────────────────────────────────

@router.post(
    "/fields",
    response_model=FieldResponse,
    status_code=201,
    summary="Create a new agricultural field",
    tags=["IoT — Fields"],
)
def create_field(
    request: FieldCreateRequest,
    db: Session = Depends(get_db),
):
    """Create an agricultural field linked to a farm."""
    return iot_service.create_field(db, request)


@router.get(
    "/fields/{farm_id}",
    response_model=List[FieldResponse],
    summary="List fields for a farm",
    tags=["IoT — Fields"],
)
def list_fields(
    farm_id: str,
    db: Session = Depends(get_db),
):
    """Return all fields belonging to a farm."""
    return iot_service.list_fields(db, farm_id)
