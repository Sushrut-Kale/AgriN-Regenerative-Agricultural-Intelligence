#ifndef AGRISENSE_TELEMETRY_H
#define AGRISENSE_TELEMETRY_H

#include <string>
#include <vector>
#include <stdint.h>
#include "sensor_types.h"

/**
 * Top-level Telemetry Packet structure matching Phase 01 TelemetryIngestRequest
 */
struct TelemetryPacket {
    std::string device_id;
    std::string farm_id;
    std::string field_id;
    std::string timestamp_iso;
    uint32_t sequence_number;
    std::string firmware_version;
    bool is_synthetic = false; // Strictly false for physical sensor readings

    std::vector<SensorMeasurement> measurements;
    DeviceDiagnostics diagnostics;

    /**
     * Serializes telemetry packet into canonical JSON matching backend API.
     */
    std::string toJson() const;
};

/**
 * Device Heartbeat Packet structure matching Phase 01 DeviceHeartbeatRequest
 */
struct HeartbeatPacket {
    float battery_voltage;
    float battery_percent;
    int32_t signal_rssi;
    uint32_t uptime_seconds;
    uint32_t free_memory_bytes;
    std::string firmware_version;
    std::vector<std::pair<std::string, std::string>> sensor_statuses; // { "SOIL_MOISTURE": "OK" }

    std::string toJson() const;
};

#endif // AGRISENSE_TELEMETRY_H
