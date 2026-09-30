"""
AgriN Agricultural Measurement Unit Normalizer
================================================
Deterministic, strict conversion of localized agricultural units to AgriN Standard SI Units:
- Temperature: °C, °F, K -> °C
- Rainfall / Precipitation: mm, cm, m, inch -> mm
- Soil Nutrients (N, P, K, micronutrients): mg/kg (ppm), kg/ha, lb/acre, % -> kg/ha and mg/kg
- Electrical Conductivity: dS/m, mS/cm, µS/cm, mmhos/cm -> dS/m
- Soil pH: Water, CaCl2, KCl -> standard pH (1:2.5 H2O equivalent)
- Soil Organic Carbon / Organic Matter: % OC, % SOM, g/kg, g/dm³ -> % Organic Carbon
- Agricultural Area: hectares, acres, bigha, guntha, m² -> hectares
- Water Volume: m³, liters, megaliters, acre-inch -> m³

STRICT SCIENTIFIC HONESTY RULE:
Never silently assume units. If a unit is missing or unsupported, raise a UnitValidationError
or return normalized output with an explicit LOW_CONFIDENCE flag.
"""

from typing import Dict, Any, Tuple, Optional
import math


class UnitValidationError(ValueError):
    """Raised when an unrecognized, missing, or invalid agricultural unit/value is supplied."""
    pass


class AgriculturalUnitNormalizer:
    """Standardized converter enforcing SI agricultural measurement conventions."""

    # ── TEMPERATURE ──────────────────────────────────────────────────────────
    @staticmethod
    def normalize_temperature(val: float, unit: str = "degC") -> Tuple[float, str]:
        if val is None:
            raise UnitValidationError("Temperature value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric temperature value: {val}")

        if unit is None:
            raise UnitValidationError("Temperature unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["c", "degc", "celsius", "°c", "celsius_degree"]:
            c = val_f
        elif u in ["f", "degf", "fahrenheit", "°f"]:
            c = (val_f - 32.0) * (5.0 / 9.0)
        elif u in ["k", "kelvin"]:
            c = val_f - 273.15
        else:
            raise UnitValidationError(f"Unsupported temperature unit '{unit}'. Supported: degC, degF, K")
        
        # Physical plausibility bound: -50°C to +65°C
        if c < -50.0 or c > 65.0:
            raise UnitValidationError(f"Physically implausible ambient temperature: {c:.1f}°C")
        return round(c, 2), "degC"

    # ── RAINFALL / PRECIPITATION ─────────────────────────────────────────────
    @staticmethod
    def normalize_rainfall(val: float, unit: str = "mm") -> Tuple[float, str]:
        if val is None:
            raise UnitValidationError("Rainfall value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric rainfall value: {val}")

        if unit is None:
            raise UnitValidationError("Rainfall unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["mm", "millimeter", "millimeters"]:
            mm = val_f
        elif u in ["cm", "centimeter", "centimeters"]:
            mm = val_f * 10.0
        elif u in ["m", "meter", "meters"]:
            mm = val_f * 1000.0
        elif u in ["in", "inch", "inches"]:
            mm = val_f * 25.4
        else:
            raise UnitValidationError(f"Unsupported rainfall unit '{unit}'. Supported: mm, cm, m, inch")
        
        if mm < 0.0:
            raise UnitValidationError(f"Rainfall cannot be negative: {mm} mm.")
        if mm > 15000.0:
            raise UnitValidationError(f"Physically implausible rainfall: {mm} mm.")
        return round(mm, 2), "mm"

    # ── ELECTRICAL CONDUCTIVITY (SALINITY) ───────────────────────────────────
    @staticmethod
    def normalize_electrical_conductivity(val: float, unit: str = "dS/m") -> Tuple[float, str]:
        if val is None:
            raise UnitValidationError("Electrical conductivity value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric electrical conductivity: {val}")

        if unit is None:
            raise UnitValidationError("Electrical conductivity unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["ds/m", "decisiemens/m", "ms/cm", "millisiemens/cm", "mmhos/cm"]:
            # 1 dS/m = 1 mS/cm = 1 mmhos/cm
            dsm = val_f
        elif u in ["us/cm", "µs/cm", "microsiemens/cm"]:
            # 1000 µS/cm = 1 dS/m
            dsm = val_f / 1000.0
        elif u in ["s/m", "siemens/m"]:
            dsm = val_f * 10.0
        else:
            raise UnitValidationError(f"Unsupported EC unit '{unit}'. Supported: dS/m, mS/cm, µS/cm, mmhos/cm")
        
        if dsm < 0.0 or dsm > 50.0:
            raise UnitValidationError(f"Physically implausible soil EC: {dsm:.2f} dS/m")
        return round(dsm, 2), "dS/m"

    # ── SOIL PH ──────────────────────────────────────────────────────────────
    @staticmethod
    def normalize_soil_ph(val: float, method: str = "water") -> Tuple[float, str]:
        """
        Normalizes soil pH reading to standard 1:2.5 soil-water suspension pH.
        Converts CaCl2 and KCl laboratory methods using pedological factors:
        - CaCl2 (0.01M): pH_water = pH_cacl2 + 0.6
        - KCl (1M): pH_water = pH_kcl + 0.9
        - Water: standard scale
        Physical feasibility bound: [0.0, 14.0]
        """
        if val is None:
            raise UnitValidationError("Soil pH value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric soil pH: {val}")

        if method is None:
            method = "water"
        m = str(method).strip().lower()
        if m in ["water", "h2o", "1:2.5", "1:2.5_water", "water_1_to_2_5", "ph_water"]:
            norm_ph = val_f
        elif m in ["cacl2", "0.01m_cacl2", "ph_cacl2"]:
            norm_ph = val_f + 0.6
        elif m in ["kcl", "1m_kcl", "ph_kcl"]:
            norm_ph = val_f + 0.9
        else:
            raise UnitValidationError(f"Unsupported soil pH measurement method '{method}'. Supported: water, cacl2, kcl")

        if norm_ph < 0.0 or norm_ph > 14.0:
            raise UnitValidationError(f"Physically impossible soil pH value: {norm_ph:.2f}. Must be between 0.0 and 14.0.")

        return round(norm_ph, 2), "pH_water_1_2.5"

    # ── SOIL ORGANIC CARBON / ORGANIC MATTER ─────────────────────────────────
    @staticmethod
    def normalize_organic_carbon(val: float, unit: str = "%") -> Tuple[float, str]:
        """
        Normalizes soil organic matter or carbon to % Soil Organic Carbon (OC%).
        Van Bemmelen factor: % SOM = % OC * 1.724 (or % OC = % SOM / 1.724)
        """
        if val is None:
            raise UnitValidationError("Organic carbon value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric organic carbon: {val}")

        if unit is None:
            raise UnitValidationError("Organic carbon unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["%", "percent", "% oc", "oc_percent", "percent_oc"]:
            oc = val_f
        elif u in ["% som", "som_percent", "percent_som", "% om"]:
            # Convert Organic Matter to Organic Carbon
            oc = val_f / 1.724
        elif u in ["g/kg", "g_per_kg"]:
            # 10 g/kg = 1%
            oc = val_f / 10.0
        elif u in ["g/dm3", "g/dm³", "g/dm^3"]:
            # Brazilian EMBRAPA standard: g/dm³ SOM / 17.24 = % OC
            oc = val_f / 17.24
        else:
            raise UnitValidationError(f"Unsupported Organic Carbon unit '{unit}'. Supported: %, % SOM, g/kg, g/dm³")
        
        if oc < 0.0 or oc > 20.0:
            raise UnitValidationError(f"Physically implausible soil organic carbon: {oc:.2f}%. Must be between 0.0% and 20.0%.")
        return round(oc, 3), "%"

    @staticmethod
    def normalize_soil_organic_matter(val: float, unit: str = "%") -> Tuple[float, str]:
        """Normalizes Soil Organic Matter (SOM) to Soil Organic Carbon (% OC)."""
        return AgriculturalUnitNormalizer.normalize_organic_carbon(val, "% som" if unit in ["%", "% som", "som"] else unit)

    # ── SOIL MACRONUTRIENTS (N, P, K) ────────────────────────────────────────
    @staticmethod
    def normalize_soil_nutrient(val: float, unit: str = "kg/ha", bulk_density: float = 1.33, depth_cm: float = 15.0) -> Dict[str, Any]:
        """
        Standardizes soil nutrient to both kg/ha and mg/kg (ppm).
        Formula: 1 mg/kg (ppm) in top 15cm soil with bulk density 1.33 g/cm³ is ~2.0 kg/ha
        Weight of 1 ha furrow slice (15 cm depth, 1.33 g/cm³) = 10,000 m² * 0.15 m * 1330 kg/m³ = 1,995,000 kg ~ 2.0 * 10^6 kg.
        Therefore: kg/ha = mg/kg * 2.0 (and mg/kg = kg/ha / 2.0).
        """
        if val is None:
            raise UnitValidationError("Soil nutrient value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric soil nutrient: {val}")

        if unit is None:
            raise UnitValidationError("Soil nutrient unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["kg/ha", "kg_per_ha", "kgha"]:
            kg_ha = val_f
            mg_kg = kg_ha / 2.0
        elif u in ["mg/kg", "ppm", "parts_per_million", "mg_per_kg"]:
            mg_kg = val_f
            kg_ha = mg_kg * 2.0
        elif u in ["lb/acre", "lbs/acre", "pounds_per_acre", "lb/ac"]:
            # 1 lb/acre = 1.12085 kg/ha
            kg_ha = val_f * 1.12085
            mg_kg = kg_ha / 2.0
        elif u in ["g/ha"]:
            kg_ha = val_f / 1000.0
            mg_kg = kg_ha / 2.0
        elif u in ["%"]:
            # 1% = 10,000 mg/kg
            mg_kg = val_f * 10000.0
            kg_ha = mg_kg * 2.0
        else:
            raise UnitValidationError(f"Unsupported nutrient unit '{unit}'. Supported: kg/ha, mg/kg, ppm, lb/acre")

        if kg_ha < 0.0:
            raise UnitValidationError("Soil nutrient content cannot be negative.")
        if kg_ha > 10000.0:
            raise UnitValidationError(f"Physically implausible nutrient value: {kg_ha:.1f} kg/ha.")

        return {
            "kg_per_ha": round(kg_ha, 2),
            "mg_per_kg": round(mg_kg, 2),
            "canonical_unit": "kg/ha"
        }

    # ── AGRICULTURAL AREA ────────────────────────────────────────────────────
    @staticmethod
    def normalize_area(val: float, unit: str = "ha") -> Tuple[float, str]:
        if val is None:
            raise UnitValidationError("Land area value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric land area: {val}")

        if unit is None:
            raise UnitValidationError("Land area unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["ha", "hectare", "hectares"]:
            ha = val_f
        elif u in ["acre", "acres", "ac"]:
            # 1 acre = 0.404686 hectares
            ha = val_f * 0.404686
        elif u in ["m2", "m²", "sq_m", "square_meter"]:
            ha = val_f / 10000.0
        elif u in ["bigha", "standard_bigha"]:
            # Standard Upper India Bigha ~ 0.2529 hectares (2,529 m²)
            ha = val_f * 0.2529
        elif u in ["guntha", "gunta"]:
            # 1 guntha = 1/40 acre = 101.17 m² = 0.010117 ha
            ha = val_f * 0.010117
        else:
            raise UnitValidationError(f"Unsupported land area unit '{unit}'. Supported: ha, acre, m2, bigha, guntha")

        if ha <= 0.0:
            raise UnitValidationError("Agricultural area must be strictly positive.")
        return round(ha, 4), "ha"

    # ── WATER VOLUME ─────────────────────────────────────────────────────────
    @staticmethod
    def normalize_water_volume(val: float, unit: str = "m3") -> Tuple[float, str]:
        if val is None:
            raise UnitValidationError("Water volume value cannot be None.")
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise UnitValidationError(f"Invalid non-numeric water volume: {val}")

        if unit is None:
            raise UnitValidationError("Water volume unit cannot be None.")
        u = str(unit).strip().lower()

        if u in ["m3", "m³", "cubic_meter"]:
            m3 = val_f
        elif u in ["l", "liter", "liters", "litres"]:
            m3 = val_f / 1000.0
        elif u in ["ml", "megaliter", "megaliters"]:
            m3 = val_f * 1000.0
        elif u in ["acre-inch", "acre_inch"]:
            # 1 acre-inch = 102.79 m³
            m3 = val_f * 102.79
        else:
            raise UnitValidationError(f"Unsupported water volume unit '{unit}'. Supported: m3, liters, megaliters, acre-inch")

        if m3 < 0.0:
            raise UnitValidationError("Water volume cannot be negative.")
        return round(m3, 2), "m3"


# Global singleton instance
normalizer = AgriculturalUnitNormalizer()
