#include "temperature_sensor.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
static OneWire* g_oneWire = nullptr;
static DallasTemperature* g_dallasSensors = nullptr;
#endif

TemperatureSensor::TemperatureSensor(const std::string& sensor_id, uint8_t gpio_pin)
    : SensorBase(sensor_id, SensorType::SOIL_TEMP),
      m_gpio_pin(gpio_pin),
      m_simulation_mode(false),
      m_simulated_temp(24.5f),
      m_last_valid_temp(25.0f) {}

bool TemperatureSensor::init() {
#ifdef ARDUINO
    if (!g_oneWire) {
        g_oneWire = new OneWire(m_gpio_pin);
        g_dallasSensors = new DallasTemperature(g_oneWire);
        g_dallasSensors->begin();
        g_dallasSensors->setWaitForConversion(true);
    }
    m_initialized = (g_dallasSensors->getDeviceCount() > 0);
#else
    m_initialized = true;
#endif
    return m_initialized;
}

bool TemperatureSensor::isAvailable() const {
    return m_initialized && (m_fault_count < 5);
}

void TemperatureSensor::setSimulatedReading(float temp_c, bool enable_sim) {
    m_simulation_mode = enable_sim;
    m_simulated_temp = temp_c;
}

float TemperatureSensor::readPhysicalTemp() {
    if (m_simulation_mode) {
        return m_simulated_temp;
    }

#ifdef ARDUINO
    if (g_dallasSensors) {
        g_dallasSensors->requestTemperatures();
        float tempC = g_dallasSensors->getTempCByIndex(0);
        return tempC;
    }
    return -127.0f;
#else
    return m_simulated_temp;
#endif
}

SensorMeasurement TemperatureSensor::sample(float /*unused*/) {
    SensorMeasurement m;
    m.sensor_type = SensorType::SOIL_TEMP;
    m.parameter_name = "soil_temperature";
    m.unit = "celsius";
    m.sensor_id = m_sensor_id;
    m.calibration_version = "factory-ds18b20";
    m.data_source = m_simulation_mode ? DataSource::SYNTHETIC : DataSource::SENSOR_MEASURED;

    float tempC = readPhysicalTemp();
    m.raw_value = tempC;

    // DS18B20 Fault Detection:
    // -127.0°C indicates disconnected OneWire data line or missing pull-up resistor.
    // +85.0°C indicates reading before conversion completed (power-on state).
    if (tempC <= -120.0f || (std::abs(tempC - 85.0f) < 0.01f && m_fault_count > 0) || tempC > 65.0f) {
        m_fault_count++;
        m.calibrated_value = m_last_valid_temp;
        m.quality = MeasurementQuality::INVALID;
        m.is_valid = false;
        return m;
    }

    m.calibrated_value = tempC;
    m.quality = MeasurementQuality::GOOD;
    m.is_valid = true;
    m_last_valid_temp = tempC;
    m_fault_count = 0;

    return m;
}
