#ifndef AGRISENSE_CALIBRATION_H
#define AGRISENSE_CALIBRATION_H

#include <stdint.h>
#include <string>
#include <algorithm>
#include <cmath>

/**
 * Soil Moisture Calibration Parameters (Capacitive Dielectric)
 */
struct MoistureCalibration {
    float raw_dry = 2850.0f;       // ADC reading in completely dry air
    float raw_wet = 1350.0f;       // ADC reading in water-saturated soil
    std::string version = "1.0.0";
};

/**
 * Soil pH Calibration Parameters (Glass Electrode Nernst Model)
 */
struct PhCalibration {
    float v_ph4 = 2.95f;          // Measured voltage at pH 4.01 buffer
    float v_ph7 = 2.45f;          // Measured voltage at pH 7.00 neutral buffer
    float v_ph10 = 1.95f;         // Measured voltage at pH 10.00 alkaline buffer (optional)
    bool use_three_point = false;
    std::string version = "1.0.0";
};

/**
 * Soil Electrical Conductivity (EC) Calibration Parameters
 */
struct EcCalibration {
    float v_calib_1413 = 1.45f;   // Measured voltage in 1413 uS/cm (1.413 dS/m) KCl solution
    float standard_ec_dsm = 1.413f;
    float temp_coefficient = 0.02f; // Standard 2.0% per °C temperature compensation
    std::string version = "1.0.0";
};

/**
 * Mathematical Transformation Utilities
 */
class CalibrationMath {
public:
    /**
     * Converts raw capacitive ADC reading to Soil Moisture percentage (0.0 to 100.0%)
     */
    static float rawToSoilMoisture(float raw_adc, const MoistureCalibration& cal) {
        if (std::abs(cal.raw_dry - cal.raw_wet) < 1.0f) {
            return 0.0f;
        }
        // In capacitive probes, higher voltage/ADC count = DRY, lower = WET
        float moisture = ((cal.raw_dry - raw_adc) / (cal.raw_dry - cal.raw_wet)) * 100.0f;
        return std::clamp(moisture, 0.0f, 100.0f);
    }

    /**
     * Calculates Soil pH from analog voltage with optional Nernst temperature compensation.
     * Nernst equation: E = E0 - (2.303 * R * T / F) * pH
     * Slope adjusts proportionally to absolute temperature (Kelvin).
     */
    static float voltageToPh(float voltage, const PhCalibration& cal, float soil_temp_c = 25.0f) {
        float kelvin_ref = 298.15f; // 25°C
        float kelvin_actual = 273.15f + std::clamp(soil_temp_c, 0.0f, 60.0f);
        float temp_factor = kelvin_actual / kelvin_ref;

        if (cal.use_three_point) {
            if (voltage >= cal.v_ph7) {
                // Acidic range (pH 4 - 7)
                float base_slope = (7.0f - 4.01f) / (cal.v_ph7 - cal.v_ph4);
                float slope = base_slope * temp_factor;
                float ph = 7.0f + (voltage - cal.v_ph7) * slope;
                return std::clamp(ph, 3.0f, 10.0f);
            } else {
                // Alkaline range (pH 7 - 10)
                float base_slope = (10.0f - 7.0f) / (cal.v_ph10 - cal.v_ph7);
                float slope = base_slope * temp_factor;
                float ph = 7.0f + (voltage - cal.v_ph7) * slope;
                return std::clamp(ph, 3.0f, 10.0f);
            }
        }

        // Standard 2-point linear interpolation
        float base_slope = (7.0f - 4.01f) / (cal.v_ph7 - cal.v_ph4);
        float slope = base_slope * temp_factor;
        float ph = 7.0f + (voltage - cal.v_ph7) * slope;
        return std::clamp(ph, 3.0f, 10.0f);
    }

    /**
     * Calculates Soil EC in dS/m normalized to 25°C reference temperature.
     * EC_25 = EC_T / (1 + alpha * (T - 25))
     */
    static float voltageToEc(float voltage, const EcCalibration& cal, float soil_temp_c = 25.0f) {
        if (cal.v_calib_1413 <= 0.01f) {
            return 0.0f;
        }
        float raw_ec = (voltage / cal.v_calib_1413) * cal.standard_ec_dsm;
        float temp_correction = 1.0f + cal.temp_coefficient * (soil_temp_c - 25.0f);
        if (temp_correction <= 0.1f) {
            temp_correction = 0.1f;
        }
        float ec_25 = raw_ec / temp_correction;
        return std::clamp(ec_25, 0.0f, 20.0f);
    }

    /**
     * Calculates battery voltage and remaining percentage from ADC reading.
     */
    static void computeBattery(float adc_volts, float divider_ratio, float& out_voltage, float& out_pct) {
        out_voltage = adc_volts * divider_ratio;
        // Lithium-ion standard curve (3.2V = 0%, 4.2V = 100%)
        float pct = ((out_voltage - 3.20f) / (4.20f - 3.20f)) * 100.0f;
        out_pct = std::clamp(pct, 0.0f, 100.0f);
    }
};

#endif // AGRISENSE_CALIBRATION_H
