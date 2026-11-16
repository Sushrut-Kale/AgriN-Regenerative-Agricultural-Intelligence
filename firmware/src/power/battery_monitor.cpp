#include "battery_monitor.h"
#include "calibration.h"

#ifdef ARDUINO
#include <Arduino.h>
#endif

BatteryMonitor::BatteryMonitor(uint8_t adc_pin, float divider_ratio)
    : m_adc_pin(adc_pin),
      m_divider_ratio(divider_ratio),
      m_last_voltage(3.85f),
      m_last_percent(80.0f) {}

bool BatteryMonitor::init() {
#ifdef ARDUINO
    pinMode(m_adc_pin, INPUT);
#endif
    return true;
}

void BatteryMonitor::sample(float& out_voltage, float& out_percent) {
#ifdef ARDUINO
    // Read ESP32 12-bit ADC (0 - 4095 over 0 - 3.3V reference)
    int raw = analogRead(m_adc_pin);
    float adc_volts = (raw / 4095.0f) * 3.3f;
    CalibrationMath::computeBattery(adc_volts, m_divider_ratio, out_voltage, out_percent);
#else
    out_voltage = 3.92f;
    out_percent = 84.0f;
#endif
    m_last_voltage = out_voltage;
    m_last_percent = out_percent;
}

bool BatteryMonitor::isLowBattery() const {
    return m_last_voltage < 3.45f;
}
