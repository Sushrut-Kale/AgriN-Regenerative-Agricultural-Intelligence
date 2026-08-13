"""
FarmFriend AI — Input Validation Service
==========================================

Validates all farmer-supplied inputs against scientific/realistic ranges.
Shows farmer-friendly error messages — not technical jargon.
"""

from typing import Optional, Dict, List, Tuple

# ── Valid ranges for all inputs ──────────────────────────────────────────────
# Sources: ICAR/TNAU soil testing norms; general agricultural ranges

SOIL_RANGES = {
    # SHC macronutrients (kg/ha)
    "N": {"min": 0, "max": 800, "label": "Nitrogen (N)", "unit": "kg/ha"},
    "P": {"min": 0, "max": 300, "label": "Phosphorus (P)", "unit": "kg/ha"},
    "K": {"min": 0, "max": 1200, "label": "Potassium (K)", "unit": "kg/ha"},
    # SHC secondary nutrient (ppm)
    "S": {"min": 0, "max": 100, "label": "Sulphur (S)", "unit": "ppm"},
    # SHC micronutrients (ppm)
    "Zn": {"min": 0, "max": 20, "label": "Zinc (Zn)", "unit": "ppm"},
    "Fe": {"min": 0, "max": 100, "label": "Iron (Fe)", "unit": "ppm"},
    "Cu": {"min": 0, "max": 20, "label": "Copper (Cu)", "unit": "ppm"},
    "Mn": {"min": 0, "max": 50, "label": "Manganese (Mn)", "unit": "ppm"},
    "B":  {"min": 0, "max": 10, "label": "Boron (B)", "unit": "ppm"},
    # SHC chemical properties
    "ph": {"min": 3.0, "max": 11.0, "label": "Soil pH", "unit": ""},
    "EC": {"min": 0, "max": 20, "label": "Electrical Conductivity (EC)", "unit": "dS/m"},
    "OC": {"min": 0, "max": 5, "label": "Organic Carbon (OC)", "unit": "%"},
}

ENV_RANGES = {
    "temperature": {"min": -5, "max": 50, "label": "Temperature", "unit": "°C"},
    "humidity": {"min": 0, "max": 100, "label": "Humidity", "unit": "%"},
    "rainfall": {"min": 0, "max": 5000, "label": "Annual Rainfall", "unit": "mm"},
}

FARM_REQUIRED = ["state", "district", "season", "soil_type", "irrigation_available"]

VALID_SEASONS = ["kharif", "rabi", "summer", "perennial"]
VALID_IRRIGATION = ["yes", "no"]
VALID_DRAINAGE = ["good", "moderate", "poor", "unknown"]
VALID_SOIL_TYPES = ["black", "red", "alluvial", "sandy_loam", "loam", "clay_loam", "sandy", "laterite", "unknown"]


class ValidationError:
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" | "warning"

    def to_dict(self):
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class ValidationResult:
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str):
        self.errors.append(ValidationError(field, message, "error"))

    def add_warning(self, field: str, message: str):
        self.warnings.append(ValidationError(field, message, "warning"))

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


def validate_numeric_range(
    value, field: str, meta: dict, result: ValidationResult, required: bool = False
):
    """Validate a single numeric field against its allowed range."""
    label = meta["label"]
    unit = meta.get("unit", "")
    unit_str = f" {unit}" if unit else ""

    if value is None or value == "":
        if required:
            result.add_error(field, f"{label} is required. Please enter a value.")
        return  # Optional field — skip

    try:
        val = float(value)
    except (TypeError, ValueError):
        result.add_error(field, f"{label} must be a number.")
        return

    if val < meta["min"] or val > meta["max"]:
        result.add_error(
            field,
            f"{label} value {val}{unit_str} is outside the expected range "
            f"({meta['min']}–{meta['max']}{unit_str}). "
            "Please check your soil test report and re-enter."
        )
        return

    # Warn about suspiciously zero values (possible missing data)
    if val == 0 and field in ("N", "P", "K", "OC"):
        result.add_warning(
            field,
            f"{label} is entered as 0. If this is a missing value rather than a "
            "real measurement, please leave the field blank for more accurate analysis."
        )


def validate_soil_inputs(soil_data: dict) -> ValidationResult:
    """Validate all 12 SHC soil parameters."""
    result = ValidationResult()

    # pH is critical — warn if not provided
    if soil_data.get("ph") is None:
        result.add_warning("ph", "Soil pH was not entered. pH is important for crop suitability analysis. "
                           "Please enter it from your soil test report if available.")

    for field, meta in SOIL_RANGES.items():
        value = soil_data.get(field)
        validate_numeric_range(value, field, meta, result)

    return result


def validate_env_inputs(env_data: dict) -> ValidationResult:
    """Validate environmental inputs."""
    result = ValidationResult()

    for field, meta in ENV_RANGES.items():
        value = env_data.get(field)
        validate_numeric_range(value, field, meta, result)

    return result


def validate_farm_inputs(farm_data: dict) -> ValidationResult:
    """Validate farm information fields."""
    result = ValidationResult()

    if not farm_data.get("state"):
        result.add_error("state", "Please select your state.")

    if not farm_data.get("district"):
        result.add_error("district", "Please select your district.")

    if not farm_data.get("season"):
        result.add_error("season", "Please select the current farming season.")
    elif farm_data.get("season") not in VALID_SEASONS:
        result.add_error("season", f"Invalid season selected.")

    if farm_data.get("irrigation_available") is not None:
        irr = str(farm_data["irrigation_available"]).lower()
        if irr not in VALID_IRRIGATION:
            result.add_error("irrigation_available", "Irrigation availability must be Yes or No.")

    if farm_data.get("drainage"):
        if farm_data["drainage"] not in VALID_DRAINAGE:
            result.add_error("drainage", "Invalid drainage selection.")

    if farm_data.get("soil_type"):
        if farm_data["soil_type"] not in VALID_SOIL_TYPES:
            result.add_warning("soil_type", "Soil type selection not recognized. Using general analysis.")

    farm_area = farm_data.get("farm_area")
    if farm_area is not None:
        try:
            area = float(farm_area)
            if area <= 0:
                result.add_error("farm_area", "Farm area must be a positive number.")
            elif area > 10000:
                result.add_warning("farm_area", f"Farm area {area} acres seems very large. Please verify.")
        except (TypeError, ValueError):
            result.add_error("farm_area", "Farm area must be a number.")

    return result


def validate_whatif_inputs(whatif_data: dict) -> ValidationResult:
    """Validate what-if simulation inputs."""
    result = ValidationResult()

    for field, value in whatif_data.items():
        if field in SOIL_RANGES:
            validate_numeric_range(value, field, SOIL_RANGES[field], result)
        elif field in ENV_RANGES:
            validate_numeric_range(value, field, ENV_RANGES[field], result)

    return result


def count_missing_soil_fields(soil_data: dict) -> Tuple[int, List[str]]:
    """Count how many SHC parameters are missing."""
    all_fields = list(SOIL_RANGES.keys())
    missing = [f for f in all_fields if soil_data.get(f) is None]
    return len(missing), missing


def compute_data_confidence(soil_data: dict, env_data: dict) -> str:
    """
    Compute overall data confidence based on completeness.
    Returns: "high" | "medium" | "low"
    """
    n_missing_soil, _ = count_missing_soil_fields(soil_data)
    core_env_missing = sum(1 for f in ["temperature", "humidity", "rainfall"]
                           if env_data.get(f) is None)

    # Core ML features: N, P, K, ph, temperature, humidity, rainfall
    core_ml_missing = sum(1 for f in ["N", "P", "K", "ph"]
                          if soil_data.get(f) is None)
    core_ml_missing += core_env_missing

    if core_ml_missing == 0 and n_missing_soil <= 4:
        return "high"
    elif core_ml_missing <= 2 and n_missing_soil <= 8:
        return "medium"
    else:
        return "low"
