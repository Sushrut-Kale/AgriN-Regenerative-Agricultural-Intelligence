#ifndef AGRISENSE_TEMPERATURE_SENSOR_H
#define AGRISENSE_TEMPERATURE_SENSOR_H

#include "sensor_base.h"

class TemperatureSensor : public SensorBase {
public:
    TemperatureSensor(const std::string& sensor_id, uint8_t gpio_pin);

    bool init() override;
    bool isAvailable() const override;
    SensorMeasurement sample(float soil_temp = 25.0f) override;

    void setSimulatedReading(float temp_c, bool enable_sim = false);

private:
    uint8_t m_gpio_pin;
    bool m_simulation_mode;
    float m_simulated_temp;
    float m_last_valid_temp;

    float readPhysicalTemp();
};

#endif // AGRISENSE_TEMPERATURE_SENSOR_H
