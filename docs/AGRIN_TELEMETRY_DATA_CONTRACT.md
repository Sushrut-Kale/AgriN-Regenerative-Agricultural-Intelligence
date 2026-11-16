# 📜 AgriN Canonical Telemetry Data Contract
**Standard:** AgriSense Canonical Agricultural Data Model  
**Version:** 1.0.0  
**Document Code:** AGRIN-CONTRACT-001  

---

## 1. Specification Overview

This document specifies the exact JSON wire protocol between the edge firmware (ESP32), API ingestion gateway (`/api/telemetry/ingest`), database persistence, and agricultural intelligence consumers.

---

## 2. Telemetry Ingestion Payload (`TelemetryIngestRequest`)

```json
{
  "device_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "farm_id": "farm-parbhani-01",
  "field_id": "field-cotton-north",
  "timestamp": "2026-11-17T00:00:00Z",
  "sequence_number": 1042,
  "firmware_version": "1.0.0",
  "is_synthetic": false,
  "measurements": [
    {
      "sensor_type": "SOIL_MOISTURE",
      "parameter_name": "soil_moisture",
      "raw_value": 1850.0,
      "calibrated_value": 41.5,
      "unit": "%",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED",
      "sensor_id": "probe-moist-01",
      "calibration_version": "1.0.0",
      "is_valid": true
    },
    {
      "sensor_type": "SOIL_TEMP",
      "parameter_name": "soil_temperature",
      "raw_value": 24.8,
      "calibrated_value": 24.8,
      "unit": "celsius",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED",
      "sensor_id": "ds18b20-01",
      "calibration_version": "1.0.0",
      "is_valid": true
    },
    {
      "sensor_type": "SOIL_PH",
      "parameter_name": "soil_ph",
      "raw_value": 2.45,
      "calibrated_value": 6.85,
      "unit": "scale",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED",
      "sensor_id": "ph-probe-01",
      "calibration_version": "1.0.0",
      "is_valid": true
    },
    {
      "sensor_type": "SOIL_EC",
      "parameter_name": "soil_ec",
      "raw_value": 620.0,
      "calibrated_value": 0.62,
      "unit": "dS/m",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED",
      "sensor_id": "ec-probe-01",
      "calibration_version": "1.0.0",
      "is_valid": true
    }
  ],
  "device_diagnostics": {
    "battery_voltage": 3.95,
    "battery_percent": 86.0,
    "signal_rssi": -64,
    "signal_quality": 88.0,
    "uptime_seconds": 18450,
    "free_memory_bytes": 178200
  }
}
```

---

## 3. Strict Agronomic Boundary Rules

The API ingestion gateway validates all incoming measurements against strict physical and agronomic thresholds. Out-of-bounds readings are rejected with HTTP 422:

| Parameter | Unit | Allowed Physical Range | Rejection Criteria | Action on Failure |
| :--- | :---: | :---: | :--- | :--- |
| **`soil_moisture`** | `%` | $0.0 \le x \le 100.0$ | $< 0.0$ or $> 100.0$ | HTTP 422 Unprocessable |
| **`soil_temperature`** | `°C` | $-10.0 \le x \le 60.0$ | $< -10.0$ or $> 60.0$ | HTTP 422 Unprocessable |
| **`soil_ph`** | `scale` | $3.0 \le x \le 10.0$ | $< 3.0$ or $> 10.0$ | HTTP 422 Unprocessable |
| **`soil_ec`** | `dS/m` | $0.0 \le x \le 20.0$ | $< 0.0$ or $> 20.0$ | HTTP 422 Unprocessable |
| **`nitrogen`** | `kg/ha` | $0.0 \le x \le 800.0$ | $< 0.0$ or $> 800.0$ | HTTP 422 Unprocessable |
| **`phosphorus`** | `kg/ha` | $0.0 \le x \le 300.0$ | $< 0.0$ or $> 300.0$ | HTTP 422 Unprocessable |
| **`potassium`** | `kg/ha` | $0.0 \le x \le 1200.0$| $< 0.0$ or $> 1200.0$| HTTP 422 Unprocessable |

---

## 4. Heartbeat Payload (`DeviceHeartbeatRequest`)

Sent by the device every 60–120 seconds to report connectivity and battery status:

```json
{
  "battery_voltage": 3.84,
  "battery_percent": 78.0,
  "signal_rssi": -65,
  "uptime_seconds": 3600,
  "free_memory_bytes": 182000,
  "firmware_version": "1.0.0",
  "sensor_status": {
    "SOIL_MOISTURE": "OK",
    "SOIL_TEMP": "OK",
    "SOIL_PH": "OK",
    "SOIL_EC": "DEGRADED",
    "NPK": "MISSING"
  }
}
```
