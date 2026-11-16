#ifndef AGRISENSE_MOISTURE_SENSOR_H
#define AGRISENSE_MOISTURE_SENSOR_H

#include "sensor_base.h"
#include "calibration.h"

class MoistureSensor : public SensorBase {
public:
    MoistureSensor(const std::string& sensor_id, const MoistureCalibration& calib, uint8_t adc_channel = 0);

    bool init() override;
    bool isAvailable() const override;
    SensorMeasurement sample(float soil_temp = 25.0f) override;

    void updateCalibration(const MoistureCalibration& calib);
    void setSimulatedReading(float raw_val, bool enable_sim = false);

private:
    MoistureCalibration m_calib;
    uint8_t m_adc_channel;
    float m_ema_filtered_raw;
    bool m_has_first_sample;
    bool m_simulation_mode;
    float m_simulated_raw;

    float readRawAdc();
};

#endif // AGRISENSE_MOISTURE_SENSOR_H
