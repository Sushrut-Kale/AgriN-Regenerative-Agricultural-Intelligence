#ifndef AGRISENSE_EC_SENSOR_H
#define AGRISENSE_EC_SENSOR_H

#include "sensor_base.h"
#include "calibration.h"

class EcSensor : public SensorBase {
public:
    EcSensor(const std::string& sensor_id, const EcCalibration& calib, uint8_t adc_channel = 2);

    bool init() override;
    bool isAvailable() const override;
    SensorMeasurement sample(float soil_temp = 25.0f) override;

    void updateCalibration(const EcCalibration& calib);
    void setSimulatedReading(float voltage, bool enable_sim = false);

private:
    EcCalibration m_calib;
    uint8_t m_adc_channel;
    bool m_simulation_mode;
    float m_simulated_voltage;

    float readVoltage();
};

#endif // AGRISENSE_EC_SENSOR_H
