#include "telemetry.h"
#include <sstream>
#include <iomanip>

#ifdef ARDUINO
#include <ArduinoJson.h>
#endif

std::string TelemetryPacket::toJson() const {
#ifdef ARDUINO
    JsonDocument doc;

    doc["device_id"] = device_id;
    doc["farm_id"] = farm_id;
    if (!field_id.empty()) {
        doc["field_id"] = field_id;
    } else {
        doc["field_id"] = nullptr;
    }
    doc["timestamp"] = timestamp_iso;
    doc["sequence_number"] = sequence_number;
    doc["firmware_version"] = firmware_version;
    doc["is_synthetic"] = is_synthetic;

    JsonArray measArray = doc["measurements"].to<JsonArray>();
    for (const auto& m : measurements) {
        JsonObject mObj = measArray.add<JsonObject>();
        mObj["sensor_type"] = sensorTypeToString(m.sensor_type);
        mObj["parameter_name"] = m.parameter_name;
        mObj["raw_value"] = m.raw_value;
        mObj["calibrated_value"] = m.calibrated_value;
        mObj["unit"] = m.unit;
        mObj["quality"] = qualityToString(m.quality);
        mObj["data_source"] = dataSourceToString(m.data_source);
        mObj["sensor_id"] = m.sensor_id;
        mObj["calibration_version"] = m.calibration_version;
        mObj["is_valid"] = m.is_valid;
    }

    JsonObject diagObj = doc["device_diagnostics"].to<JsonObject>();
    diagObj["battery_voltage"] = diagnostics.battery_voltage;
    diagObj["battery_percent"] = diagnostics.battery_percent;
    diagObj["signal_rssi"] = diagnostics.signal_rssi;
    diagObj["signal_quality"] = diagnostics.signal_quality;
    diagObj["uptime_seconds"] = diagnostics.uptime_seconds;
    diagObj["free_memory_bytes"] = diagnostics.free_memory_bytes;

    std::string output;
    serializeJson(doc, output);
    return output;
#else
    // Native / Host fallback serialization (std::ostringstream)
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(2);
    ss << "{\n";
    ss << "  \"device_id\": \"" << device_id << "\",\n";
    ss << "  \"farm_id\": \"" << farm_id << "\",\n";
    if (!field_id.empty()) {
        ss << "  \"field_id\": \"" << field_id << "\",\n";
    }
    ss << "  \"timestamp\": \"" << timestamp_iso << "\",\n";
    ss << "  \"sequence_number\": " << sequence_number << ",\n";
    ss << "  \"firmware_version\": \"" << firmware_version << "\",\n";
    ss << "  \"is_synthetic\": " << (is_synthetic ? "true" : "false") << ",\n";
    ss << "  \"measurements\": [\n";

    for (size_t i = 0; i < measurements.size(); ++i) {
        const auto& m = measurements[i];
        ss << "    {\n";
        ss << "      \"sensor_type\": \"" << sensorTypeToString(m.sensor_type) << "\",\n";
        ss << "      \"parameter_name\": \"" << m.parameter_name << "\",\n";
        ss << "      \"raw_value\": " << m.raw_value << ",\n";
        ss << "      \"calibrated_value\": " << m.calibrated_value << ",\n";
        ss << "      \"unit\": \"" << m.unit << "\",\n";
        ss << "      \"quality\": \"" << qualityToString(m.quality) << "\",\n";
        ss << "      \"data_source\": \"" << dataSourceToString(m.data_source) << "\",\n";
        ss << "      \"sensor_id\": \"" << m.sensor_id << "\",\n";
        ss << "      \"calibration_version\": \"" << m.calibration_version << "\",\n";
        ss << "      \"is_valid\": " << (m.is_valid ? "true" : "false") << "\n";
        ss << "    }" << (i + 1 < measurements.size() ? "," : "") << "\n";
    }
    ss << "  ],\n";
    ss << "  \"device_diagnostics\": {\n";
    ss << "    \"battery_voltage\": " << diagnostics.battery_voltage << ",\n";
    ss << "    \"battery_percent\": " << diagnostics.battery_percent << ",\n";
    ss << "    \"signal_rssi\": " << diagnostics.signal_rssi << ",\n";
    ss << "    \"signal_quality\": " << diagnostics.signal_quality << ",\n";
    ss << "    \"uptime_seconds\": " << diagnostics.uptime_seconds << ",\n";
    ss << "    \"free_memory_bytes\": " << diagnostics.free_memory_bytes << "\n";
    ss << "  }\n";
    ss << "}";
    return ss.str();
#endif
}

std::string HeartbeatPacket::toJson() const {
#ifdef ARDUINO
    JsonDocument doc;
    doc["battery_voltage"] = battery_voltage;
    doc["battery_percent"] = battery_percent;
    doc["signal_rssi"] = signal_rssi;
    doc["uptime_seconds"] = uptime_seconds;
    doc["free_memory_bytes"] = free_memory_bytes;
    doc["firmware_version"] = firmware_version;

    JsonObject statusObj = doc["sensor_status"].to<JsonObject>();
    for (const auto& kv : sensor_statuses) {
        statusObj[kv.first] = kv.second;
    }

    std::string output;
    serializeJson(doc, output);
    return output;
#else
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(2);
    ss << "{\n";
    ss << "  \"battery_voltage\": " << battery_voltage << ",\n";
    ss << "  \"battery_percent\": " << battery_percent << ",\n";
    ss << "  \"signal_rssi\": " << signal_rssi << ",\n";
    ss << "  \"uptime_seconds\": " << uptime_seconds << ",\n";
    ss << "  \"free_memory_bytes\": " << free_memory_bytes << ",\n";
    ss << "  \"firmware_version\": \"" << firmware_version << "\",\n";
    ss << "  \"sensor_status\": {\n";
    for (size_t i = 0; i < sensor_statuses.size(); ++i) {
        ss << "    \"" << sensor_statuses[i].first << "\": \"" << sensor_statuses[i].second << "\""
           << (i + 1 < sensor_statuses.size() ? "," : "") << "\n";
    }
    ss << "  }\n";
    ss << "}";
    return ss.str();
#endif
}
