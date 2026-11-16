# AGRISENSE Firmware Architecture Specification
**Project:** AgriN — Regenerative Agricultural Intelligence  
**Document Version:** 1.0.0  
**Target Firmware Version:** 1.0.0  
**Status:** DRAFT — Hardware team must fill all `TBD_BY_HARDWARE_TEAM` placeholders before physical device fabrication.

---

## 1. Hardware Platform

| Parameter | Value |
|-----------|-------|
| Target MCU | ESP32 DevKit V1 (Espressif ESP32-WROOM-32) |
| CPU | Dual-core Xtensa LX6, 240 MHz |
| RAM | 520 KB SRAM |
| Flash | 4 MB (SPI flash, internal) |
| GPIO Logic Level | **3.3 V** — NEVER expose GPIO pins to 5 V without bidirectional level-shifting |
| ADC | 12-bit SAR, up to 18 channels (use ADS1115 external ADC for precision) |
| UART | 3× hardware UART (UART0 = debug/USB, UART1/UART2 = sensor buses) |
| I²C | 1× hardware I²C (SDA/SCL configurable) |
| SPI | 2× SPI buses |
| Wi-Fi | 802.11 b/g/n 2.4 GHz, WPA/WPA2 |
| Bluetooth | BT 4.2 / BLE 4.2 (reserved for future OTA/pairing) |
| Power Supply | 3.3 V regulated from 5 V boost converter (Li-ion + solar panel via MPPT module) |
| Operating Temperature | –40 °C to +85 °C |

> [!CAUTION]
> The ESP32 GPIO pins operate at 3.3 V logic. Directly connecting any 5 V signal without a level-shifter (e.g., TXS0108E, BSS138) will permanently damage the MCU. The RS-485 MAX3485 module must also be powered from 3.3 V or use a 5 V variant with level-shifted DE/RE control pins.

---

## 2. Sensor Interface Table

> [!IMPORTANT]
> All GPIO pin assignments are **TBD by the hardware team**. The firmware uses `hardware_profile.json` to load pin assignments at runtime — do not hard-code GPIO numbers in production firmware.

| Sensor | Interface Type | GPIO Pins | Voltage Level | Protocol / Library | Notes |
|--------|---------------|-----------|---------------|--------------------|-------|
| Capacitive Soil Moisture (e.g., DFROBOT SEN0193 or Chirp!) | ADC via ADS1115 | I²C SDA/SCL — `TBD_BY_HARDWARE_TEAM` | 3.3 V | I²C (ADS1115) | ADS1115 addr 0x48 default; channel A0. Calibrate dry/wet values per sensor unit. |
| DS18B20 Soil Temperature | OneWire | `TBD_BY_HARDWARE_TEAM` (single GPIO) | 3.3 V | OneWire + Dallas Temperature library | 4.7 kΩ pull-up to 3.3 V on data line. Parasite power NOT recommended for long cable runs. |
| pH Probe (analog probe + pH signal conditioner board) | ADC via ADS1115 | I²C SDA/SCL shared | 3.3 V | I²C (ADS1115) | ADS1115 channel A1. 2-point calibration with pH 4.0 and pH 7.0 buffer solutions required. |
| EC Sensor (electrical conductivity, analog probe) | ADC via ADS1115 | I²C SDA/SCL shared | 3.3 V | I²C (ADS1115) | ADS1115 channel A2. Temperature-compensated reading (cross-reference DS18B20). |
| NPK Sensor (RS-485 Modbus RTU) | RS-485 via MAX3485 | DE/RE GPIO `TBD`; UART RX `TBD`; UART TX `TBD` | 3.3 V (MAX3485) or 5 V w/ level shift | Modbus RTU @ 9600 baud | Obtain Modbus register map from sensor datasheet. `enabled: false` by default until register map confirmed. |
| ADS1115 ADC Module | I²C | SDA `TBD`; SCL `TBD` | 3.3 V | I²C @ 100–400 kHz | ADDR pin → GND for 0x48. Up to 4 analog channels multiplexed. |
| Solar MPPT / Battery Monitor (optional) | I²C or ADC | `TBD_BY_HARDWARE_TEAM` | 3.3 V | INA219 or voltage divider | Battery voltage divider must not exceed 3.3 V at full charge on ADC pin. |

---

## 3. Firmware State Machine

```
 ┌─────────┐
 │  BOOT   │  Power-on / reset / watchdog recovery
 └────┬────┘
      │  Load hardware_profile.json from SPIFFS/LittleFS
      │  Initialize serial debug (115200 baud)
      ▼
 ┌─────────────┐
 │ WIFI_CONNECT│  Connect to configured SSID (up to 3 retries × 10 s)
 └──────┬──────┘  On failure after retries → ERROR state → deep sleep 60 s → BOOT
        │
        ▼
 ┌──────────────┐
 │ DEVICE_AUTH  │  POST /api/devices/{device_id}/heartbeat with api_key
 └──────┬───────┘  HTTP 401 → ERROR (invalid credentials, halt)
        │          HTTP 200 → continue
        ▼
 ┌──────────────┐
 │ SENSOR_INIT  │  Initialize all enabled sensors per hardware_profile.json
 └──────┬───────┘  Record per-sensor init status (GOOD / FAILED / SKIPPED)
        │          At least one sensor must init successfully to proceed
        ▼
 ┌──────────────────┐
 │ MEASUREMENT_CYCLE│  Read all enabled sensors
 └────────┬─────────┘  Apply calibration transforms
          │            Record raw + calibrated values + quality flags
          │            Increment sequence_number (persisted in RTC memory)
          ▼
 ┌──────────┐
 │ TRANSMIT │  Build telemetry JSON payload
 └────┬─────┘  POST /api/telemetry/ingest
      │        HTTP 200/201 → success → continue
      │        HTTP 4xx → log error code → continue (don't discard data)
      │        HTTP 5xx / timeout → retry up to 2× with 5 s back-off
      │        Persistent failure → store to SPIFFS queue (offline buffer)
      ▼
 ┌────────────┐
 │ SLEEP/IDLE │  Enter light_sleep or deep_sleep per hardware_profile.json
 └────────────┘  Wake after measurement_interval_seconds (default 300 s)
                 → Back to MEASUREMENT_CYCLE (skip BOOT/WIFI if WiFi stays connected)
```

### State Transition Error Rules

| State | Error Condition | Recovery Action |
|-------|----------------|-----------------|
| WIFI_CONNECT | Cannot connect after 3 retries | Deep sleep 60 s, then BOOT |
| DEVICE_AUTH | HTTP 401 Unauthorized | Halt and blink error LED; require reflash |
| DEVICE_AUTH | Network timeout | Retry 2×; then sleep and try next cycle |
| SENSOR_INIT | All sensors failed | Log ERROR_SENSOR_ALL_FAILED; transmit diagnostics-only payload |
| TRANSMIT | HTTP 5xx / timeout | Retry 2× with 5 s back-off; queue to SPIFFS on failure |
| TRANSMIT | Offline buffer full | Drop oldest record (rolling buffer, max 50 records) |

---

## 4. Telemetry JSON Schema

The ESP32 **MUST** POST the following JSON body to `POST /api/telemetry/ingest`.  
Content-Type: `application/json`  
Authentication: `api_key` field inside the payload (no separate Authorization header required by default).

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "agrisense-device-api-key-here",
  "firmware_version": "1.0.0",
  "sequence_number": 12345,
  "timestamp_utc": "2026-11-17T00:00:00Z",
  "measurements": [
    {
      "sensor_type": "SOIL_MOISTURE",
      "sensor_id": "moisture-01",
      "raw_value": 2048.0,
      "calibrated_value": 42.3,
      "unit": "percent",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED"
    },
    {
      "sensor_type": "SOIL_TEMP",
      "sensor_id": "temperature-01",
      "raw_value": 24.5,
      "calibrated_value": 24.5,
      "unit": "celsius",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED"
    },
    {
      "sensor_type": "SOIL_PH",
      "sensor_id": "ph-01",
      "raw_value": 1.84,
      "calibrated_value": 6.8,
      "unit": "pH",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED"
    },
    {
      "sensor_type": "SOIL_EC",
      "sensor_id": "ec-01",
      "raw_value": 1.52,
      "calibrated_value": 1.45,
      "unit": "dS/m",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED"
    },
    {
      "sensor_type": "NITROGEN",
      "sensor_id": "npk-01",
      "raw_value": 42.0,
      "calibrated_value": 42.0,
      "unit": "mg/kg",
      "quality": "GOOD",
      "data_source": "SENSOR_MEASURED"
    }
  ],
  "diagnostics": {
    "battery_voltage": 3.72,
    "battery_percent": 78,
    "signal_rssi": -65,
    "uptime_seconds": 3600,
    "free_memory_bytes": 180000
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | string (UUID) | ✅ | Device UUID assigned during registration |
| `api_key` | string | ✅ | Device-specific API key from registration response |
| `firmware_version` | string (semver) | ✅ | Firmware version string, e.g. `"1.0.0"` |
| `sequence_number` | integer | ✅ | Monotonically increasing counter per device (stored in RTC memory, survives light sleep) |
| `timestamp_utc` | string (ISO 8601) | ✅ | UTC timestamp of measurement start. Use NTP-synced time. |
| `measurements` | array | ✅ | Array of 1–10 measurement objects |
| `measurements[].sensor_type` | string enum | ✅ | One of: `SOIL_MOISTURE`, `SOIL_TEMP`, `SOIL_PH`, `SOIL_EC`, `NITROGEN`, `PHOSPHORUS`, `POTASSIUM`, `AMBIENT_TEMP`, `AMBIENT_HUMIDITY` |
| `measurements[].sensor_id` | string | ✅ | Hardware sensor identifier (e.g. `"moisture-01"`) |
| `measurements[].raw_value` | float | ✅ | Raw ADC count or sensor output before calibration |
| `measurements[].calibrated_value` | float | ✅ | Calibrated engineering-unit value |
| `measurements[].unit` | string | ✅ | Engineering unit string |
| `measurements[].quality` | string enum | ✅ | `GOOD`, `DEGRADED`, `INVALID`, `MISSING` |
| `measurements[].data_source` | string enum | ✅ | `SENSOR_MEASURED` for real sensor data; `SYNTHETIC` for simulator |
| `diagnostics` | object | ✅ | Device health metrics |
| `diagnostics.battery_voltage` | float | ✅ | Battery voltage in volts (e.g. 3.72) |
| `diagnostics.battery_percent` | integer | ✅ | Estimated state-of-charge 0–100 |
| `diagnostics.signal_rssi` | integer | ✅ | Wi-Fi RSSI in dBm (negative number) |
| `diagnostics.uptime_seconds` | integer | ✅ | Seconds since last hard reset |
| `diagnostics.free_memory_bytes` | integer | ✅ | Free heap memory in bytes |

### Quality Flag Rules

| Quality | Condition |
|---------|-----------|
| `GOOD` | Reading within calibrated range, no sensor errors |
| `DEGRADED` | Reading near limits, or sensor warm-up incomplete |
| `INVALID` | Reading outside physical range, or calibration not performed |
| `MISSING` | Sensor not responding / disabled |

---

## 5. Calibration Procedures

### 5.1 Soil Moisture Calibration (Capacitive Sensor)

Capacitive moisture sensors output an ADC voltage inversely proportional to soil moisture. Each physical sensor unit has slightly different dry/wet endpoints.

**Required materials:** Dry soil sample (oven-dried), saturated wet soil sample.

**Procedure:**
1. Power the ESP32 with sensor connected to ADS1115 channel A0.
2. Place sensor in **completely dry soil** (or in air). Read ADC raw value → record as `raw_min_dry` in `hardware_profile.json`.
3. Place sensor in **saturated soil** (at field capacity, not waterlogged). Read ADC raw value → record as `raw_max_wet`.
4. The firmware linearly interpolates: `moisture_percent = map(raw, raw_min_dry, raw_max_wet, 0, 100)`.
5. Values outside the calibrated range are clamped to [0, 100] and flagged `DEGRADED`.

> [!NOTE]
> `raw_min_dry` will typically be **higher** than `raw_max_wet` for capacitive sensors (higher capacitance = higher water content = lower ADC output on most analog-output boards). Verify polarity with your specific module.

### 5.2 pH Probe 2-Point Calibration

**Required materials:** pH 4.00 buffer solution, pH 7.00 buffer solution, deionized water rinse.

**Procedure:**
1. Rinse probe with deionized water, then immerse in **pH 7.00 buffer**. Wait 60 s for stabilisation.
2. Record ADS1115 A1 voltage → `ph7_voltage` in `hardware_profile.json`.
3. Rinse probe, immerse in **pH 4.00 buffer**. Wait 60 s.
4. Record ADS1115 A1 voltage → `ph4_voltage`.
5. Firmware computes slope: `slope = (7.0 - 4.0) / (ph7_voltage - ph4_voltage)`.
6. Live pH: `pH = 7.0 + slope * (measured_voltage - ph7_voltage)`.
7. Cross-check with a third buffer (pH 6.86 or 9.18) — error must be < 0.1 pH units.

**Recalibration interval:** Every 30 days or after sensor storage > 7 days.

### 5.3 EC (Electrical Conductivity) Calibration

**Required materials:** KCl standard solution at 1.413 dS/m (25 °C), or 2.76 dS/m for high-range fields.

**Procedure:**
1. Rinse EC probe with deionized water.
2. Immerse in **1.413 dS/m KCl standard** at 25 °C (temperature-compensated).
3. Record ADS1115 A2 raw voltage → store as `ec_reference_voltage` and `ec_reference_value_dSm`.
4. Firmware applies: `EC_dSm = (measured_voltage / ec_reference_voltage) * ec_reference_value_dSm * temperature_compensation_factor`.
5. Temperature compensation: `compensation_factor = 1 + 0.019 * (temperature_C - 25)`.

> [!TIP]
> Always perform EC calibration at known temperature (DS18B20 reading). Store both `ec_reference_voltage` and `ec_reference_temperature_C` in `hardware_profile.json` for firmware cross-correction.

---

## 6. Firmware Error Codes

The firmware embeds an error code in the telemetry payload `diagnostics` object when an error occurs.  
Backend should log these and surface them in device status dashboards.

| Code | Symbol | Meaning | Action |
|------|--------|---------|--------|
| `E000` | `OK` | No error | — |
| `E001` | `ERROR_WIFI_TIMEOUT` | WiFi connect timed out | Check SSID/password; retry next cycle |
| `E002` | `ERROR_NTP_SYNC_FAILED` | NTP time sync failed | Timestamp may be inaccurate; backend should flag |
| `E003` | `ERROR_AUTH_REJECTED` | Backend returned HTTP 401 | Reflash device with correct api_key |
| `E004` | `ERROR_SENSOR_MOISTURE_FAIL` | Moisture sensor init failed | Check I²C wiring; check ADS1115 power |
| `E005` | `ERROR_SENSOR_TEMP_FAIL` | DS18B20 not found on OneWire | Check pull-up resistor and GPIO pin |
| `E006` | `ERROR_SENSOR_PH_FAIL` | pH ADC reading out of range | Check probe connection; recalibrate |
| `E007` | `ERROR_SENSOR_EC_FAIL` | EC ADC reading out of range | Check probe connection; recalibrate |
| `E008` | `ERROR_SENSOR_NPK_FAIL` | Modbus RTU no response | Check RS-485 wiring, baud rate, address |
| `E009` | `ERROR_SENSOR_ALL_FAILED` | All sensors failed init | Hardware fault; transmit diagnostics-only payload |
| `E010` | `ERROR_TRANSMIT_FAILED` | HTTP POST failed after retries | Check server reachability; payload queued locally |
| `E011` | `ERROR_SPIFFS_QUEUE_FULL` | Offline buffer at capacity | Oldest records dropped; check connectivity |
| `E012` | `ERROR_CALIBRATION_MISSING` | Sensor has no calibration data | Load factory calibration or perform field calibration |
| `E013` | `ERROR_LOW_BATTERY` | Battery voltage < 3.3 V | Device will reduce measurement frequency |
| `E014` | `ERROR_WATCHDOG_RESET` | Watchdog timer triggered reset | Log prior crash; check for infinite loops |
| `E015` | `ERROR_OTA_FAILED` | OTA firmware update failed | Device retains previous firmware; retry |

Error codes are reported as an optional `error_codes` array in `diagnostics`:

```json
"diagnostics": {
  "battery_voltage": 3.72,
  "battery_percent": 78,
  "signal_rssi": -65,
  "uptime_seconds": 3600,
  "free_memory_bytes": 180000,
  "error_codes": ["E002", "E006"]
}
```

---

## 7. OTA (Over-The-Air) Firmware Update

- OTA updates are delivered via the backend API endpoint: `GET /api/firmware/latest?device_id={id}`
- Device checks for updates on every DEVICE_AUTH cycle.
- OTA uses ESP32's native `Update` library with dual-partition rollback.
- If OTA partition write fails or the new firmware fails its first heartbeat, the device automatically rolls back to the previous partition.
- OTA is gated by `firmware_version` field: backend only pushes update if device version < latest available.

---

## 8. Offline Buffering

- When the backend is unreachable, the ESP32 stores telemetry payloads to SPIFFS/LittleFS as JSON files.
- Maximum buffer: **50 records** (rolling, oldest dropped first when full).
- On next successful connection, the device flushes buffered records in chronological order before sending new data.
- Each buffered record retains its original `timestamp_utc` and `sequence_number`.

---

## 9. Power Management

| Mode | Current Draw (est.) | Use Case |
|------|---------------------|----------|
| Active (WiFi TX) | ~240 mA peak | Transmit phase only |
| Active (sensors) | ~50–80 mA | Measurement cycle |
| Light Sleep | ~0.8 mA | Between measurement cycles (WiFi preserved) |
| Deep Sleep | ~10 µA | Extended low-power intervals (WiFi dropped) |

**Default:** `light_sleep` between 5-minute measurement cycles.  
**Low-battery mode** (< 3.3 V): Switch to `deep_sleep`, extend interval to 15 minutes.

---

## 10. TBD Items — Hardware Team Action Required

| # | Item | File | Field |
|---|------|------|-------|
| 1 | Soil moisture sensor GPIO (SDA/SCL for ADS1115) | `hardware_profile.json` | `sensors.soil_moisture` → I²C pins |
| 2 | Moisture sensor dry ADC reading | `hardware_profile.json` | `sensors.soil_moisture.raw_min_dry` |
| 3 | Moisture sensor wet ADC reading | `hardware_profile.json` | `sensors.soil_moisture.raw_max_wet` |
| 4 | DS18B20 OneWire GPIO pin | `hardware_profile.json` | `sensors.soil_temperature.gpio_pin` |
| 5 | pH probe voltage at pH 4.00 | `hardware_profile.json` | `sensors.soil_ph.calibration_points.ph4_voltage` |
| 6 | pH probe voltage at pH 7.00 | `hardware_profile.json` | `sensors.soil_ph.calibration_points.ph7_voltage` |
| 7 | EC reference voltage at 1.413 dS/m | `hardware_profile.json` | `sensors.soil_ec.ec_reference_voltage` |
| 8 | NPK sensor DE/RE GPIO pin | `hardware_profile.json` | `sensors.npk.gpio_de_re` |
| 9 | NPK sensor UART RX GPIO pin | `hardware_profile.json` | `sensors.npk.gpio_rx` |
| 10 | NPK sensor UART TX GPIO pin | `hardware_profile.json` | `sensors.npk.gpio_tx` |
| 11 | NPK sensor Modbus address | `hardware_profile.json` | `sensors.npk.modbus_address` |
| 12 | NPK sensor Modbus register map | Sensor datasheet | (Needed before enabling NPK) |
| 13 | WiFi SSID & password | `hardware_profile.json` → device flash | `wifi.ssid`, `wifi.password` |
| 14 | Backend server IP/hostname | `hardware_profile.json` | `backend.api_base_url` |
| 15 | ADS1115 I²C SDA/SCL GPIO pins | `hardware_profile.json` | (shared by moisture/pH/EC) |

---

*Document maintained by: AgriN Firmware Team*  
*Contact: post hardware-confirmed values to project repository as a PR updating `hardware_profile.json`*
