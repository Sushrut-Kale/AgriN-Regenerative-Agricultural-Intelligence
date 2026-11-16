#include "moisture_sensor.h"
#include <cmath>

#ifdef ARDUINO
#include <Arduino.h>
#include <Adafruit_ADS1X15.h>
extern Adafruit_ADS1115 g_ads;
extern bool g_ads_initialized;
#endif

MoistureSensor::MoistureSensor(const std::string& sensor_id, const MoistureCalibration& calib, uint8_t adc_channel)
    : SensorBase(sensor_id, SensorType::SOIL_MOISTURE),
      m_calib(calib),
      m_adc_channel(adc_channel),
      m_ema_filtered_raw(0.0f),
      m_has_first_sample(false),
      m_simulation_mode(false),
      m_simulated_raw(2100.0f) {}

bool MoistureSensor::init() {
    m_initialized = true;
    m_has_first_sample = false;
    return true;
}

bool MoistureSensor::isAvailable() const {
    return m_initialized && (m_fault_count < 10);
}

void MoistureSensor::updateCalibration(const MoistureCalibration& calib) {
    m_calib = calib;
}

void MoistureSensor::setSimulatedReading(float raw_val, bool enable_sim) {
    m_simulation_mode = enable_sim;
    m_simulated_raw = raw_val;
}

float MoistureSensor::readRawAdc() {
    if (m_simulation_mode) {
        return m_simulated_raw;
    }

#ifdef ARDUINO
    if (g_ads_initialized) {
        // Read 16-bit single-ended from ADS1115 channel
        int16_t adc = g_ads.readADC_SingleEnded(m_adc_channel);
        return static_cast<float>(adc);
    } else {
        // Fallback to internal ESP32 12-bit ADC (GPIO 34 or 35)
        return static_cast<float>(analogRead(34));
    }
#else
    return m_simulated_raw;
#endif
}

SensorMeasurement MoistureSensor::sample(float soil_temp) {
    SensorMeasurement m;
    m.sensor_type = SensorType::SOIL_MOISTURE;
    m.parameter_name = "soil_moisture";
    m.unit = "%";
    m.sensor_id = m_sensor_id;
    m.calibration_version = m_calib.version;
    m.data_source = m_simulation_mode ? DataSource::SYNTHETIC : DataSource::SENSOR_MEASURED;

    float raw = readRawAdc();

    // Noise filtering: Exponential Moving Average (alpha = 0.3)
    if (!m_has_first_sample) {
        m_ema_filtered_raw = raw;
        m_has_first_sample = true;
    } else {
        const float alpha = 0.3f;
        m_ema_filtered_raw = (alpha * raw) + ((1.0f - alpha) * m_ema_filtered_raw);
    }

    m.raw_value = raw;

    // Disconnection & hardware fault detection:
    // Raw count < 100 indicates ground short or disconnected pull-down
    // Raw count > 32500 indicates floating pin or supply short
    if (m_ema_filtered_raw < 100.0f || m_ema_filtered_raw > 32500.0f) {
        m_fault_count++;
        m.calibrated_value = 0.0f;
        m.quality = MeasurementQuality::INVALID;
        m.is_valid = false;
        return m;
    }

    // Apply calibration
    m.calibrated_value = CalibrationMath::rawToSoilMoisture(m_ema_filtered_raw, m_calib);
    m.quality = MeasurementQuality::GOOD;
    m.is_valid = true;
    m_fault_count = 0; // Clear fault on valid acquisition

    return m;
}
