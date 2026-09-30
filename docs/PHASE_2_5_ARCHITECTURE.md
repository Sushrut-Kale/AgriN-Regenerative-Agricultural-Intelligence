# 🏗️ AgriN — Phase 2.5 Architecture: Pan-India Intelligence Hardening

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Date:** September 2026  
> **Status:** Production Architecture Standard

---

## 1. Unified System Architecture

```text
                         AGRIN
                           │
                 PAN-INDIA FARM LAYER
            (28 States + 8 UTs + WGS84 GPS)
                           │
             ┌─────────────┼─────────────┐
             │             │             │
           SOIL         WEATHER       LOCATION
        (12 SHC params) (Live Open-   (Centroid +
                         Meteo / IMD)  Boundary GeoJSON)
             │             │             │
             └─────────────┼─────────────┘
                           │
                    FARM OBSERVATIONS
               (Time-Series FarmObservation)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
     ML MODEL          SATELLITE           DISEASE
   (Random Forest    (Sentinel-2 MSI     (Pathology
     Classifier)     Ready / Indices)    Triage Model)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                AGRICULTURAL INTELLIGENCE
            (Agronomic Rules, ACZ Calendars,
             Gates, Data Confidence & Provenance)
                           │
            ┌──────────────┼──────────────┐
            │              │              │
          CROP          REGENERATIVE    RISK
       RECOMMENDATION   PRACTICES      DETECTION
       (Multi-Factor)  (10+ ICAR/CRIDA (Heat, Drought,
                        Practices)      Deficiencies)
            │              │              │
            └──────────────┼──────────────┘
                           │
                    AI ADVISORY ENGINE
             (Canonical AgriculturalAdvisory)
                           │
                    FARMER ACTION
                           │
                    FEEDBACK LOOP
              (Action Taken & Outcome Logs)
                           │
                    DATA / LEARNING
                           │
                INTEROPERABILITY LAYER
                  (AgriN Data Exchange)
                           │
                    FUTURE BRICS
                    COOPERATION
           (India, Brazil, Russia, China, SA)
```

---

## 2. Key Subsystems Introduced in Phase 2.5

### 2.1 Formal Data Confidence & Provenance System
* **Coverage:** `FULL`, `PARTIAL`, `BASIC`, `UNAVAILABLE`
* **Confidence Levels:** `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`
* **Spatial Granularity:** `POINT`, `PARCEL`, `VILLAGE`, `SUB_DISTRICT`, `DISTRICT`, `STATE`, `NATIONAL`
* **Provenance:** Every result links back to its origin authority (IMD, ICAR, Open-Meteo, SHC, ML Model).
* *Reference:* `docs/DATA_CONFIDENCE.md`

### 2.2 Decoupled Agricultural Intelligence Pipeline
* **ML Model $\neq$ Agricultural Truth:** Model produces statistical probabilities; the Agricultural Intelligence Layer evaluates hard eligibility gates, regional calendars, and water regimes.
* **Explanation Layer:** LLMs contextualize pre-validated JSON without hallucinating agronomic facts.
* *Reference:* `docs/ADVISORY_ENGINE.md`

### 2.3 Time-Series Farm Observation Model
* Table `farm_observations` in SQLite; supports multi-sensor tracking over time (`SOIL`, `WEATHER`, `CROP`, `SATELLITE`, `DISEASE`, `IRRIGATION`, `FIELD_VISIT`).
* *Reference:* `docs/OBSERVATION_MODEL.md`

### 2.4 Honest Farm Health Snapshot
* Aggregates soil, water, crop, weather risk, and regenerative readiness.
* Explicitly returns `UNAVAILABLE` for unmeasured satellite and disease indices (zero data fabrication).
* Service: `backend/app/services/farm_health_service.py`

### 2.5 Canonical Agricultural Advisory
* Standardized output schema (`AgriculturalAdvisory`) with category, priority, recommendation, reasoning, actions, confidence, and provenance.
* Service: `backend/app/services/advisory_service.py`

### 2.6 Satellite Intelligence Architecture
* Sentinel-2 MSI and Landsat-8/9 processing pipeline blueprint: cloud masking, NDVI, NDWI, EVI, SAVI formulations.
* Schema: `SatelliteObservation`.
* *Reference:* `docs/SATELLITE_INTELLIGENCE_ARCHITECTURE.md`

### 2.7 Crop Disease Diagnosis Architecture
* Diagnostic workflow from farmer image to quality check, model prediction, and KVK expert review.
* Lifecycle states: `NOT_ASSESSED`, `SUSPECTED`, `LIKELY`, `CONFIRMED`, `REVIEW_REQUIRED`.
* *Reference:* `docs/DISEASE_INTELLIGENCE_ARCHITECTURE.md`

### 2.8 Regenerative Agriculture Knowledge & Engine
* Structured repository of 10 practices (`knowledge/regenerative/practices.json`).
* Engine evaluates biophysical synergy (`backend/app/services/regenerative_service.py`).
* Component-level readiness framework across 7 dimensions without arbitrary scores.
* *Reference:* `docs/REGENERATIVE_INTELLIGENCE_ARCHITECTURE.md`

### 2.9 Multilingual Architecture
* Complete decoupling of agronomic knowledge core from localization rendering across 12 Indian languages.
* *Reference:* `docs/MULTILINGUAL_ARCHITECTURE.md`

### 2.10 Farmer Feedback Loop
* Table `advisory_feedback` tracking farmer actions (`accepted`, `rejected`, `partially_followed`) and observed outcomes (`outcome_positive`, `outcome_negative`).
* Endpoint: `POST /api/advisory/feedback`.

### 2.11 BRICS Interoperability Abstraction
* AgriN Data Exchange (ADE) using SI units and WGS84 for cross-border cooperation with Brazil, Russia, China, and South Africa.
* *Reference:* `docs/BRICS_INTEROPERABILITY_ARCHITECTURE.md`

---

## 3. Database Schema Overview

```text
SQLite: backend/farmfriend.db
├── farmer_sessions          (session_id, country, state, district, sub_district, village, lat, lon, area_hectares, boundary_geojson, ACZ, season)
├── soil_records             (session_id, N, P, K, S, Zn, Fe, Cu, Mn, B, ph, EC, OC, soil_type)
├── env_records              (session_id, temperature, humidity, rainfall)
├── predictions              (session_id, model_version, top_crop, top_score, ranked_crops_json, data_confidence)
├── feasibility_records      (session_id, chosen_crop, suitability_score, feasibility_outcome, result_json)
├── whatif_records           (session_id, crop_name, before_score, after_score, score_change, changed_params_json)
├── feedback_records         (feedback_id, session_id, recommended_crop, rating, reason, crop_performance, actual_yield)
├── farm_observations        (observation_id, farm_id, timestamp, observation_type, parameter_name, value, unit, source, confidence, metadata_json)
├── agricultural_advisories  (advisory_id, farm_id, category, priority, title, recommendation, reasoning_json, actions_json, confidence_json, data_sources_json)
└── advisory_feedback        (feedback_id, advisory_id, farm_id, action_taken, outcome, notes)
```
