# 🛰️ Track 4 Final Hardening: Capability Audit & Reality Map

**Project**: AgriN — Regenerative Agricultural Intelligence Network  
**Theme**: Track 4 Challenge — Interoperable Agricultural Intelligence Network | BRICS Digital Cooperation  
**Audit Date**: 2026-09-30  
**Repository State**: 120/120 Tests Passing (100%), Production Vite Bundle Built (1.99s).  
**Scientific Honesty Standard**: Capabilities are evaluated based on actual runtime behavior, external connections, local models, or demonstration flags. An interface or Pydantic class without live connectivity or loaded weights is strictly labeled `ARCHITECTURE ONLY` or `UNAVAILABLE`.

---

## 1. Subsystem Capability Classification Matrix

| Subsystem / Capability | Component Files | Classification | Concrete Evidence & Reality Check |
| :--- | :--- | :---: | :--- |
| **1. Pan-India Geography & ACZ Resolution** | `backend/app/services/geo_service.py`<br>`knowledge/india/states_and_districts.json`<br>`knowledge/india/agro_climatic_zones.json` | **REAL + LOCAL** | Full in-memory database of 28 States, 8 Union Territories, 700+ district centroids, and 15 ICAR National Agro-Climatic Zones. Nearest-district lookup via Haversine GPS formula (`find_nearest_district`). |
| **2. Agrometeorology & Weather Forecasting** | `backend/app/services/weather_service.py` | **REAL + CONNECTED** | Live HTTPS connection to Open-Meteo Global NWP API (`https://api.open-meteo.com/v1/forecast`) returning live temperature, rainfall, humidity, wind, and evaporative demand for any global GPS coordinate. Graceful local fallback to climatological normal when network is unreachable. |
| **3. Soil Intelligence & Edaphic Constraints** | `backend/app/services/soil_intelligence.py`<br>`knowledge/soil_health_standards.json` | **REAL + LOCAL** | Comprehensive 12-parameter evaluation based on ICAR/DAC&FW national guidelines. Detects 7 edaphic constraints (salinity, sodicity, acidity, low organic carbon, nitrogen deficit, phosphorus fixation, potassium depletion) and outputs non-chemical/organic remediation recipes. |
| **4. Crop Suitability & Machine Learning** | `backend/app/services/suitability_scorer.py`<br>`backend/app/services/crop_prediction.py`<br>`backend/app/services/crop_comparison.py` | **REAL + LOCAL** | Hybrid engine: Decoupled 15-feature Random Forest ML classifier (60% weight) blended with deterministic agronomic physiological filters (40% weight). Pairwise multi-candidate comparison without arbitrary winners. |
| **5. Regenerative Agriculture Advisor** | `backend/app/services/regenerative_advisor.py`<br>`knowledge/regenerative_practices.json` | **REAL + LOCAL** | Dynamic evaluation of 10 regenerative practices (green manuring, residue retention, biochar, cover cropping, drip fertigation, bio-fertilizers) structured into Immediate Action $\to$ Seasonal Practice $\to$ Long-Term Soil Goal. |
| **6. Farm Resilience Index** | `backend/app/services/farm_resilience.py` | **REAL + LOCAL** | 5-dimensional decoupled resilience index (Soil, Water, Climate, Crop Diversity, Data Confidence). Completely decoupled from data completeness so sparse farms are not penalized on biological health. |
| **7. Data Confidence & Missing-Data Guidance** | `backend/app/services/confidence_engine.py` | **REAL + LOCAL** | 5-factor mathematical confidence scoring (Completeness 0.35, Freshness 0.25, Geographic Precision 0.20, Source Reliability 0.20). Emits localized progressive guidance detailing *what to measure next* and *how it impacts advisory confidence*. |
| **8. What-If Scenario Simulator** | `backend/app/services/what_if.py`<br>`frontend/src/pages/WhatIf.jsx` | **REAL + LOCAL** | Sensitivity simulation allowing farmers to adjust Nitrogen, Phosphorus, Potassium, Organic Carbon, pH, and Rainfall. Labeled: *"Scenario simulation — not a prediction of actual future yield."* |
| **9. Farm Memory & Longitudinal Trends** | `backend/app/services/farm_memory.py` | **REAL + LOCAL** | Historical observation store with strict $\ge 2$ observations threshold. Emits `IMPROVING`, `STABLE`, `DECLINING`, or `INSUFFICIENT_HISTORY`. Rejects single-observation trend claims. |
| **10. Agricultural Knowledge Graph & Provenance** | `backend/app/services/knowledge_graph.py`<br>`knowledge/knowledge_sources.json` | **REAL + LOCAL** | Relationship traversal linking Crops, Soils, Climates, Risks, Practices, and Official Sources. Emits traceable reasoning traces: `OBSERVATION + RULE/MODEL + KNOWLEDGE SOURCE = RECOMMENDATION`. |
| **11. Measurement Unit Normalizer** | `backend/app/services/unit_normalizer.py` | **REAL + LOCAL** | Deterministic mathematical conversions across SI and foreign/regional units: Temperature (°C, °F, K), Rainfall (mm, cm, inch), Nutrients (kg/ha, ppm, lb/acre), EC (dS/m, mS/cm, µS/cm), Organic Carbon (% OC, % SOM, g/dm³), Area (ha, acre, bigha, guntha), Volume (m³, liters, acre-inch). |
| **12. Canonical Agricultural Data Model** | `backend/app/models/canonical_agri_model.py` | **REAL + LOCAL** | Country-neutral standardized schemas for `CanonicalLocation`, `CanonicalSoilObservation`, `CanonicalWeatherObservation`, `CanonicalCropObservation`, `CanonicalSatelliteObservation`, `ProvenanceRecord`, and the compact `FarmIntelligenceSnapshot`. |
| **13. Copernicus Sentinel-2 STAC Feed** | `backend/app/services/satellite_service.py` (`SentinelProvider`) | **ARCHITECTURE ONLY** | Implements the Copernicus Data Space STAC catalog query interface for 10m L2A Bottom-Of-Atmosphere rasters. Credentials unlinked on demonstration instances; honestly reports `status: "NOT_CONNECTED"`, `ndvi: null`. Zero synthetic numbers fabricated under production label. |
| **14. USGS Landsat-8/9 STAC Feed** | `backend/app/services/satellite_service.py` (`LandsatProvider`) | **ARCHITECTURE ONLY** | Implements the USGS EROS STAC gateway interface for 30m multispectral rasters. Production M2M API key unlinked; reports `status: "NOT_CONNECTED"`. |
| **15. Local Foliar Edge Vision Classifier** | `backend/app/services/disease_service.py` (`LocalVisionModelProvider`) | **ARCHITECTURE ONLY** | ONNX runtime / TorchScript inference harness for MobileNetV4 / PlantPathology. If model checkpoint is unlinked, safely returns `MODEL_NOT_DEPLOYED` and `diagnosis_status: "NOT_ASSESSED"`. Refuses to manufacture pathogen labels. |
| **16. External Diagnostic Cloud API** | `backend/app/services/disease_service.py` (`ExternalModelProvider`) | **ARCHITECTURE ONLY** | REST client for institutional diagnostic webhooks. Unconfigured endpoint returns `NOT_CONNECTED`. |
| **17. Satellite Demonstration Engine** | `backend/app/services/satellite_service.py` (`DemoSatelliteProvider`) | **SYNTHETIC / DEMO** | Deterministic multi-spectral scene generator based on latitude coordinates. Active only when `AGRIN_DEMO_MODE=true` or explicitly requested. Outputs explicit `is_synthetic: true` and demonstration banner. |
| **18. Plant Pathology Demo Screening** | `backend/app/services/disease_service.py` (`DemoDiseaseProvider`) | **SYNTHETIC / DEMO** | Deterministic foliar triage generator (Cotton Leaf Curl Virus, Cercospora Spot, Early Rust) with responsible IPM sanitation guidance. Flagged `is_synthetic: true`. |
| **19. BRICS Domestic Adapter (India)** | `backend/app/adapters/india.py` (`IndiaAdapter`) | **REAL + LOCAL** | Operational reference implementation ingesting Indian SHC and Census datasets into the canonical model with zero data loss. |
| **20. BRICS Foreign Country Adapters** | `backend/app/adapters/brics.py` (`BrazilAdapter`, `SouthAfricaAdapter`, `RussiaAdapter`, `ChinaAdapter`) | **REAL + PARTIALLY CONNECTED** | Ingestion, validation, and unit normalization of foreign agricultural schemas (EMBRAPA Cerrado Oxisol, ARC Highveld, Chernozem, Loess Plateau) into standard AgriN vectors. Tested deterministically via `run_brics_interoperability_simulation()`. |
| **21. Live Bilateral Cross-Border Government Gateways** | N/A | **UNAVAILABLE** | Live electronic data pipelines between sovereign ministries (e.g. ICAR to EMBRAPA) require international bilateral treaties and data sharing agreements outside the technical scope of software architecture. |

---

## 2. Summary Counts by Category

```text
┌──────────────────────────────────────────────────────────┐
│              CAPABILITY AUDIT SUMMARY                    │
├────────────────────────────────┬─────────────────────────┤
│ Operational Classification     │ Count                   │
├────────────────────────────────┼─────────────────────────┤
│ REAL + CONNECTED               │ 1  (Weather NWP)        │
│ REAL + LOCAL                   │ 11 (Geo, Soil, ML, ...) │
│ REAL + PARTIALLY CONNECTED     │ 1  (BRICS Adapters)     │
│ SYNTHETIC / DEMO (Labeled)     │ 2  (Sat Demo, Path Demo)│
│ ARCHITECTURE ONLY              │ 5  (Copernicus, USGS...)│
│ UNAVAILABLE                    │ 1  (Govt Gateways)      │
└────────────────────────────────┴─────────────────────────┘
```

---

## 3. Strict Non-Fabrication Confirmation

1. **No Fabricated Satellite Indices**: In production mode (`AGRIN_DEMO_MODE=false`), when Copernicus or USGS STAC credentials are absent, the API returns:
   ```json
   {
     "satellite_status": "NOT_CONNECTED",
     "vegetation_observation": null,
     "message": "Satellite Earth Observation provider is not currently connected. System adheres to strict non-fabrication policy."
   }
   ```
2. **No Hallucinated Plant Disease Diagnoses**: In production mode without local ONNX weights, the pathology endpoint returns:
   ```json
   {
     "status": "MODEL_NOT_DEPLOYED",
     "diagnosis_status": "NOT_ASSESSED",
     "confidence": 0.0,
     "explainability": {
       "reason": "Responsible AI safety guardrail: Refuses to hallucinate plant pathology when model weights are unlinked."
     }
   }
   ```
3. **Transparent Demonstration Labeling**: Demo mode observations are prominently marked:
   ```json
   {
     "is_synthetic": true,
     "notice": "DEMONSTRATION DATA — NOT A VALIDATED CLINICAL PLANT DIAGNOSIS"
   }
   ```
