#ifndef AGRISENSE_NPK_SENSOR_H
#define AGRISENSE_NPK_SENSOR_H

#include "sensor_base.h"
#include <vector>

struct NpkRegisters {
    uint8_t slave_id = 1;
    uint16_t reg_nitrogen = 0x001E;     // Common industrial 3-in-1 Modbus NPK holding registers
    uint16_t reg_phosphorus = 0x001F;
    uint16_t reg_potassium = 0x0020;
    uint32_t baud_rate = 9600;
};

class NpkSensor {
public:
    NpkSensor(uint8_t rx_pin, uint8_t tx_pin, uint8_t de_re_pin, const NpkRegisters& config);

    bool init();
    bool isAvailable() const;

    // Reads all three nutrients; returns vector of 3 SensorMeasurements (N, P, K)
    std::vector<SensorMeasurement> sampleAll(bool enabled);

    // Static CRC-16 calculation for Modbus RTU
    static uint16_t calculateCrc16(const uint8_t* buffer, size_t length);

private:
    uint8_t m_rx_pin;
    uint8_t m_tx_pin;
    uint8_t m_de_re_pin;
    NpkRegisters m_config;
    bool m_initialized;
    uint32_t m_fault_count;

    bool queryRegister(uint16_t reg_addr, float& out_val);
};

#endif // AGRISENSE_NPK_SENSOR_H
