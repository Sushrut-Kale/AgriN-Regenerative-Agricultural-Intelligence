# 📊 AgriN — Formal Data Confidence & Provenance Framework

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Active Standard  
> **Applicability:** All AgriN services, ML models, external data ingestion, and advisory generation

---

## 1. Motivation & Core Problem

In agricultural AI, outputs presented without confidence or provenance are dangerous. A machine learning model predicting a 92% statistical probability of sugarcane suitability based on a missing pH input is **not** high confidence; it is high uncertainty masked by model overconfidence.

Similarly, treating coarse district climatology benchmarks as if they were live on-farm sensor readings deceives farmers and downstream decision-makers.

Phase 2.5 introduces a **Formal Data Confidence & Provenance System** governed by one core rule:
> **Never invent numerical confidence. Where numerical confidence cannot be mathematically or empirically proven, use categorical confidence and report missing data transparently.**

---

## 2. Core Concepts & Taxonomy

```text
┌────────────────────────────────────────────────────────┐
│                   Data Confidence                      │
├────────────────────┬───────────────────────────────────┤
│ DataCoverage       │ FULL | PARTIAL | BASIC |          │
│                    │ UNAVAILABLE                       │
├────────────────────┼───────────────────────────────────┤
│ DataConfidence     │ HIGH | MEDIUM | LOW | UNKNOWN     │
├────────────────────┼───────────────────────────────────┤
│ DataResolution     │ POINT | PARCEL | VILLAGE |        │
│                    │ SUB_DISTRICT | DISTRICT | STATE | │
│                    │ NATIONAL                          │
├────────────────────┼───────────────────────────────────┤
│ DataSource         │ GOVERNMENT | SATELLITE | WEATHER  │
│                    │ | SOIL | ML_MODEL |               │
│                    │ AGRONOMIC_RULE | FARMER_INPUT |   │
│                    │ FIELD_OBSERVATION                 │
└────────────────────┴───────────────────────────────────┘
```

### 2.1 DataCoverage Levels

| Level | Definition | Example in AgriN |
| :--- | :--- | :--- |
| `FULL` | All required primary parameters are measured and directly available at target resolution. | A complete 12-parameter Soil Health Card lab test for the farmer's parcel. |
| `PARTIAL` | Primary parameters are present, but secondary or micronutrients are estimated or absent. | Soil test has N-P-K and pH, but lacks Zinc, Boron, and Electrical Conductivity. |
| `BASIC` | Only proxy, regional, or historical baseline values are available. | Using district-level 30-year average rainfall instead of on-farm or live station data. |
| `UNAVAILABLE` | No data exists. The parameter must be represented as `null` or explicitly tagged as missing. | Satellite vegetation indices (NDVI) before satellite API ingestion is integrated. |

### 2.2 DataConfidence Levels

Confidence in AgriN is evaluated through a multi-factor matrix:

$$\text{Confidence} = f(\text{Source Reliability}, \text{Spatial Resolution}, \text{Temporal Recency}, \text{Input Completeness})$$

| Level | Numerical Range (When Justified) | Decision Criterion |
| :--- | :--- | :--- |
| `HIGH` | $0.80 - 1.00$ | Verified field input + live localized weather + verified agronomic bounds. Zero critical gates violated. |
| `MEDIUM` | $0.50 - 0.79$ | Partial soil test or regional weather proxy. No severe agronomic violation, but parameters missing. |
| `LOW` | $0.20 - 0.49$ | Heavy reliance on national defaults or multiple missing key variables ($N, P, K, \text{pH}$). |
| `UNKNOWN` | `null` | Untested crop variety, uncalibrated sensor, or simulated prediction outside validation domain. |

### 2.3 Spatial Resolution Hierarchy

Advisories explicitly state their spatial resolution so farmers know the geographic granularity of the underlying data:

1. **`POINT`**: Farm GPS coordinates (in-situ soil core, farmer handheld device).
2. **`PARCEL`**: Field boundary polygon (cadastral boundary, 10m Sentinel-2 pixel).
3. **`VILLAGE`**: Revenue village (Gram Panchayat station).
4. **`SUB_DISTRICT`**: Block / Taluka / Tehsil level.
5. **`DISTRICT`**: District centroid (climatology, district agricultural office).
6. **`STATE`**: State agricultural university (SAU) recommendation package.
7. **`NATIONAL`**: ICAR national benchmark.

---

## 3. Data Provenance & The `DataSource` Entity

Every piece of data used to formulate an advisory carries provenance metadata:

```json
{
  "source_name": "Open-Meteo Real-Time Weather API",
  "source_type": "WEATHER",
  "source_url": "https://open-meteo.com",
  "retrieved_at": "2026-09-30T10:15:00Z",
  "coverage": "FULL",
  "resolution": "DISTRICT",
  "license": "CC BY 4.0"
}
```

### Supported Source Types
* `GOVERNMENT`: Official national/state repositories (DAC&FW, IMD, ICAR).
* `SATELLITE`: Multispectral Earth observation constellations (Copernicus Sentinel-2, Landsat-8/9).
* `WEATHER`: Numerical weather prediction models and live meteorological feeds.
* `SOIL`: Soil testing laboratories, official Soil Health Card portal.
* `ML_MODEL`: Validated internal statistical/ML model artifacts (e.g. Random Forest Classifier).
* `AGRONOMIC_RULE`: Peer-reviewed scientific constraints (ICAR / State Agricultural University package of practices).
* `FARMER_INPUT`: Self-reported declarations from the farm manager.
* `FIELD_OBSERVATION`: Ground-truth inspection logged by an agronomist or extension worker.

---

## 4. Standard Confidence Payload

Every major intelligence result (Crop Suitability, Soil Health, Regenerative Practices) exposes the standardized confidence payload:

```json
{
  "confidence": 0.85,
  "confidence_level": "HIGH",
  "coverage": "PARTIAL",
  "data_resolution": "DISTRICT",
  "data_timestamp": "2026-09-30T10:15:00Z",
  "sources": [
    {
      "source_name": "Farmer Soil Test Card",
      "source_type": "FARMER_INPUT",
      "coverage": "PARTIAL",
      "resolution": "POINT"
    },
    {
      "source_name": "Open-Meteo Real-Time Weather API",
      "source_type": "WEATHER",
      "coverage": "FULL",
      "resolution": "DISTRICT"
    }
  ]
}
```

---

## 5. Architectural Invariants

1. **No Simulated Confidence:** Confidence numbers must never be randomly generated or hardcoded to look plausible.
2. **Missing Over Proxy:** When a parameter is missing, mark it `missing` / `uncertain` with reduced confidence, rather than substituting an arbitrary constant without notice.
3. **Traceability:** Every `AgriculturalAdvisory` object generated by AgriN must embed its supporting `ConfidenceMetadata` and `DataSourceMetadata`.
