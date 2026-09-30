# 🏛️ AgriN Intelligence Architecture Specification

> **Platform:** AgriN — Regenerative Agricultural Intelligence  
> **Track:** SIH Track 4 — AgriN & Regenerative Agricultural Intelligence  
> **Global Theme:** BRICS Agricultural Cooperation  
> **Current Status:** `IMPLEMENTED` & Fully Verified  

---

## 1. Architectural Vision & Decoupled Pipeline

The core intelligence layer coordinates agricultural data ingestion, biophysical evaluation, and multi-horizon decision-support through an acyclic pipeline with clean service boundaries:

```
                  AGRIN INTELLIGENCE ORCHESTRATOR
                                │
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
    LOCATION                  SOIL                   WEATHER
(GeoService / ACZ)    (SoilIntelligence / SHC)  (Live / Climatology)
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ↓
                          CROP CONTEXT
                   (National Crop Calendar)
                                ↓
                      AGRICULTURAL ANALYSIS
                                ↓
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
 CROP SUITABILITY          SOIL HEALTH             CROP HEALTH
(ML + Hard Gates)     (Constraints & SOC)     (Diagnostic Guardrails)
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ↓
                      REGENERATIVE ADVISOR
              (8 Classes of Sustainable Practices)
                                ↓
                   FARM RESILIENCE PROTOTYPE
                   (Transparent 5-Part Index)
                                ↓
                     DATA CONFIDENCE ENGINE
                     (Mathematical Scoring)
                                ↓
                      FARM ADVISORY OUTPUT
               (Explainable: What, Why, Based-On)
```

---

## 2. Implementation Status by Component

| Subsystem Component | Module Location | Implementation Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Agricultural Orchestrator** | `backend/app/services/agrin_intelligence.py` | `IMPLEMENTED` | `test_master_agrin_intelligence_pipeline` passing |
| **Soil Intelligence Module** | `backend/app/services/soil_intelligence.py` | `IMPLEMENTED` | `test_soil_intelligence_*` passing |
| **Crop Suitability Engine** | `backend/app/services/crop_prediction.py` | `IMPLEMENTED` | Decoupled ML (Random Forest) + 15 ACZ rules |
| **Regenerative Advisor** | `backend/app/services/regenerative_advisor.py` | `IMPLEMENTED` | Evaluates 8 practice classes; strict missing data handling |
| **Farm Resilience Index** | `backend/app/services/farm_resilience.py` | `IMPLEMENTED` | Prototype multi-component score formula |
| **Disease Vision Architecture** | `backend/app/services/disease_service.py` | `ARCHITECTURE READY` | Strict `MODEL_NOT_DEPLOYED` guardrail |
| **Satellite Intelligence** | `backend/app/services/satellite_service.py` | `ARCHITECTURE READY` | Provider abstraction; strict `NOT_CONNECTED` |
| **Data Confidence Engine** | `backend/app/services/confidence_engine.py` | `IMPLEMENTED` | Mathematical scoring across 5 dimensions |
| **Interoperability Core** | `backend/app/services/agri_interoperability.py`| `IMPLEMENTED` | Country-neutral ADE schema (SI units, WGS84) |
| **Country Adapters** | `backend/app/adapters/` | `IMPLEMENTED` (India) / `ARCHITECTURE READY` (BRICS) | India reference active; BRICS interfaces defined |

---

## 3. Service Boundaries & API Contract

1. **Location Services (`geo_service.py`):**
   - Resolves centroid coordinates, 36 Indian States/UTs, 700+ districts, and 15 ICAR Agro-Climatic Zones.
   - Computes distance fallbacks via Haversine formula.

2. **Soil Intelligence (`soil_intelligence.py`):**
   - Ingests N, P, K, pH, EC, OC, and micronutrients (Zn, Fe, Cu, Mn, B).
   - Generates structured `SoilHealthProfile` classifying nutrient status, chemical properties, organic matter, and specific soil constraints (salinity, sodicity, acidity, OC depletion).

3. **Weather Intelligence (`weather_service.py`):**
   - Queries Open-Meteo REST API using geographic coordinates with fallback to district agro-climatic climatology.

4. **Regenerative Advisory Engine (`regenerative_advisor.py`):**
   - Evaluates 8 sustainable practice classes: crop rotation, diversification, cover crops, soil organic matter restoration, water conservation, minimum tillage, integrated nutrient management, and residue retention.
   - Handles missing data explicitly with `status="insufficient_data"`.

5. **Farm Resilience Index (`farm_resilience.py`):**
   - Computes transparent composite resilience score with full sub-score breakdown (soil health, water context, climate context, crop diversity, crop suitability).
   - Explicitly marked as prototype decision support.

6. **Interoperability Layer (`agri_interoperability.py` & `adapters/`):**
   - Normalizes domain objects into country-neutral schemas using standard SI units.
   - Decouples core agricultural logic from country-specific administrative hierarchies.
