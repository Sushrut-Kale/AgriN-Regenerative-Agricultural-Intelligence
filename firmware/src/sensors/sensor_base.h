#ifndef AGRISENSE_SENSOR_BASE_H
#define AGRISENSE_SENSOR_BASE_H

#include <string>
#include <vector>
#include "sensor_types.h"

/**
 * Abstract Base Class for all physical sensor drivers.
 * Guarantees modularity: a failure or disconnection in one sensor never crashes the system.
 */
class SensorBase {
public:
    SensorBase(const std::string& sensor_id, SensorType type)
        : m_sensor_id(sensor_id), m_type(type), m_initialized(false), m_fault_count(0) {}

    virtual ~SensorBase() = default;

    virtual bool init() = 0;
    virtual bool isAvailable() const = 0;
    virtual SensorMeasurement sample(float ambient_or_soil_temp = 25.0f) = 0;
    virtual void resetFaults() { m_fault_count = 0; }

    const std::string& getSensorId() const { return m_sensor_id; }
    SensorType getSensorType() const { return m_type; }
    bool isInitialized() const { return m_initialized; }
    uint32_t getFaultCount() const { return m_fault_count; }

protected:
    std::string m_sensor_id;
    SensorType m_type;
    bool m_initialized;
    uint32_t m_fault_count;
};

#endif // AGRISENSE_SENSOR_BASE_H
