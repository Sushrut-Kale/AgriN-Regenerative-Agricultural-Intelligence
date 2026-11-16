#ifndef AGRISENSE_PINS_H
#define AGRISENSE_PINS_H

/**
 * ============================================================================
 * AgriSense IoT Pin Assignments — ESP32 DevKit V1 (30-pin / 36-pin)
 * ============================================================================
 * 
 * ELECTRICAL WARNING:
 * ESP32 GPIO logic operates strictly at 3.3V. NEVER connect 5V directly!
 * Any analog voltage above 3.3V will permanently destroy the ESP32 silicon.
 * The external ADS1115 ADC must be powered from the 3.3V rail.
 */

// I2C Bus Configuration (Shared between ADS1115 and optional OLED/RTC)
#define PIN_I2C_SDA                 (21)    // Standard ESP32 I2C Data
#define PIN_I2C_SCL                 (22)    // Standard ESP32 I2C Clock
#define ADS1115_I2C_ADDR            (0x48)  // ADDR pin tied to GND

// ADS1115 Analog Input Channel Multiplexing
#define ADS1115_CH_SOIL_MOISTURE    (0)     // A0: Capacitive Soil Moisture Sensor
#define ADS1115_CH_SOIL_PH          (1)     // A1: Analog pH conditioning module
#define ADS1115_CH_SOIL_EC          (2)     // A2: Analog EC conductivity module
#define ADS1115_CH_BATTERY_MONITOR  (3)     // A3: Optional high-res battery monitoring

// 1-Wire Digital Bus (DS18B20 Soil Temperature)
#define PIN_ONEWIRE_TEMP            (4)     // GPIO 4 (Requires 4.7 kΩ pull-up to 3.3V)

// RS-485 / Modbus RTU (NPK Sensor via MAX3485)
// Default hardware UART2 pins on ESP32
#define PIN_RS485_RX                (16)    // UART2 RX (Connected to MAX3485 RO)
#define PIN_RS485_TX                (17)    // UART2 TX (Connected to MAX3485 DI)
#define PIN_RS485_DE_RE             (5)     // Transmit/Receive Direction Control (HIGH = TX, LOW = RX)

// Battery & Power Monitoring (Direct internal ADC channel with 1:2 voltage divider)
#define PIN_BATTERY_ADC             (34)    // GPIO 34 (ADC1_CH6 - Input only)
#define BATTERY_DIVIDER_RATIO       (2.0f)  // R1=100k, R2=100k -> V_in = V_adc * 2.0

// Status Indicator LEDs
#define PIN_LED_STATUS              (2)     // Onboard blue LED on DevKit V1
#define PIN_LED_NETWORK             (15)    // Green external network status LED (Optional)

// Sensor Power Switch / Gate (Low-power high-side P-channel MOSFET switch)
// Keeps sensors powered OFF during deep sleep to conserve battery.
#define PIN_SENSOR_POWER_GATE       (18)    // LOW = Powered, HIGH = Disconnected

#endif // AGRISENSE_PINS_H
