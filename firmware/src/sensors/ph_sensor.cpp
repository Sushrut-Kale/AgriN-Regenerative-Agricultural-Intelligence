#include "ph_sensor.h"
#include <cmath>

#ifdef ARDUINO
#include <Arduino.h>
#include <Adafruit_ADS1X15.h>
extern Adafruit_ADS1115 g_ads;
extern bool g_ads_initialized;
#endif

PhSensor::PhSensor(const std::string& sensor_id, const PhCalibration& calib, uint8_t adc_channel)
    : SensorBase(sensor_id, SensorType::SOIL_PH),
      m_calib(calib),
      m_adc_channel(adc_channel),
      m_simulation_mode(false),
      m_simulated_voltage(2.45f) {}

bool PhSensor::init() {
    m_initialized = true;
    return true;
}

bool PhSensor::isAvailable() const {
    return m_initialized && (m_fault_count < 10);
}

void PhSensor::updateCalibration(const PhCalibration& calib) {
    m_calib = calib;
}

void PhSensor::setSimulatedReading(float voltage, bool enable_sim) {
    m_simulation_mode = enable_sim;
    m_simulated_voltage = voltage;
}

float PhSensor::readVoltage() {
    if (m_simulation_mode) {
        return m_simulated_voltage;
    }

#ifdef ARDUINO
    if (g_ads_initialized) {
        int16_t adc = g_ads.readADC_SingleEnded(m_adc_channel);
        // Default ADS1115 gain is 2/3 (0.1875 mV per LSB)
        return adc * 0.0001875f;
    } else {
        int raw = analogRead(35);
        return (raw / 4095.0f) * 3.3f;
    }
#else
    return m_simulated_voltage;
#endif
}

SensorMeasurement PhSensor::sample(float soil_temp) {
    SensorMeasurement m;
    m.sensor_type = SensorType::SOIL_PH;
    m.parameter_name = "soil_ph";
    m.unit = "scale";
    m.sensor_id = m_sensor_id;
    m.calibration_version = m_calib.version;
    m.data_source = m_simulation_mode ? DataSource::SYNTHETIC : DataSource::SENSOR_MEASURED;

    float voltage = readVoltage();
    m.raw_value = voltage;

    // Fault detection:
    // Voltage < 0.1V: Sensor unplugged or shorted to GND
    // Voltage > 3.25V: BNC cable severed or rail short
    if (voltage < 0.10f || voltage > 3.25f) {
        m_fault_count++;
        m.calibrated_value = 7.0f;
        m.quality = MeasurementQuality::INVALID;
        m.is_valid = false;
        return m;
    }

    // Apply temperature-compensated calibration
    float ph = CalibrationMath::voltageToPh(voltage, m_calib, soil_temp);
    m.calibrated_value = std::round(ph * 100.0f) / 100.0f;
    m.quality = MeasurementQuality::GOOD;
    m.is_valid = true;
    m_fault_count = 0;

    return m;
}
