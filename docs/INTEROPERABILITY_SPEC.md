# 🌐 Interoperability Specification & BRICS Country Adapters

> **Module:** `backend/app/services/agri_interoperability.py`  
> **Adapter Package:** `backend/app/adapters/`  
> **Global Theme:** BRICS Agricultural Cooperation  
> **Status:** `IMPLEMENTED` (India Reference Deployment) / `ARCHITECTURE READY` (BRICS Adapters)  

---

## 1. Overview & Country-Neutral Philosophy

To achieve cross-border agricultural interoperability without forcing one country's administrative hierarchy onto another, AgriN introduces the **AgriN Data Exchange (ADE)** specification:
- Pure SI standard units (kg/ha, mg/kg, mm, °C, dS/m).
- Standard WGS84 coordinates.
- Decoupled administrative hierarchies (country-neutral `location_context`).
- Country-specific rules, regional crops, and soil thresholds are isolated inside **Country Adapters**.

---

## 2. Core Normalized ADE Entities

Implemented in `backend/app/services/agri_interoperability.py`:
- `ADE_Location`: Canonical coordinates, elevation, and administrative tuple.
- `ADE_SoilObservation`: Normalized physicochemical test results.
- `ADE_WeatherObservation`: Temperature, relative humidity, precipitation, solar radiation.
- `ADE_CropObservation`: Botanical name, local cultivar, growth stage, canopy cover.
- `ADE_Advisory`: Category, urgency, agronomic actions, and 5-part explainability envelope.
- `ADE_RegenerativePractice`: Practice taxonomy code, agro-ecological suitability, and co-benefits.

---

## 3. Country Adapter Architecture

```
                    AGRICULTURAL CORE (ADE)
                              │
        ┌───────────────┬─────┴─────────┬───────────────┐
        ↓               ↓               ↓               ↓
  INDIA ADAPTER   BRAZIL ADAPTER  RUSSIA ADAPTER  CHINA ADAPTER
(Fully Deployed)   (Arch Ready)    (Arch Ready)    (Arch Ready)
        │               │               │               │
  • ICAR SHC      • Embrapa Cerrado• Chernozem Org• Chinese CAS
  • 15 ACZs       • Soy/Maize Rot  • Spring Wheat • Paddy Rice
  • 36 States/UTs • Zarc Agro-Risk • Rosstat ACZ  • Eco-Farming
```

### Registered Adapters:
1. `IndiaAdapter` (`ACTIVE`): Reference implementation utilizing ICAR 12-parameter standards, 15 Planning Commission zones, and 700+ districts.
2. `BrazilAdapter` (`ARCHITECTURE_READY`): Embrapa-aligned tropical soil and Zarc agro-climatic zoning interface.
3. `RussiaAdapter` (`ARCHITECTURE_READY`): Chernozem organic matter preservation and boreal crop cycles.
4. `ChinaAdapter` (`ARCHITECTURE_READY`): Intensive cropping diversification and precision nutrient stewardship.
5. `SouthAfricaAdapter` (`ARCHITECTURE_READY`): ARC water-scarcity resilience and dryland rotation.

---

## 4. Verification Evidence

Automated test: `tests/test_track4_evolution.py::test_country_adapters_and_ade`
- Verified: India adapter returns active status and resolves states/districts.
- Verified: BRICS adapters (`BR`, `RU`, `CN`, `ZA`) instantiate cleanly and report `ARCHITECTURE_READY`.
- Verified: ADE schemas serialize and validate standard SI measurements without country-specific lock-in.
