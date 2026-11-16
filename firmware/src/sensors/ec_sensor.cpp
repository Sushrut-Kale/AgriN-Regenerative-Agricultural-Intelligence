#include "ec_sensor.h"
#include <cmath>

#ifdef ARDUINO
#include <Arduino.h>
#include <Adafruit_ADS1X15.h>
extern Adafruit_ADS1115 g_ads;
extern bool g_ads_initialized;
#endif

EcSensor::EcSensor(const std::string& sensor_id, const EcCalibration& calib, uint8_t adc_channel)
    : SensorBase(sensor_id, SensorType::SOIL_EC),
      m_calib(calib),
      m_adc_channel(adc_channel),
      m_simulation_mode(false),
      m_simulated_voltage(0.55f) {}

bool EcSensor::init() {
    m_initialized = true;
    return true;
}

bool EcSensor::isAvailable() const {
    return m_initialized && (m_fault_count < 10);
}

void EcSensor::updateCalibration(const EcCalibration& calib) {
    m_calib = calib;
}

void EcSensor::setSimulatedReading(float voltage, bool enable_sim) {
    m_simulation_mode = enable_sim;
    m_simulated_voltage = voltage;
}

float EcSensor::readVoltage() {
    if (m_simulation_mode) {
        return m_simulated_voltage;
    }

#ifdef ARDUINO
    if (g_ads_initialized) {
        int16_t adc = g_ads.readADC_SingleEnded(m_adc_channel);
        return adc * 0.0001875f;
    } else {
        int raw = analogRead(32);
        return (raw / 4095.0f) * 3.3f;
    }
#else
    return m_simulated_voltage;
#endif
}

SensorMeasurement EcSensor::sample(float soil_temp) {
    SensorMeasurement m;
    m.sensor_type = SensorType::SOIL_EC;
    m.parameter_name = "soil_ec";
    m.unit = "dS/m";
    m.sensor_id = m_sensor_id;
    m.calibration_version = m_calib.version;
    m.data_source = m_simulation_mode ? DataSource::SYNTHETIC : DataSource::SENSOR_MEASURED;

    float voltage = readVoltage();
    m.raw_value = voltage;

    if (voltage < 0.01f || voltage > 3.25f) {
        m_fault_count++;
        m.calibrated_value = 0.0f;
        m.quality = MeasurementQuality::INVALID;
        m.is_valid = false;
        return m;
    }

    float ec = CalibrationMath::voltageToEc(voltage, m_calib, soil_temp);
    m.calibrated_value = std::round(ec * 100.0f) / 100.0f;
    m.quality = MeasurementQuality::GOOD;
    m.is_valid = true;
    m_fault_count = 0;

    return m;
}
