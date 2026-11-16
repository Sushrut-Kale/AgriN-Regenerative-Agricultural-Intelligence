#ifndef AGRISENSE_PH_SENSOR_H
#define AGRISENSE_PH_SENSOR_H

#include "sensor_base.h"
#include "calibration.h"

class PhSensor : public SensorBase {
public:
    PhSensor(const std::string& sensor_id, const PhCalibration& calib, uint8_t adc_channel = 1);

    bool init() override;
    bool isAvailable() const override;
    SensorMeasurement sample(float soil_temp = 25.0f) override;

    void updateCalibration(const PhCalibration& calib);
    void setSimulatedReading(float voltage, bool enable_sim = false);

private:
    PhCalibration m_calib;
    uint8_t m_adc_channel;
    bool m_simulation_mode;
    float m_simulated_voltage;

    float readVoltage();
};

#endif // AGRISENSE_PH_SENSOR_H
