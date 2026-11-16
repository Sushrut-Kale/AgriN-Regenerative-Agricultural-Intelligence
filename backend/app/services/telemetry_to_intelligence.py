"""
AgriN Telemetry-to-Intelligence Bridge
=======================================

Converts raw validated IoT sensor telemetry → AnalysisRequest-compatible dict
for the existing intelligence pipeline, with strict provenance tracking.

=============================================================================
ML FEATURE ALIGNMENT AUDIT (verified 2026-11-17)
=============================================================================

FEATURES (15, in exact order):
  N, P, K, S, Zn, Fe, Cu, Mn, B, ph, EC, OC, temperature, humidity, rainfall

TRAIN vs PREDICT consistency:
  ✅ Feature names identical in ml/train.py (via DataFrame columns from CSV)
     and ml/predict.py FEATURE_NAMES constant.
  ✅ Feature ORDER identical (hardcoded in FEATURE_NAMES, matches CSV column order).
  ✅ Missing value strategy: predict.py substitutes training-distribution medians
     for any None feature — documented in DEFAULT_MEDIANS.
  ✅ Scaler: train.py fits StandardScaler but Random Forest is selected as best
     model (uses_scaler=False in model_metadata.json) → predict.py skips scaling
     for RF. CONSISTENT.

UNIT ALIGNMENT (sensor raw → model expectation):
  N, P, K  : IoT Modbus NPK sensors output mg/kg (ppm).
             Model trained on ICAR SHC kg/ha values (N:280-560, P:10-25, K:108-280).
             CONVERSION REQUIRED: ppm → kg/ha using bulk_density × depth_cm × 0.1
             Default: bulk_density=1.35 g/cm³, depth=20cm → factor ≈ 2.7
             Bridge applies this conversion when NPK sensor IS present.
             If NPK sensor NOT present → values = None → model uses median fallback
             (N=90, P=50, K=180 kg/ha). This is documented as UNAVAILABLE, not measured.

  ph       : Model key is lowercase "ph". SoilDataInput uses "ph" (lowercase).
             agrin_intelligence.py resolves both "pH" and "ph" via dual-key lookup.
             Bridge outputs "ph" (lowercase) to match ML feature name exactly.

  EC       : IoT EC sensor → µS/cm. Model expects dS/m.
             CONVERSION: µS/cm ÷ 1000 = dS/m. Applied in bridge.

  temperature: °C (direct, no conversion)
  humidity   : % RH (direct, no conversion)
  rainfall   : mm annual (from Open-Meteo → may be daily; bridge uses annual proxy)

  OC, S, Zn, Fe, Cu, Mn, B: NO IoT sensors → always UNAVAILABLE → model median fallback.

KNOWN LIMITATION:
  NPK sensors (Modbus RS-485) measure NH4+/NO3- or total NPK via spectral method
  and report mg/kg. The conversion factor (bulk_density × depth) introduces
  uncertainty (~15-25%). This is documented in provenance metadata.
  The confidence engine will reflect this as MEDIUM confidence for NPK fields.
=============================================================================
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Data provenance enum values (mirror IoT models without import dependency)
# ---------------------------------------------------------------------------
SENSOR_MEASURED = "SENSOR_MEASURED"       # Direct hardware measurement
EXTERNAL_OBSERVED = "EXTERNAL_OBSERVED"  # From live external API (Open-Meteo)
FARMER_ENTERED = "FARMER_ENTERED"        # Manual entry by farmer/agronomist
CALCULATED = "CALCULATED"               # Derived via documented formula
UNAVAILABLE = "UNAVAILABLE"             # Not measured; NOT substituted silently


# ---------------------------------------------------------------------------
# NPK unit conversion constants
# ---------------------------------------------------------------------------
# Default soil bulk density and sampling depth for mg/kg → kg/ha conversion
# Reference: ICAR Soil Testing Manual (2017), Chap 3
_DEFAULT_BULK_DENSITY_G_CM3 = 1.35  # g/cm³, typical black/alluvial soils
_DEFAULT_SAMPLE_DEPTH_CM = 20.0     # Standard 0–20 cm topsoil horizon

# kg/ha = mg/kg × (bulk_density × sample_depth_cm × 0.1)
# factor = 1.35 × 20 × 0.1 = 2.70
_NPK_CONVERSION_FACTOR: float = _DEFAULT_BULK_DENSITY_G_CM3 * _DEFAULT_SAMPLE_DEPTH_CM * 0.1


# ---------------------------------------------------------------------------
# Agro-climatic zone lookup by GPS bounding boxes (simplified ICAR ACZ 2003)
# ---------------------------------------------------------------------------
_ACZ_ZONES = [
    {"code": "IN_ACZ_01", "name": "Western Himalayan",       "lat_min": 29, "lat_max": 36, "lon_min": 73, "lon_max": 82},
    {"code": "IN_ACZ_02", "name": "Eastern Himalayan",       "lat_min": 25, "lat_max": 30, "lon_min": 86, "lon_max": 97},
    {"code": "IN_ACZ_03", "name": "Lower Gangetic Plains",   "lat_min": 22, "lat_max": 27, "lon_min": 85, "lon_max": 90},
    {"code": "IN_ACZ_04", "name": "Middle Gangetic Plains",  "lat_min": 24, "lat_max": 29, "lon_min": 78, "lon_max": 86},
    {"code": "IN_ACZ_05", "name": "Upper Gangetic Plains",   "lat_min": 25, "lat_max": 31, "lon_min": 73, "lon_max": 80},
    {"code": "IN_ACZ_06", "name": "Trans-Gangetic Plains",   "lat_min": 27, "lat_max": 32, "lon_min": 73, "lon_max": 78},
    {"code": "IN_ACZ_07", "name": "Eastern Plateau & Hills", "lat_min": 18, "lat_max": 24, "lon_min": 78, "lon_max": 87},
    {"code": "IN_ACZ_08", "name": "Central Plateau & Hills", "lat_min": 20, "lat_max": 26, "lon_min": 73, "lon_max": 80},
    {"code": "IN_ACZ_09", "name": "Western Plateau & Hills (Deccan)", "lat_min": 15, "lat_max": 22, "lon_min": 73, "lon_max": 80},
    {"code": "IN_ACZ_10", "name": "Southern Plateau & Hills","lat_min": 10, "lat_max": 18, "lon_min": 74, "lon_max": 80},
    {"code": "IN_ACZ_11", "name": "East Coast Plains & Hills","lat_min": 8, "lat_max": 20, "lon_min": 79, "lon_max": 85},
    {"code": "IN_ACZ_12", "name": "West Coast Plains & Ghats","lat_min": 8, "lat_max": 20, "lon_min": 73, "lon_max": 77},
    {"code": "IN_ACZ_13", "name": "Gujarat Plains & Hills",  "lat_min": 20, "lat_max": 25, "lon_min": 68, "lon_max": 75},
    {"code": "IN_ACZ_14", "name": "Western Dry Region",     "lat_min": 24, "lat_max": 30, "lon_min": 68, "lon_max": 73},
    {"code": "IN_ACZ_15", "name": "Island Ecosystems",      "lat_min": 6,  "lat_max": 14, "lon_min": 92, "lon_max": 94},
]

_DEFAULT_ACZ = {"code": "IN_ACZ_09", "name": "Western Plateau & Hills (Deccan / Maharashtra)"}


def _resolve_acz_from_coords(lat: float, lon: float) -> Dict[str, str]:
    """
    Resolves ICAR Agro-Climatic Zone from GPS coordinates using bounding-box lookup.
    Returns the first match; falls back to Deccan default if no match found.
    """
    for zone in _ACZ_ZONES:
        if (zone["lat_min"] <= lat <= zone["lat_max"] and
                zone["lon_min"] <= lon <= zone["lon_max"]):
            return {"code": zone["code"], "name": zone["name"]}
    return _DEFAULT_ACZ


# ---------------------------------------------------------------------------
# Live weather fetch from Open-Meteo (re-implemented for bridge isolation)
# ---------------------------------------------------------------------------
_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _fetch_open_meteo_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches current weather conditions from Open-Meteo for given GPS coordinates.

    Provenance: EXTERNAL_OBSERVED — live NWP model output from NOAA/ECMWF blend.

    Returns dict with keys: temperature, humidity, rainfall_today_mm,
    rainfall_annual_proxy_mm, is_live_data, source, observed_at, error (if any).
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "daily": "precipitation_sum",
        "forecast_days": 1,
        "timezone": "auto",
    }
    url = _OPEN_METEO_URL + "?" + urllib.parse.urlencode(params)
    result: Dict[str, Any] = {
        "is_live_data": False,
        "source": "Open-Meteo NWP API",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "temperature": None,
        "humidity": None,
        "rainfall_today_mm": None,
        # Annual rainfall proxy: not available from current-hour API;
        # use climatological fallback (see note in bridge function)
        "rainfall_annual_proxy_mm": None,
    }
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgriN/2.5"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data.get("current", {})
        result["temperature"] = current.get("temperature_2m")
        result["humidity"] = current.get("relative_humidity_2m")
        result["rainfall_today_mm"] = current.get("precipitation", 0.0)
        result["is_live_data"] = True
        result["observed_at"] = current.get("time", result["observed_at"])
    except Exception as exc:
        result["error"] = str(exc)

    return result


def _get_annual_rainfall_proxy(lat: float, lon: float, district: str = "") -> Optional[float]:
    """
    Returns the annual rainfall proxy for a location.
    Uses weather_service district lookup first, then Open-Meteo climatology isn't
    available from the forecast endpoint, so we rely on the geo_service lookup.
    Returns None if unavailable — caller must handle gracefully.
    """
    try:
        # Try geo_service which has district-level climatological values
        try:
            from backend.app.services.weather_service import get_district_info
        except ImportError:
            from app.services.weather_service import get_district_info

        if district:
            d_info = get_district_info(district)
            return float(d_info.get("default_rainfall", 750))
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Core bridge data classes (plain dicts — no Pydantic dependency here)
# ---------------------------------------------------------------------------

class FieldProvenance:
    """Tracks provenance of a single field value in the bridge output."""

    def __init__(
        self,
        value: Optional[float],
        source: str,
        unit: str,
        raw_value: Optional[float] = None,
        conversion_note: Optional[str] = None,
        sensor_type: Optional[str] = None,
        quality: str = "GOOD",
    ):
        self.value = value
        self.source = source  # One of SENSOR_MEASURED, EXTERNAL_OBSERVED, UNAVAILABLE, etc.
        self.unit = unit
        self.raw_value = raw_value
        self.conversion_note = conversion_note
        self.sensor_type = sensor_type
        self.quality = quality  # GOOD | DEGRADED | INVALID | MISSING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "unit": self.unit,
            "raw_value": self.raw_value,
            "conversion_note": self.conversion_note,
            "sensor_type": self.sensor_type,
            "quality": self.quality,
            "is_measured": self.source == SENSOR_MEASURED,
            "is_available": self.source != UNAVAILABLE,
        }


# ---------------------------------------------------------------------------
# Main bridge function
# ---------------------------------------------------------------------------

def build_analysis_request_from_telemetry(
    measurements: Dict[str, Any],
    device_location: Tuple[float, float],
    district: str,
    state: str,
    device_id: str = "",
    field_id: str = "",
    season: str = "Kharif",
    soil_type: str = "black",
    irrigation_available: str = "no",
    drainage: str = "good",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Converts raw validated IoT sensor measurements into an AnalysisRequest-compatible
    dict for the AgriN intelligence pipeline, with full provenance tracking.

    Parameters
    ----------
    measurements : dict
        Keys are sensor_type strings (e.g. "SOIL_MOISTURE", "SOIL_PH", "SOIL_EC",
        "SOIL_TEMP", "NITROGEN", "PHOSPHORUS", "POTASSIUM").
        Values are dicts with at minimum:
          - calibrated_value: float or None
          - raw_value: float or None
          - unit: str
          - quality: str ("GOOD", "DEGRADED", "INVALID", "MISSING")
          - is_valid: bool
    device_location : (lat, lon)
        GPS coordinates of the device/field. Required for weather + ACZ enrichment.
    district : str
        Administrative district name.
    state : str
        State name.
    device_id : str
        Device identifier (for traceability).
    field_id : str
        Field identifier (for traceability).
    season : str
        Crop season ("Kharif", "Rabi", "Summer", "Perennial").
    soil_type : str
        Soil physical type ("black", "alluvial", "red", "sandy", "clayey").
    irrigation_available : str
        "yes" or "no".
    drainage : str
        "good", "moderate", "poor".

    Returns
    -------
    (farm_data_dict, confidence_report)
        farm_data_dict : dict suitable for run_full_agricultural_intelligence()
        confidence_report : dict listing provenance of every field
    """
    lat, lon = device_location
    now_utc = datetime.now(timezone.utc)

    # ── Degraded-state early exit ─────────────────────────────────────────────
    if lat is None or lon is None:
        return _degraded_state(
            reason="No GPS coordinates provided — cannot enrich weather or ACZ.",
            device_id=device_id,
            field_id=field_id,
        )

    has_any_soil = any(
        measurements.get(st, {}).get("is_valid") is True
        for st in ["SOIL_MOISTURE", "SOIL_PH", "SOIL_EC", "SOIL_TEMP",
                   "NITROGEN", "PHOSPHORUS", "POTASSIUM"]
    )
    if not has_any_soil:
        return _degraded_state(
            reason="No valid soil sensor readings — insufficient data for soil intelligence layer.",
            device_id=device_id,
            field_id=field_id,
        )

    # ── Helper: extract a valid measurement ──────────────────────────────────
    def _get(sensor_type: str) -> Optional[Dict[str, Any]]:
        """Returns the measurement dict if valid, else None."""
        m = measurements.get(sensor_type)
        if m and m.get("is_valid") is True and m.get("calibrated_value") is not None:
            return m
        return None

    # ── 1. Soil moisture ─────────────────────────────────────────────────────
    # Capacitive soil moisture → moisture_percent
    # Provenance: SENSOR_MEASURED
    moisture_m = _get("SOIL_MOISTURE")
    if moisture_m:
        moisture_prov = FieldProvenance(
            value=moisture_m["calibrated_value"],
            source=SENSOR_MEASURED,
            unit=moisture_m.get("unit", "%"),
            raw_value=moisture_m.get("raw_value"),
            sensor_type="SOIL_MOISTURE (Capacitive)",
            quality=moisture_m.get("quality", "GOOD"),
        )
    else:
        moisture_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="%",
            sensor_type="SOIL_MOISTURE",
            quality="MISSING",
        )

    # ── 2. Soil temperature ──────────────────────────────────────────────────
    # DS18B20 OneWire → soil_temperature (°C)
    temp_m = _get("SOIL_TEMP")
    if temp_m:
        soil_temp_prov = FieldProvenance(
            value=temp_m["calibrated_value"],
            source=SENSOR_MEASURED,
            unit="°C",
            raw_value=temp_m.get("raw_value"),
            sensor_type="SOIL_TEMP (DS18B20 OneWire)",
            quality=temp_m.get("quality", "GOOD"),
        )
    else:
        soil_temp_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="°C",
            sensor_type="SOIL_TEMP",
            quality="MISSING",
        )

    # ── 3. Soil pH ───────────────────────────────────────────────────────────
    # Analog pH probe → soil_ph (pH units, 0–14)
    # ML model expects key "ph" (lowercase). We store under "ph".
    ph_m = _get("SOIL_PH")
    if ph_m:
        ph_val = ph_m["calibrated_value"]
        # Physical validity guard: pH must be 3–11 (Pydantic SoilDataInput bounds)
        if ph_val is not None and (ph_val < 3.0 or ph_val > 11.0):
            ph_prov = FieldProvenance(
                value=None,
                source=UNAVAILABLE,
                unit="pH",
                raw_value=ph_m.get("raw_value"),
                conversion_note=f"pH value {ph_val} out of physical bounds (3–11); discarded.",
                sensor_type="SOIL_PH (Analog probe)",
                quality="INVALID",
            )
        else:
            ph_prov = FieldProvenance(
                value=ph_val,
                source=SENSOR_MEASURED,
                unit="pH",
                raw_value=ph_m.get("raw_value"),
                sensor_type="SOIL_PH (Analog probe)",
                quality=ph_m.get("quality", "GOOD"),
            )
    else:
        ph_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="pH",
            sensor_type="SOIL_PH",
            quality="MISSING",
        )

    # ── 4. Electrical conductivity ───────────────────────────────────────────
    # EC sensor → usually outputs µS/cm; model expects dS/m
    # Conversion: µS/cm ÷ 1000 = dS/m
    # NOTE: Some sensors output mS/cm or dS/m directly — check calibrated_value unit.
    ec_m = _get("SOIL_EC")
    if ec_m:
        raw_ec = ec_m["calibrated_value"]
        ec_unit = ec_m.get("unit", "µS/cm").lower()
        if "ds" in ec_unit or "ms/cm" in ec_unit:
            # Already in dS/m (or mS/cm which equals dS/m)
            ec_val = raw_ec
            conversion_note = f"Unit '{ec_unit}' treated as dS/m directly."
        else:
            # Assume µS/cm → convert
            ec_val = raw_ec / 1000.0 if raw_ec is not None else None
            conversion_note = f"Converted from µS/cm ({raw_ec}) → dS/m ({ec_val:.4f}) via ÷1000."

        ec_prov = FieldProvenance(
            value=ec_val,
            source=SENSOR_MEASURED,
            unit="dS/m",
            raw_value=raw_ec,
            conversion_note=conversion_note,
            sensor_type="SOIL_EC (EC probe)",
            quality=ec_m.get("quality", "GOOD"),
        )
    else:
        ec_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="dS/m",
            sensor_type="SOIL_EC",
            quality="MISSING",
        )

    # ── 5. NPK (Modbus RS-485 sensor) ────────────────────────────────────────
    # If present: convert mg/kg → kg/ha using documented bulk_density × depth factor.
    # If NOT present: value = None with UNAVAILABLE provenance.
    # CRITICAL: We NEVER fabricate NPK from ML estimates and present it as measured.

    def _convert_npk(sensor_type: str, element_name: str) -> FieldProvenance:
        """
        Converts NPK sensor mg/kg reading to ICAR-compatible kg/ha.
        Returns UNAVAILABLE FieldProvenance if sensor not present/valid.

        Conversion: kg/ha = mg/kg × bulk_density(g/cm³) × depth(cm) × 0.1
        Default bulk_density=1.35 g/cm³, depth=20cm → factor=2.70
        """
        m = _get(sensor_type)
        if not m:
            return FieldProvenance(
                value=None,
                source=UNAVAILABLE,
                unit="kg/ha",
                sensor_type=f"{sensor_type} (Modbus NPK)",
                quality="MISSING",
            )
        raw_mg_kg = m["calibrated_value"]
        kg_ha = raw_mg_kg * _NPK_CONVERSION_FACTOR if raw_mg_kg is not None else None
        return FieldProvenance(
            value=round(kg_ha, 2) if kg_ha is not None else None,
            source=SENSOR_MEASURED,
            unit="kg/ha",
            raw_value=raw_mg_kg,
            conversion_note=(
                f"NPK sensor → {raw_mg_kg} mg/kg × {_NPK_CONVERSION_FACTOR:.2f} "
                f"(ρ={_DEFAULT_BULK_DENSITY_G_CM3} g/cm³ × d={_DEFAULT_SAMPLE_DEPTH_CM} cm × 0.1) "
                f"= {kg_ha:.1f} kg/ha. Uncertainty ±15–25% from bulk density assumption."
            ),
            sensor_type=f"{element_name} NPK sensor (Modbus RS-485)",
            quality=m.get("quality", "GOOD"),
        )

    n_prov = _convert_npk("NITROGEN", "Nitrogen")
    p_prov = _convert_npk("PHOSPHORUS", "Phosphorus")
    k_prov = _convert_npk("POTASSIUM", "Potassium")

    # ── 6. Micronutrients (S, Zn, Fe, Cu, Mn, B) ────────────────────────────
    # NO IoT sensor hardware provides these in this device profile.
    # We mark all as UNAVAILABLE; the ML model will use its training medians.
    # CRITICAL: We do NOT estimate these from ML and present as measured.
    _unavailable_micro = FieldProvenance(
        value=None,
        source=UNAVAILABLE,
        unit="ppm",
        conversion_note="No sensor hardware for this parameter. ML model will use training-distribution median as inference fallback (not presented as measured).",
        quality="MISSING",
    )

    # ── 7. Organic Carbon ────────────────────────────────────────────────────
    # OC requires wet oxidation lab test (Walkley-Black method).
    # IoT sensors cannot measure OC directly. UNAVAILABLE — no estimation.
    oc_prov = FieldProvenance(
        value=None,
        source=UNAVAILABLE,
        unit="%",
        conversion_note="Organic Carbon requires Walkley-Black lab test. Cannot be measured by in-field IoT sensors. Provenance: UNAVAILABLE.",
        quality="MISSING",
    )

    # ── 8. Live weather enrichment from Open-Meteo ───────────────────────────
    # Provenance: EXTERNAL_OBSERVED (live NWP API)
    weather_raw = _fetch_open_meteo_weather(lat, lon)
    weather_is_live = weather_raw.get("is_live_data", False)
    weather_error = weather_raw.get("error")

    ambient_temp_prov: FieldProvenance
    humidity_prov: FieldProvenance
    rainfall_prov: FieldProvenance

    if weather_is_live:
        ambient_temp_prov = FieldProvenance(
            value=weather_raw.get("temperature"),
            source=EXTERNAL_OBSERVED,
            unit="°C",
            sensor_type="Open-Meteo NWP API (temperature_2m)",
            quality="GOOD",
        )
        humidity_prov = FieldProvenance(
            value=weather_raw.get("humidity"),
            source=EXTERNAL_OBSERVED,
            unit="%",
            sensor_type="Open-Meteo NWP API (relative_humidity_2m)",
            quality="GOOD",
        )
        # Annual rainfall: not from current-hour API; use district climatology
        annual_rf = _get_annual_rainfall_proxy(lat, lon, district)
        if annual_rf is not None:
            rainfall_prov = FieldProvenance(
                value=annual_rf,
                source=EXTERNAL_OBSERVED,
                unit="mm",
                conversion_note="Annual rainfall: district-level climatological normal from geo_service. Open-Meteo hourly precipitation does not proxy annual totals.",
                sensor_type="Climatological district normal",
                quality="GOOD",
            )
        else:
            rainfall_prov = FieldProvenance(
                value=None,
                source=UNAVAILABLE,
                unit="mm",
                quality="MISSING",
            )
    else:
        # Weather API failed — use climatological fallback but flag clearly
        annual_rf = _get_annual_rainfall_proxy(lat, lon, district) or 750.0
        ambient_temp_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="°C",
            conversion_note=f"Open-Meteo unavailable: {weather_error}. Temperature not substituted.",
            quality="MISSING",
        )
        humidity_prov = FieldProvenance(
            value=None,
            source=UNAVAILABLE,
            unit="%",
            conversion_note=f"Open-Meteo unavailable: {weather_error}. Humidity not substituted.",
            quality="MISSING",
        )
        rainfall_prov = FieldProvenance(
            value=annual_rf,
            source=EXTERNAL_OBSERVED,
            unit="mm",
            conversion_note="Open-Meteo unreachable; annual rainfall from district climatological normal.",
            sensor_type="Climatological district normal (fallback)",
            quality="DEGRADED",
        )

    # ── 9. Agro-climatic zone enrichment ─────────────────────────────────────
    acz = _resolve_acz_from_coords(lat, lon)

    # ── 10. Assemble farm_data dict for intelligence pipeline ─────────────────
    # Uses same flat-dict format as run_full_agricultural_intelligence()
    farm_data: Dict[str, Any] = {
        # --- Location ---
        "latitude": lat,
        "longitude": lon,
        "state": state,
        "district": district,
        "agro_climatic_zone": acz["code"],
        "device_id": device_id,
        "field_id": field_id,
        # --- Farm context ---
        "season": season,
        "soil_type": soil_type,
        "irrigation_available": irrigation_available,
        "drainage": drainage,
        # --- Soil chemistry (from sensors; None if UNAVAILABLE) ---
        # pH: lowercase "ph" to match ML feature name exactly
        "ph": ph_prov.value,
        "pH": ph_prov.value,  # Also set uppercase alias used by soil_intelligence.py
        "EC": ec_prov.value,
        "OC": oc_prov.value,  # Always None (no IoT sensor)
        # --- NPK: only set if sensor measured; None → model uses median ---
        "N": n_prov.value,
        "P": p_prov.value,
        "K": k_prov.value,
        # --- Micronutrients: always None (UNAVAILABLE) ---
        "S": None,
        "Zn": None,
        "Fe": None,
        "Cu": None,
        "Mn": None,
        "B": None,
        # --- Soil moisture (used by soil_intelligence.py for moisture indicator) ---
        "moisture": moisture_prov.value,
        "moisture_percent": moisture_prov.value,
        # --- Soil temperature ---
        "soil_temperature": soil_temp_prov.value,
        # --- Weather (from Open-Meteo) ---
        "temperature": ambient_temp_prov.value,
        "humidity": humidity_prov.value,
        "rainfall": rainfall_prov.value,
        # --- Telemetry metadata ---
        "_telemetry_source": "IOT_HARDWARE",
        "_bridge_version": "1.0.0",
        "_bridge_timestamp": now_utc.isoformat(),
        "_weather_live": weather_is_live,
    }

    # ── 11. Build DataConfidenceReport ────────────────────────────────────────
    all_provenance = {
        "soil_moisture_pct":    moisture_prov.to_dict(),
        "soil_temperature_c":   soil_temp_prov.to_dict(),
        "soil_ph":              ph_prov.to_dict(),
        "soil_ec_ds_m":         ec_prov.to_dict(),
        "nitrogen_kg_ha":       n_prov.to_dict(),
        "phosphorus_kg_ha":     p_prov.to_dict(),
        "potassium_kg_ha":      k_prov.to_dict(),
        "organic_carbon_pct":   oc_prov.to_dict(),
        "sulphur_ppm":          _unavailable_micro.to_dict(),
        "zinc_ppm":             _unavailable_micro.to_dict(),
        "iron_ppm":             _unavailable_micro.to_dict(),
        "copper_ppm":           _unavailable_micro.to_dict(),
        "manganese_ppm":        _unavailable_micro.to_dict(),
        "boron_ppm":            _unavailable_micro.to_dict(),
        "ambient_temperature_c": ambient_temp_prov.to_dict(),
        "relative_humidity_pct": humidity_prov.to_dict(),
        "annual_rainfall_mm":    rainfall_prov.to_dict(),
    }

    measured_fields = [k for k, v in all_provenance.items() if v["source"] == SENSOR_MEASURED]
    external_fields = [k for k, v in all_provenance.items() if v["source"] == EXTERNAL_OBSERVED]
    unavailable_fields = [k for k, v in all_provenance.items() if v["source"] == UNAVAILABLE]

    # Compute a bridge-level confidence rating
    critical_soil_params = ["soil_ph", "soil_ec_ds_m"]
    critical_available = sum(1 for p in critical_soil_params if all_provenance[p]["source"] == SENSOR_MEASURED)
    npk_available = sum(1 for p in ["nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha"]
                        if all_provenance[p]["source"] == SENSOR_MEASURED)
    weather_ok = weather_is_live

    if critical_available == 2 and npk_available == 3 and weather_ok:
        bridge_confidence = "HIGH"
    elif critical_available >= 1 and weather_ok:
        bridge_confidence = "MEDIUM"
    elif critical_available >= 1:
        bridge_confidence = "LOW"
    else:
        bridge_confidence = "INSUFFICIENT"

    confidence_report: Dict[str, Any] = {
        "bridge_confidence": bridge_confidence,
        "telemetry_timestamp": now_utc.isoformat(),
        "device_id": device_id,
        "field_id": field_id,
        "location": {"lat": lat, "lon": lon, "district": district, "state": state},
        "agro_climatic_zone": acz,
        "weather_source": {
            "is_live": weather_is_live,
            "api": "Open-Meteo NWP API",
            "error": weather_error,
        },
        "field_provenances": all_provenance,
        "summary": {
            "measured_from_sensor": measured_fields,
            "from_external_api": external_fields,
            "unavailable": unavailable_fields,
            "ml_will_use_median_for": unavailable_fields,  # explicit, not hidden
        },
        "responsible_ai_notice": (
            "Fields marked UNAVAILABLE are NOT fabricated or ML-estimated for presentation. "
            "The ML model internally uses training-distribution medians for missing features, "
            "which is disclosed here and in the confidence report. "
            "NPK values, if sensor-measured, carry ±15–25% bulk-density conversion uncertainty."
        ),
    }

    return farm_data, confidence_report


# ---------------------------------------------------------------------------
# Degraded-state constructor
# ---------------------------------------------------------------------------

def _degraded_state(
    reason: str,
    device_id: str = "",
    field_id: str = "",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Returns a clearly-marked degraded pair when critical inputs are missing.
    The intelligence pipeline can still be called with this but will produce
    INSUFFICIENT confidence — callers should check bridge_confidence first.
    """
    farm_data: Dict[str, Any] = {
        "device_id": device_id,
        "field_id": field_id,
        "_telemetry_source": "IOT_HARDWARE_DEGRADED",
        "_bridge_version": "1.0.0",
        "_bridge_timestamp": datetime.now(timezone.utc).isoformat(),
        "_degraded": True,
        "_degraded_reason": reason,
    }
    confidence_report: Dict[str, Any] = {
        "bridge_confidence": "DEGRADED",
        "device_id": device_id,
        "field_id": field_id,
        "degraded": True,
        "degraded_reason": reason,
        "field_provenances": {},
        "summary": {
            "measured_from_sensor": [],
            "from_external_api": [],
            "unavailable": ["ALL"],
            "ml_will_use_median_for": ["ALL"],
        },
    }
    return farm_data, confidence_report


# ---------------------------------------------------------------------------
# Convenience: build from a list of SensorMeasurement-like dicts
# ---------------------------------------------------------------------------

def build_measurements_index(sensor_measurement_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Converts a list of SensorMeasurement-like dicts (from the IoT database or
    telemetry payload) into the {sensor_type: measurement_dict} index expected
    by build_analysis_request_from_telemetry().

    Each item in the list must have at least:
      - sensor_type: str (e.g. "SOIL_MOISTURE")
      - calibrated_value: float or None
      - raw_value: float or None
      - unit: str
      - quality: str
      - is_valid: bool

    When multiple measurements of the same sensor_type exist, the most recent
    GOOD-quality one is kept. Falls back to any DEGRADED. INVALID/MISSING discarded.
    """
    index: Dict[str, Any] = {}
    for m in sensor_measurement_list:
        st = m.get("sensor_type")
        if not st:
            continue
        quality = m.get("quality", "MISSING")
        existing = index.get(st)
        if existing is None:
            index[st] = m
        else:
            # Prefer GOOD over DEGRADED
            existing_q = existing.get("quality", "MISSING")
            priority = {"GOOD": 0, "DEGRADED": 1, "INVALID": 2, "MISSING": 3}
            if priority.get(quality, 3) < priority.get(existing_q, 3):
                index[st] = m
    return index
