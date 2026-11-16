# 🔌 AgriN Hardware Integration Specification
**System:** AgriSense IoT Edge Device  
**Target Platform:** ESP32 DevKit V1 (ESP32-WROOM-32)  
**Document Code:** AGRIN-HW-SPEC-001  
**Intended Audience:** Embedded Systems Engineers, PCB Hardware Designers, Field Deployers  

---

## 1. Overview & Safety Directives

The AgriSense IoT node collects continuous agricultural biophysical telemetry from agricultural plots and transmits it over Wi-Fi / Cellular to the AgriN platform.

> [!CAUTION]
> **CRITICAL ELECTRICAL SAFETY RULE — 3.3V GPIO LOGIC**:  
> The ESP32 MCU logic operates strictly at **3.3V**. Connecting any 5V sensor output directly to an ESP32 GPIO pin will cause permanent dielectric breakdown and hardware destruction. All analog probes must interface through the **ADS1115 ADC** (powered at 3.3V) or utilize bidirectional logic level shifters (e.g., BSS138 / TXS0108E).

---

## 2. Sensor Bill of Materials (BOM) & Pin Allocations

| Component | Function | Interface | Voltage Rail | Hardware Pin (Default Reference) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ESP32 DevKit V1** | Central Microcontroller | - | 3.3V Regulated | - | 240 MHz dual-core, 520 KB SRAM |
| **ADS1115 16-bit ADC** | High-precision Analog-to-Digital | I²C Bus | 3.3V | SDA: `GPIO 21`, SCL: `GPIO 22` | Address `0x48` (ADDR pin to GND) |
| **Capacitive Moisture** | Soil Volumetric Water Content | Analog | 3.3V | ADS1115 `Channel A0` | Corrosion-resistant probe |
| **DS18B20 Temp Probe** | Soil Rootzone Temperature | 1-Wire | 3.3V | `GPIO 4` | Requires 4.7 kΩ pull-up resistor to 3.3V |
| **Soil pH Probe** | Soil Acidity / Alkalinity | Analog | 3.3V / 5V | ADS1115 `Channel A1` | Conditioned via BNC interface board |
| **Soil EC Probe** | Electrical Conductivity (Salinity) | Analog | 3.3V / 5V | ADS1115 `Channel A2` | Temperature compensated |
| **MAX3485 Module** | RS-485 / Modbus RTU (NPK) | Hardware UART | 3.3V | RX: `GPIO 16`, TX: `GPIO 17`, DE/RE: `GPIO 5` | 9600 baud, 8-N-1 (Optional) |
| **CN3065 Solar Charger** | Solar MPPT Lithium Charger | - | 5V Solar | Connect to 3.7V 18650 Li-ion | Red/Green charge status LEDs |
| **5V Boost Converter** | Rail Stabilization | - | 3.7V in / 5V out | Connects battery to ESP32 Vin | High-efficiency synchronous boost |

---

## 3. Sensor Calibration Guide

### A. Capacitive Soil Moisture Sensor (Analog ADS1115 A0)
1. **Dry Air Calibration**: Hold the probe suspended in dry ambient air. Record raw ADC value ($ADC_{dry} \approx 2800$).
2. **Pure Water Calibration**: Submerge probe up to the stop line in tap water. Record raw ADC value ($ADC_{wet} \approx 1350$).
3. **Firmware Formula**:
   $$\text{Moisture (\%)} = \text{clamp}\left(\frac{ADC_{dry} - ADC_{measured}}{ADC_{dry} - ADC_{wet}} \times 100.0, 0.0, 100.0\right)$$

### B. Soil pH Sensor (Analog ADS1115 A1)
1. **pH 7.0 Neutral Calibration**: Dip probe in standard pH 7.0 buffer. Read voltage $V_7$.
2. **pH 4.0 Acidic Calibration**: Rinse in distilled water, dip in pH 4.0 buffer. Read voltage $V_4$.
3. **Slope Calculation**:
   $$\text{Slope} = \frac{7.0 - 4.0}{V_7 - V_4}, \quad \text{pH} = 7.0 + (V_{measured} - V_7) \times \text{Slope}$$

### C. Soil EC Sensor (Analog ADS1115 A2)
1. Submerge in standard $1413\ \mu\text{S/cm}$ ($1.413\ \text{dS/m}$) calibration standard at 25°C.
2. Store linear conversion coefficient in `hardware_profile.json`.

---

## 4. Hardware Team Checklist: Action Items to Supply

Before physical deployment, the hardware engineering team must provide:

- [ ] Exact final PCB schematic routing showing GPIO assignments for I2C, OneWire, and UART.
- [ ] Confirmed ADS1115 channel mappings (A0, A1, A2, A3).
- [ ] Measured dry/wet calibration ADC integer counts for the chosen capacitive probe model.
- [ ] Measured buffer voltages ($V_4, V_7$) for the soil pH signal conditioning module.
- [ ] Modbus register map datasheet for the RS485 NPK probe (holding register addresses for N, P, K).
- [ ] Solar panel wattage ($5\text{W}$ or $10\text{W}$) and battery nominal capacity ($2600\text{ mAh}$ / $5200\text{ mAh}$).
