# 🌾 FarmFriend AI — Comprehensive Product Handover & Technical Specification

**Product Version:** 2.0.0  
**Status:** Production Ready  
**Repository:** [https://github.com/Sushrut-Kale/farm-friend.git](https://github.com/Sushrut-Kale/farm-friend.git)  
**Primary Tech Stack:** Python (FastAPI, scikit-learn), React 19 (Vite, Tailwind CSS), SQLite, Open-Meteo API  

---

## 📋 Table of Contents
1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Machine Learning Engine & Pipeline](#3-machine-learning-engine--pipeline)
4. [Knowledge Base & Agronomic Rule Engines](#4-knowledge-base--agronomic-rule-engines)
5. [Backend API & Business Logic](#5-backend-api--business-logic)
6. [Database Schema & Data Persistence](#6-database-schema--data-persistence)
7. [Frontend Architecture & User Flows](#7-frontend-architecture--user-flows)
8. [External Integrations](#8-external-integrations)
9. [Verification, Quality Assurance & Test Suite](#9-verification-quality-assurance--test-suite)
10. [Deployment & Operations Guide](#10-deployment--operations-guide)
11. [Maintenance, Retraining & Feedback Loop](#11-maintenance-retraining--feedback-loop)
12. [Known Limitations & Roadmap](#12-known-limitations--roadmap)

---

## 1. Executive Summary & Purpose

**FarmFriend AI** is an explainable AI decision-support platform designed to empower farmers, agronomists, and agricultural officers with data-driven crop suitability recommendations. 

Traditional crop recommendations rely either purely on basic rule lookups (which fail to capture non-linear multi-variable interactions) or black-box machine learning models (which lack farmer trust and fail to explain *why* a crop is suitable or what limiting factors exist). FarmFriend AI bridges this gap by combining:
1. **Multi-variable Machine Learning** (Random Forest trained on 15 soil and climate features).
2. **Domain-Specific Agronomic Guardrails** (ICAR, TNAU, and Government of India Soil Health Card standards).
3. **Transparent Explainability** (SHAP feature contribution breakdowns, limiting factor diagnosis, and customized fertilizer recommendations).
4. **Interactive Simulators** ("What-If" parameter sandbox and target-crop feasibility analysis).

---

## 2. High-Level Architecture

The system is architected as a decoupled, full-stack web application:

```
┌────────────────────────────────────────────────────────┐
│               Frontend: React + Vite                   │
│   (Wizard flow, Crop Cards, Radar Charts, What-If)     │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON API (:5173 -> :8000)
┌───────────────────────────▼────────────────────────────┐
│               Backend: FastAPI Core                    │
│   ├── Validation Service (SHC limits, ranges)          │
│   ├── Weather Service (Open-Meteo Integration)         │
│   ├── ML Predictor (Scikit-Learn Random Forest)        │
│   ├── Suitability Scorer & Agronomic Guardrails        │
│   ├── Feasibility & What-If Simulation Services        │
│   └── Natural Language & SHAP Explainer Engine         │
└───────┬───────────────────┬────────────────────┬───────┘
        │                   │                    │
┌───────▼────────┐  ┌───────▼────────┐   ┌───────▼───────┐
│ Knowledge Base │  │ Model Artifacts│   │ SQLite Storage│
│ (JSON / YAML)  │  │ (.joblib/json) │   │(farmfriend.db)│
└────────────────┘  └────────────────┘   └───────────────┘
```

---

## 3. Machine Learning Engine & Pipeline

### 3.1 Training Data & Features
- **Dataset:** Unified multi-source agricultural dataset enriched with ICAR/TNAU agronomic requirements (`data/scripts/build_training_dataset.py`).
- **Target Variable:** 23 distinct crop classes (`rice`, `cotton`, `soybean`, `chickpea`, `maize`, `coffee`, `pigeonpeas`, `kidneybeans`, `mungbean`, `blackgram`, `lentil`, `pomegranate`, `banana`, `mango`, `grapes`, `watermelon`, `muskmelon`, `apple`, `orange`, `papaya`, `coconut`, `jute`, `mothbeans`).
- **Feature Space (15 features):**
  - Macronutrients: `N`, `P`, `K` (kg/ha)
  - Micronutrients: `S`, `Zn`, `Fe`, `Cu`, `Mn`, `B` (ppm / mg/kg)
  - Soil Chemistry: `ph`, `EC` (dS/m), `OC` (%)
  - Climate: `temperature` (°C), `humidity` (%), `rainfall` (mm)

### 3.2 Model Specifications
- **Algorithm:** Random Forest Classifier (`ml/train.py`)
- **Hyperparameters:** `n_estimators=200`, `max_depth=16`, `min_samples_split=4`, `random_state=42`
- **Performance:**
  - Test Accuracy: **~79.7%**
  - Weighted F1-Score: **~0.794**
  - Cross-Validation Mean Accuracy: **~79.2%**
- **Model Artifacts** (`models/`):
  - `crop_model_v1.joblib`: Serialized trained model
  - `model_metadata.json`: Feature importance weights, cross-validation metrics, and class mappings
  - `confusion_matrix.png` & `feature_importance.png`: Visual evaluation artifacts

### 3.3 Explainability Framework
- SHAP-inspired tree feature contributions calculate the contribution of every soil and environmental parameter relative to baseline crop thresholds.
- Factors are grouped into:
  - **Supporting Factors:** Variables in the optimum range that increase suitability.
  - **Limiting Factors:** Variables outside the optimum range that penalize score and require amendment.

---

## 4. Knowledge Base & Agronomic Rule Engines

Located in `knowledge/`:
- `crop_requirements.json`: Precise minimum, maximum, and optimum thresholds for N, P, K, pH, rainfall, and temperature for all 23 supported crops.
- `shc_thresholds.json`: Government of India Soil Health Card (SHC) standard classification cutoffs (`Very Low`, `Low`, `Medium`, `High`, `Very High`, `Toxic`).
- `crop_calendar.json`: Sowing, harvesting, and duration metadata per agro-climatic season (Kharif, Rabi, Zaid).
- `maharashtra_data.json`: District-level soil benchmarks and agro-climatic zone mapping.
- `units.yaml`: Standardized units dictionary ensuring conversion consistency across the platform.

---

## 5. Backend API & Business Logic

FastAPI application entry point: `backend/app/main.py`

### 5.1 Endpoints Summary

| Endpoint | Method | Input Schema | Functionality |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | None | Service liveness probe. |
| `/api/validate-farm` | `POST` | `FarmInput` | Validates soil tests against physical limits and agronomic warnings. |
| `/api/predict-crops` | `POST` | `FarmInput` | Computes ML prediction blended with SHC rule filters to return top recommendations. |
| `/api/crop-details` | `POST` | `CropDetailRequest` | Returns deep agronomic breakdown, SHAP factors, and fertilizer recommendations. |
| `/api/feasibility-check` | `POST` | `FeasibilityRequest` | Evaluates single target crop suitability score and limiting constraints. |
| `/api/what-if` | `POST` | `WhatIfRequest` | Real-time simulation of soil/climate adjustments against baseline. |
| `/api/feedback` | `POST` | `FeedbackCreate` | Stores ground-truth farmer harvest outcomes and ratings. |
| `/api/analytics` | `GET` | None | Returns aggregated usage statistics and model comparison benchmarks. |
| `/api/model-info` | `GET` | None | Returns metadata, training date, feature importance, and performance scores. |

---

## 6. Database Schema & Data Persistence

Storage engine: SQLite (`backend/farmfriend.db`) managed via `backend/app/database/db.py`.

### 6.1 Tables
1. **`telemetry`**:
   - `id` (INTEGER PRIMARY KEY)
   - `event_type` (TEXT: `analysis`, `feasibility_check`, `whatif_run`)
   - `crop_name` (TEXT)
   - `suitability_score` (REAL)
   - `timestamp` (DATETIME)
2. **`feedback`**:
   - `id` (INTEGER PRIMARY KEY)
   - `crop_name` (TEXT)
   - `farmer_name` (TEXT)
   - `district` (TEXT)
   - `actual_yield` (REAL)
   - `rating` (INTEGER)
   - `comments` (TEXT)
   - `created_at` (DATETIME)

---

## 7. Frontend Architecture & User Flows

Built with React 19 and Vite (`frontend/`):

### 7.1 Key Pages (`frontend/src/pages/`)
1. `Home.jsx`: Landing view, feature overview, and quick-start entry point.
2. `FarmDetails.jsx`: Wizard Step 1 — Regional selection, season, farm size, soil type.
3. `SoilTest.jsx`: Wizard Step 2 — NPK, pH, EC, OC, and micronutrient inputs.
4. `Environment.jsx`: Wizard Step 3 — Climate and live weather auto-fetch.
5. `Recommendations.jsx`: Top crop recommendation cards, suitability meters, and radar comparison.
6. `CropDetails.jsx`: In-depth SHAP feature explainability, agronomic schedule, and soil amendment recommendations.
7. `IWantToGrow.jsx`: Target crop feasibility checker.
8. `WhatIf.jsx`: Real-time interactive simulation sliders.
9. `Dashboard.jsx`: Analytics, usage charts, and ML algorithm benchmarks.

### 7.2 State Management
- `AppContext.jsx`: Global React context maintaining wizard inputs, user modifications, and active crop analysis across navigation transitions.

---

## 8. External Integrations

- **Open-Meteo Weather API** (`backend/app/services/weather_service.py`):
  - Fetches real-time temperature, relative humidity, and annual/seasonal rainfall by latitude and longitude.
  - Built-in fallback mechanism to regional historical averages if network fails or coordinates are missing.

---

## 9. Verification, Quality Assurance & Test Suite

All 35 automated tests are passing (`pytest`):

```bash
pytest -v
```

### Test Coverage Summary:
- `tests/test_agricultural_validation.py`: Verifies boundary conditions, toxic thresholds, and input sanitation.
- `tests/test_api.py`: Validates FastAPI route integrity, status codes, and JSON response contracts.
- `tests/test_services.py`: Validates scoring algorithms, SHAP calculation, and What-If simulation accuracy.
- `tests/test_weather_service.py`: Tests live weather requests and fallback resilience.
- `tests/test_parbhani_case.py`: Real-world end-to-end Marathwada Black Soil case study.
- `tests/test_feedback.py`: Verifies SQLite transaction safety and telemetry counters.

---

## 10. Deployment & Operations Guide

### 10.1 Running Locally
```bash
# Terminal 1: Backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 10.2 Production Deployment (Docker / Cloud)
- **Backend:** Can be containerized via `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4`.
- **Frontend:** Build static bundle via `npm run build` in `frontend/` and serve via Nginx or Cloudflare Pages.

---

## 11. Maintenance, Retraining & Feedback Loop

### Retraining the Model
When new soil records or augmented datasets are added:
1. Update raw data in `data/` or modify `data/scripts/build_training_dataset.py`.
2. Run `python data/scripts/build_training_dataset.py`.
3. Run `python ml/train.py`.
4. Artifacts in `models/` will automatically be re-generated and picked up on next backend restart.

---

## 12. Known Limitations & Roadmap

- **Current Limitations:**
  - Micronutrient data defaults to median regional values if farmer has only basic NPK test results.
  - Weather forecasts rely on current snapshot data rather than multi-month seasonal climate forecasts.
- **Future Roadmap:**
  - Multi-language voice interface (Marathi, Hindi, Telugu).
  - Integration with satellite NDVI data (Sentinel-2) for real-time vegetative health monitoring.
  - Soil amendment cost calculator integrated with local mandi pricing.
