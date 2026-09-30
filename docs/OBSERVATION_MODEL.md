# 🕒 AgriN — Time-Series Agricultural Observation Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Active Standard  
> **Target Schema:** `FarmObservation` / `farm_observations` table

---

## 1. Context: Transition From Static Sessions to Dynamic Observability

In Phase 1 and 2, AgriN treated a farm as an isolated static session (`FarmerSession`) accompanied by a single static `SoilRecord` and `EnvRecord`.

Real-world agriculture is inherently dynamic:
* Soil nitrate and moisture deplete continuously between irrigation cycles.
* Weather variables fluctuate hourly and daily across crop phenological stages.
* Satellite imagery generates new spectral reflectance observations every 5 days (Sentinel-2 constellation).
* Plant diseases manifest over days following humidity spikes or fungal spore dispersal.

Phase 2.5 establishes the **`FarmObservation` model**: an extensible, time-series data foundation for multi-source temporal intelligence.

---

## 2. Core Observation Data Model

The `FarmObservation` model is decoupled from any single sensor or feature, supporting any biophysical observation with standardized physical units and provenance.

### 2.1 Schema Definition

```text
FarmObservation:
├── observation_id : String (UUID / unique index)
├── farm_id        : String (session_id or registered farm UUID)
├── timestamp      : DateTime (UTC ISO-8601)
├── observation_type: Enum (SOIL | WEATHER | CROP | SATELLITE | DISEASE | IRRIGATION | FIELD_VISIT)
├── parameter_name : String (e.g., "available_nitrogen", "surface_temperature", "ndvi", "powdery_mildew")
├── value          : Float (numerical value)
├── unit           : String (standardized SI / agronomic unit: "kg/ha", "°C", "mm", "index", "percent")
├── source         : String (e.g., "SoilLab_Pune", "Open-Meteo", "Sentinel-2A", "FarmerInspection")
├── latitude       : Float (WGS84 coordinate of observation)
├── longitude      : Float (WGS84 coordinate of observation)
├── confidence     : Float (0.0 to 1.0 confidence score of measurement)
└── metadata       : JSON (extensible context: sensor model, depth cm, lab ID, bounding polygon)
```

---

## 3. Observation Types & Parameter Standards

| Type | Standard Parameters | Units | Expected Source |
| :--- | :--- | :--- | :--- |
| `SOIL` | `N`, `P`, `K`, `S`, `Zn`, `Fe`, `Cu`, `Mn`, `B`, `ph`, `EC`, `OC`, `soil_moisture` | `kg/ha`, `ppm`, `pH`, `dS/m`, `%` | Soil Health Card, Soil probes, IoT sensors |
| `WEATHER` | `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed`, `solar_radiation` | `°C`, `%`, `mm`, `m/s`, `MJ/m²` | Open-Meteo, IMD Automatic Weather Stations (AWS) |
| `CROP` | `canopy_height`, `crop_stage`, `stand_count`, `biomass_est` | `cm`, `stage_code`, `plants/m²`, `kg/ha` | Extension scouting, Drone survey, Farmer log |
| `SATELLITE` | `NDVI`, `NDWI`, `EVI`, `SAVI`, `surface_reflectance_b04`, `surface_reflectance_b08` | Unitless index ($[-1.0, 1.0]$), reflectance $[0.0, 1.0]$ | Copernicus Sentinel-2 MSI, Landsat-8/9 |
| `DISEASE` | `leaf_spot_severity`, `rust_incidence`, `pest_trap_count` | `%`, `severity_score (1-9)`, `insects/trap` | Plant pathology image model, Scout report |
| `IRRIGATION`| `water_applied`, `flow_rate`, `salinity_ec` | `mm`, `liters/hr`, `dS/m` | Drip fertigation controller, Water meter |
| `FIELD_VISIT` | `weed_density`, `lodging_percentage`, `tillage_depth` | `plants/m²`, `%`, `cm` | KVK agronomist, Soil surveyor |

---

## 4. Database Implementation & APIs

Implemented in `backend/app/database/db.py`:

```python
class FarmObservationRecord(Base):
    __tablename__ = "farm_observations"

    id = Column(Integer, primary_key=True)
    observation_id = Column(String, unique=True, index=True)
    farm_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    observation_type = Column(String, index=True)
    parameter_name = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    source = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
```

### Endpoints:
* `POST /api/farms/{farm_id}/observations`: Ingests single or batch observations with validation.
* `GET /api/farms/{farm_id}/observations?observation_type=SOIL`: Returns time-series chronological feed for a farm.

---

## 5. Architectural Role in Future Phases

1. **Seasonal Trend Detection:** Enables detection of nitrogen leaching over the monsoon.
2. **Satellite Anomaly Cross-Checking:** When satellite NDVI drops, the system inspects recent `WEATHER` observations (drought/hail) and `DISEASE` observations before triggering alerts.
3. **Model Retraining Dataset:** Verified time-series observations become ground-truth features for retraining subsequent ML models.
