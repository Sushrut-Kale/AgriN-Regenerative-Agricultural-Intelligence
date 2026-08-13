# FarmFriend AI — Data Catalog & Provenance Log

**Version**: 2.0  
**Updated**: 2026-08-13  
**Catalog Maintainer**: Data Engineering Team  

---

## 1. Data Provenance & Source Catalog

| Dataset ID | Dataset Name | Organization / Source | Geographic Scope | Time Scope | Variables Captured | License | Status |
|---|---|---|---|---|---|---|---|
| `DS_A_SOIL` | Soil Health Card Sample Database | Govt. of India / DAC&FW | India (Maharashtra Focus) | 2017–2023 | N, P, K, S, Zn, Fe, Cu, Mn, B, pH, EC, OC, Location | OGDL India | Processed (`data/processed/`) |
| `DS_B_WEATHER` | IMD District Weather Summaries | India Meteorological Dept. | Maharashtra Districts | 1990–2023 | Temperature (min/max/mean), Rainfall, Humidity | Open Access | Processed (`data/processed/`) |
| `DS_C_CROP` | Crop Production Statistics | Ministry of Agriculture, GoI | All India Districts | 1997–2021 | State, District, Season, Crop, Area, Production, Yield | OGDL India | Processed (`data/processed/`) |
| `DS_D_KNOWLEDGE` | Crop Requirements Knowledge Base | ICAR / TNAU / FAO / VNMKV | National / Maharashtra | Current | Crop, pH, NPK, Micronutrients, Temp, Rain, Soil, Irrigation | Curated | Active (`knowledge/crop_requirements.json`) |
| `DS_E_REGIONAL` | Maharashtra Agro-Climatic Zones | ICAR-NBSS&LUP | Maharashtra (36 Districts)| Current | Agro-climatic zone, soil series, major crop patterns, rainfall zone | Curated | Active (`knowledge/maharashtra_data.json`) |
| `DS_F_FEEDBACK` | Farmer Feedback Log | FarmFriend AI Production DB | Live Application | Real-time | Session ID, Crop, Rating, Reason, Actual Outcome, Yield | Internal / Anonymized | Live (`backend/farmfriend.db`) |

---

## 2. Directory Structure Conventions

```
s:\fram friend\data\
├── raw\                             # Untouched raw source datasets (NEVER modified)
│   ├── crop_recommendation_synthetic.csv  # Legacy benchmark file (synthetic)
│   ├── dataset_metadata.json
│   ├── india_district_crop_production.csv # Open GoI production statistics
│   └── soil_health_card_maharashtra.csv   # Real soil health observation records
├── processed\                       # Cleaned, unit-normalized parquet/CSV data
│   ├── unified_crop_soil_dataset.csv  # Verified training dataset
│   └── dataset_provenance.json
└── scripts\                         # Reproducible data pipelines
    ├── build_training_dataset.py
    └── clean_and_normalize_data.py
```

---

## 3. Data Ingestion & Cleaning Rules
1. **Raw Data Preservation**: Files in `data/raw/` are strictly read-only.
2. **Missing Data Protocol**: Missing nutrient values are marked as `NaN` / `null`. Never convert missing to `0` or replace with global averages without explicit missing indicator flags.
3. **Outlier Policy**: Extreme soil or rainfall values are flagged using IQR bounds but NOT deleted if agronomically plausible for Indian soils (e.g. sodic soils with pH > 9.0 or saline Vertisols).
4. **Deterministic Hashes**: Every generated dataset file records SHA-256 hash, row count, feature schema, and generation timestamp in `dataset_provenance.json`.
