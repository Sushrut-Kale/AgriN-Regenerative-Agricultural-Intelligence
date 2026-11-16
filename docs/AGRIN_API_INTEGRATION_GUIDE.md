# 🌐 AgriN API Integration Guide
**API Version:** 2.0.0  
**Base URL:** `http://localhost:8000/api` (Production: configurable via `FRONTEND_URL` / reverse proxy)  
**Document Code:** AGRIN-API-GUIDE-001  

---

## 1. Device Management Endpoints

### 1.1 Register New Hardware Node
- **Endpoint:** `POST /api/devices/register`
- **Status Code:** `201 Created`
- **Request:**
```bash
curl -X POST "http://localhost:8000/api/devices/register" \
     -H "Content-Type: application/json" \
     -d '{
       "farm_id": "farm-parbhani-01",
       "field_id": "field-cotton-north",
       "name": "AgriSense-Node-01",
       "hardware_profile": "ESP32-DevKit-V1-Standard",
       "firmware_version": "1.0.0",
       "wifi_ssid": "FarmNet-2G"
     }'
```
- **Response:**
```json
{
  "device_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "farm_id": "farm-parbhani-01",
  "field_id": "field-cotton-north",
  "name": "AgriSense-Node-01",
  "status": "UNREGISTERED",
  "api_key": "agrisense_sec_a8f9c1b2d3e4...",
  "created_at": "2026-11-17T00:00:00Z"
}
```

### 1.2 Get Device Health & Connectivity
- **Endpoint:** `GET /api/devices/{device_id}`
- **Response:**
```json
{
  "device_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "farm_id": "farm-parbhani-01",
  "field_id": "field-cotton-north",
  "name": "AgriSense-Node-01",
  "status": "ONLINE",
  "battery_voltage": 3.92,
  "battery_percent": 84.0,
  "signal_rssi": -65,
  "signal_quality": "GOOD",
  "firmware_version": "1.0.0",
  "last_seen_at": "2026-11-17T00:15:00Z",
  "is_active": true
}
```

### 1.3 Post Device Heartbeat Ping
- **Endpoint:** `POST /api/devices/{device_id}/heartbeat`
- **Status Code:** `201 Created`
- **Request:**
```bash
curl -X POST "http://localhost:8000/api/devices/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/heartbeat" \
     -H "Content-Type: application/json" \
     -d '{
       "battery_voltage": 3.85,
       "battery_percent": 80.0,
       "signal_rssi": -68,
       "uptime_seconds": 7200,
       "free_memory_bytes": 178000,
       "firmware_version": "1.0.0"
     }'
```

---

## 2. Telemetry Ingestion Endpoints

### 2.1 Ingest Telemetry Packet
- **Endpoint:** `POST /api/telemetry/ingest`
- **Status Code:** `201 Created`
- **Payload:** Complies with `TelemetryIngestRequest` (see `AGRIN_TELEMETRY_DATA_CONTRACT.md`)
- **Response:**
```json
{
  "telemetry_id": "7c12f0a8-8e6b-4b2a-bf34-61c0d8ef4920",
  "device_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "PROCESSED",
  "measurements_saved": 4,
  "duplicate": false,
  "message": "Telemetry accepted and persisted"
}
```

### 2.2 Retrieve Latest Telemetry
- **Endpoint:** `GET /api/telemetry/{device_id}/latest`
- **Response:** Returns the most recent valid readings for all attached sensors with quality and provenance badges.

### 2.3 Historical Telemetry
- **Endpoint:** `GET /api/telemetry/{device_id}/history?page=1&page_size=20`
- **Response:** Paginated array of historical telemetry packets with timestamps and sensor values.

---

## 3. Field Management Endpoints

### 3.1 Create Field / Agricultural Plot
- **Endpoint:** `POST /api/fields`
- **Request:**
```json
{
  "farm_id": "farm-parbhani-01",
  "name": "North Cotton Acre",
  "area_hectares": 2.5,
  "location_lat": 19.26,
  "location_lon": 76.78,
  "soil_type": "black",
  "irrigation_type": "drip"
}
```

### 3.2 List Fields by Farm
- **Endpoint:** `GET /api/fields/{farm_id}`
- **Response:** List of agricultural fields associated with the farm.
