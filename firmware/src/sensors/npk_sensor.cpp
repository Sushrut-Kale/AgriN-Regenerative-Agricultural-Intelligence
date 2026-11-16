#include "npk_sensor.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <HardwareSerial.h>
static HardwareSerial g_rs485Serial(2); // UART2
#endif

NpkSensor::NpkSensor(uint8_t rx_pin, uint8_t tx_pin, uint8_t de_re_pin, const NpkRegisters& config)
    : m_rx_pin(rx_pin),
      m_tx_pin(tx_pin),
      m_de_re_pin(de_re_pin),
      m_config(config),
      m_initialized(false),
      m_fault_count(0) {}

uint16_t NpkSensor::calculateCrc16(const uint8_t* buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t pos = 0; pos < length; pos++) {
        crc ^= static_cast<uint16_t>(buffer[pos]);
        for (int i = 8; i != 0; i--) {
            if ((crc & 0x0001) != 0) {
                crc >>= 1;
                crc ^= 0xA001; // Modbus standard polynomial
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

bool NpkSensor::init() {
#ifdef ARDUINO
    pinMode(m_de_re_pin, OUTPUT);
    digitalWrite(m_de_re_pin, LOW); // Set MAX3485 to Receive mode by default
    g_rs485Serial.begin(m_config.baud_rate, SERIAL_8N1, m_rx_pin, m_tx_pin);
    m_initialized = true;
#else
    m_initialized = true;
#endif
    return m_initialized;
}

bool NpkSensor::isAvailable() const {
    return m_initialized && (m_fault_count < 5);
}

bool NpkSensor::queryRegister(uint16_t reg_addr, float& out_val) {
#ifdef ARDUINO
    // Construct Modbus RTU Read Holding Registers Frame (Function Code 0x03)
    uint8_t request[8];
    request[0] = m_config.slave_id;
    request[1] = 0x03; // Function Code
    request[2] = (reg_addr >> 8) & 0xFF;
    request[3] = reg_addr & 0xFF;
    request[4] = 0x00; // Number of registers high
    request[5] = 0x01; // Number of registers low (1 register = 2 bytes)
    
    uint16_t crc = calculateCrc16(request, 6);
    request[6] = crc & 0xFF;        // CRC low byte first
    request[7] = (crc >> 8) & 0xFF; // CRC high byte

    // Flush any pending RX bytes
    while (g_rs485Serial.available()) {
        g_rs485Serial.read();
    }

    // Transmit
    digitalWrite(m_de_re_pin, HIGH); // Enable TX
    delayMicroseconds(50);
    g_rs485Serial.write(request, sizeof(request));
    g_rs485Serial.flush();
    delayMicroseconds(50);
    digitalWrite(m_de_re_pin, LOW);  // Back to RX

    // Await 7-byte response: [SlaveID, FuncCode, ByteCount(2), DataHigh, DataLow, CRCLow, CRCHigh]
    uint32_t start_time = millis();
    uint8_t response[7];
    size_t bytes_read = 0;

    while ((millis() - start_time < 500) && (bytes_read < sizeof(response))) {
        if (g_rs485Serial.available()) {
            response[bytes_read++] = g_rs485Serial.read();
        }
    }

    if (bytes_read < 7) {
        m_fault_count++;
        return false;
    }

    // Validate Slave ID and Function
    if (response[0] != m_config.slave_id || response[1] != 0x03 || response[2] != 2) {
        m_fault_count++;
        return false;
    }

    // Validate CRC
    uint16_t resp_crc = (static_cast<uint16_t>(response[6]) << 8) | response[5];
    uint16_t calc_crc = calculateCrc16(response, 5);
    if (resp_crc != calc_crc) {
        m_fault_count++;
        return false;
    }

    uint16_t raw_val = (static_cast<uint16_t>(response[3]) << 8) | response[4];
    out_val = static_cast<float>(raw_val);
    m_fault_count = 0;
    return true;
#else
    (void)reg_addr;
    out_val = 0.0f;
    return false;
#endif
}

std::vector<SensorMeasurement> NpkSensor::sampleAll(bool enabled) {
    std::vector<SensorMeasurement> results;

    const char* names[3] = {"nitrogen", "phosphorus", "potassium"};
    SensorType types[3] = {SensorType::NITROGEN, SensorType::PHOSPHORUS, SensorType::POTASSIUM};
    uint16_t regs[3] = {m_config.reg_nitrogen, m_config.reg_phosphorus, m_config.reg_potassium};

    for (int i = 0; i < 3; i++) {
        SensorMeasurement m;
        m.sensor_type = types[i];
        m.parameter_name = names[i];
        m.unit = "kg/ha";
        m.sensor_id = std::string("npk-") + names[i];
        m.calibration_version = "modbus-linear-v1";

        if (!enabled) {
            // Disabled in hardware profile -> return UNAVAILABLE with zero fabrication
            m.raw_value = 0.0f;
            m.calibrated_value = 0.0f;
            m.quality = MeasurementQuality::MISSING;
            m.data_source = DataSource::UNAVAILABLE;
            m.is_valid = false;
        } else {
            float raw_ppm = 0.0f;
            bool success = queryRegister(regs[i], raw_ppm);

            if (success) {
                m.raw_value = raw_ppm;
                // Conversion factor: mg/kg * 2.70 = kg/ha (ICAR soil depth 20cm, bulk density 1.35)
                m.calibrated_value = raw_ppm * 2.70f;
                m.quality = MeasurementQuality::GOOD;
                m.data_source = DataSource::SENSOR_MEASURED;
                m.is_valid = true;
            } else {
                m.raw_value = 0.0f;
                m.calibrated_value = 0.0f;
                m.quality = MeasurementQuality::INVALID;
                m.data_source = DataSource::UNAVAILABLE;
                m.is_valid = false;
            }
        }
        results.push_back(m);
    }

    return results;
}
