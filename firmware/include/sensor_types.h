#ifndef AGRISENSE_SENSOR_TYPES_H
#define AGRISENSE_SENSOR_TYPES_H

#include <stdint.h>
#include <string>

/**
 * Sensor Types matching Phase 01 backend schemas exactly.
 */
enum class SensorType {
    SOIL_MOISTURE,
    SOIL_TEMP,
    SOIL_PH,
    SOIL_EC,
    NITROGEN,
    PHOSPHORUS,
    POTASSIUM,
    AMBIENT_TEMP,
    AMBIENT_HUMIDITY,
    BATTERY_VOLTAGE,
    UNKNOWN
};

inline const char* sensorTypeToString(SensorType t) {
    switch (t) {
        case SensorType::SOIL_MOISTURE:     return "SOIL_MOISTURE";
        case SensorType::SOIL_TEMP:         return "SOIL_TEMP";
        case SensorType::SOIL_PH:           return "SOIL_PH";
        case SensorType::SOIL_EC:           return "SOIL_EC";
        case SensorType::NITROGEN:          return "NITROGEN";
        case SensorType::PHOSPHORUS:        return "PHOSPHORUS";
        case SensorType::POTASSIUM:         return "POTASSIUM";
        case SensorType::AMBIENT_TEMP:      return "AMBIENT_TEMP";
        case SensorType::AMBIENT_HUMIDITY:  return "AMBIENT_HUMIDITY";
        case SensorType::BATTERY_VOLTAGE:   return "BATTERY_VOLTAGE";
        default:                            return "UNKNOWN";
    }
}

/**
 * Quality levels for individual readings.
 */
enum class MeasurementQuality {
    GOOD,
    DEGRADED,
    INVALID,
    MISSING
};

inline const char* qualityToString(MeasurementQuality q) {
    switch (q) {
        case MeasurementQuality::GOOD:      return "GOOD";
        case MeasurementQuality::DEGRADED:  return "DEGRADED";
        case MeasurementQuality::INVALID:   return "INVALID";
        case MeasurementQuality::MISSING:   return "MISSING";
        default:                            return "MISSING";
    }
}

/**
 * Provenance tracking: distinguishes physical readings from estimates or simulations.
 */
enum class DataSource {
    SENSOR_MEASURED,
    CALCULATED,
    ML_ESTIMATED,
    EXTERNAL,
    FARMER_ENTERED,
    SYNTHETIC,
    UNAVAILABLE
};

inline const char* dataSourceToString(DataSource s) {
    switch (s) {
        case DataSource::SENSOR_MEASURED:   return "SENSOR_MEASURED";
        case DataSource::CALCULATED:        return "CALCULATED";
        case DataSource::ML_ESTIMATED:      return "ML_ESTIMATED";
        case DataSource::EXTERNAL:          return "EXTERNAL";
        case DataSource::FARMER_ENTERED:    return "FARMER_ENTERED";
        case DataSource::SYNTHETIC:         return "SYNTHETIC";
        case DataSource::UNAVAILABLE:       return "UNAVAILABLE";
        default:                            return "UNAVAILABLE";
    }
}

/**
 * Canonical sensor measurement structure.
 */
struct SensorMeasurement {
    SensorType sensor_type;
    std::string parameter_name;
    float raw_value;
    float calibrated_value;
    std::string unit;
    MeasurementQuality quality;
    DataSource data_source;
    std::string sensor_id;
    std::string calibration_version;
    bool is_valid;
    int64_t timestamp_epoch; // Epoch timestamp (seconds or ms)
};

/**
 * Node health diagnostics structure.
 */
struct DeviceDiagnostics {
    float battery_voltage;
    float battery_percent;
    int32_t signal_rssi;
    float signal_quality;
    uint32_t uptime_seconds;
    uint32_t free_memory_bytes;
    uint32_t failed_transmissions;
    uint32_t buffered_records;
};

#endif // AGRISENSE_SENSOR_TYPES_H
