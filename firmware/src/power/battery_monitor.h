#ifndef AGRISENSE_BATTERY_MONITOR_H
#define AGRISENSE_BATTERY_MONITOR_H

#include <stdint.h>

class BatteryMonitor {
public:
    BatteryMonitor(uint8_t adc_pin, float divider_ratio);

    bool init();
    void sample(float& out_voltage, float& out_percent);
    bool isLowBattery() const;

private:
    uint8_t m_adc_pin;
    float m_divider_ratio;
    float m_last_voltage;
    float m_last_percent;
};

#endif // AGRISENSE_BATTERY_MONITOR_H
