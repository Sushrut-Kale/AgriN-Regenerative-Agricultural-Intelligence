#ifndef AGRISENSE_DEVICE_CONFIG_H
#define AGRISENSE_DEVICE_CONFIG_H

#include <string>
#include <stdint.h>
#include "calibration.h"

/**
 * Runtime device configuration structure stored in persistent NVS memory.
 */
struct DeviceConfig {
    // Device Identity & Association
    std::string device_id = "agrisense-dev-001";
    std::string api_key = "agrisense_sec_default";
    std::string farm_id = "farm-parbhani-01";
    std::string field_id = "field-cotton-north";
    std::string device_name = "AgriSense-Field-Probe";
    std::string firmware_version = "2.0.0";
    std::string hardware_profile = "ESP32-DevKit-V1-Standard";

    // Network Connectivity
    std::string wifi_ssid = "AgriNet-Farm-WiFi";
    std::string wifi_password = "";
    std::string api_base_url = "http://192.168.1.100:8000";
    std::string telemetry_endpoint = "/api/telemetry/ingest";
    std::string heartbeat_endpoint = "/api/devices"; // appended with /{device_id}/heartbeat

    // Operational Intervals (in seconds)
    uint32_t sampling_interval_sec = 60;
    uint32_t telemetry_interval_sec = 300;
    uint32_t heartbeat_interval_sec = 120;

    // Sensor Enable / Disable Flags
    bool enable_moisture = true;
    bool enable_temperature = true;
    bool enable_ph = true;
    bool enable_ec = true;
    bool enable_npk = false; // Disabled by default until RS485 Modbus sensor is physically attached
    bool enable_simulation_mode = false; // Strict separation: false = Real hardware acquisition

    // Calibration Parameters
    MoistureCalibration calib_moisture;
    PhCalibration calib_ph;
    EcCalibration calib_ec;
};

#endif // AGRISENSE_DEVICE_CONFIG_H
