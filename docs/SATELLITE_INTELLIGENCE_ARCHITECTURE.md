# 🛰️ AgriN — Satellite Intelligence Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Architecture Blueprint & Implementation Roadmap  
> **Target Constellations:** European Space Agency (ESA) Copernicus Sentinel-2 MSI & NASA/USGS Landsat-8/9

---

## 1. Executive Summary & Honest Baseline

### Current State (Phase 2.5)
* **Architecture and Data Model Only.**
* AgriN provides the standardized `SatelliteObservation` schema and ingestion interface.
* **No fake satellite data is generated or displayed.** In all API responses and frontend dashboards, satellite vegetation metrics are marked explicitly as `UNAVAILABLE` with status `null` until live satellite ingestion is integrated.

### Next Implementation Phase (Phase 3.0)
* Integration of Copernicus Open Access / Google Earth Engine (GEE) REST API for automated Sentinel-2 surface reflectance scene queries.

### Future Phase (Phase 4.0)
* Sub-parcel anomaly detection, multi-temporal phenology tracking, and automated satellite-driven crop stress alerts.

---

## 2. End-to-End Satellite Processing Pipeline

```text
┌────────────────────────────────────────────────────────┐
│                   1. Farm Boundary                     │
│        (Farm Point coordinate or GeoJSON Polygon)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 2. Geospatial Query                    │
│      (Query Copernicus Data Space / GEE STAC API)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 3. Satellite Scene                     │
│      (Retrieve Sentinel-2 Level-2A BOA Reflectance)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 4. Cloud Filtering                     │
│     (Scene Classification Layer (SCL) & QA60 Mask)     │
│        (Exclude if parcel cloud cover > 20%)           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               5. Spectral Processing                   │
│        (Extract B02-Blue, B03-Green, B04-Red,          │
│            B08-NIR, B11-SWIR, B12-SWIR)                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               6. Vegetation Indices                    │
│     Compute NDVI, NDWI, EVI, SAVI across parcel pixels │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               7. Temporal Comparison                   │
│   (Compare with baseline 15-day / 30-day moving mean)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              8. Crop Stress Detection                  │
│    (Classify vegetative vigor anomaly or water stress) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              9. Agricultural Advisory                  │
│      (Generate canonical AgriculturalAdvisory)         │
└────────────────────────────────────────────────────────┘
```

---

## 3. Mathematical Definitions of Spectral Indices

### 3.1 Normalized Difference Vegetation Index (NDVI)
Quantifies vegetative canopy density and chlorophyll absorption:
$$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}} = \frac{B08 - B04}{B08 + B04}$$
* **Range:** $-1.0$ to $+1.0$.
* **Interpretation:** $< 0.1$ (Bare soil / rock / water), $0.2 - 0.4$ (Sparse vegetation / emergence), $0.6 - 0.9$ (Dense, healthy green canopy).

### 3.2 Normalized Difference Water Index (NDWI)
Sensitive to canopy liquid water content and irrigation status:
$$\text{NDWI} = \frac{\text{NIR} - \text{SWIR}}{\text{NIR} + \text{SWIR}} = \frac{B08 - B11}{B08 + B11}$$
* **Interpretation:** Negative values reflect canopy water deficit; positive values denote well-hydrated vegetation.

### 3.3 Enhanced Vegetation Index (EVI)
Corrects for atmospheric aerosols and canopy background signals in high-biomass crops (Sugarcane, Banana):
$$\text{EVI} = 2.5 \times \frac{\text{NIR} - \text{Red}}{\text{NIR} + 6 \times \text{Red} - 7.5 \times \text{Blue} + 1} = 2.5 \times \frac{B08 - B04}{B08 + 6 \times B04 - 7.5 \times B02 + 1}$$

### 3.4 Soil-Adjusted Vegetation Index (SAVI)
Minimizes soil brightness influences in early vegetative stages with partial ground cover:
$$\text{SAVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red} + L} \times (1 + L)$$
* Where $L = 0.5$ for intermediate canopy density.

---

## 4. Standard Satellite Data Model (`SatelliteObservation`)

Defined in `backend/app/models/intelligence_schemas.py`:

```python
class SatelliteObservation(BaseModel):
    farm_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    satellite: str = "Sentinel-2"
    sensor: str = "MSI"
    band: Optional[str] = None
    index: SpectralIndex  # NDVI | NDWI | EVI | SAVI
    value: Optional[float] = None
    resolution_meters: float = 10.0
    cloud_cover_percentage: Optional[float] = None
    source: str = "Copernicus Open Access Hub (Planned)"
    status: str = "UNAVAILABLE"
    data_confidence: ConfidenceMetadata
```

---

## 5. Cloud Masking & Quality Control Protocol

In India, cloud cover during the Kharif monsoon (June to September) obscures optical satellite observations. The pipeline will apply strict Quality Assurance:

1. **Scene Classification Layer (SCL):** Pixel-level mask provided with Sentinel-2 Level-2A data:
   - SCL 3: Cloud shadows $\rightarrow$ Masked
   - SCL 8, 9, 10: Clouds medium/high probability and Cirrus $\rightarrow$ Masked
2. **Parcel Cloud Threshold:** If $> 20\%$ of parcel pixels are masked, the scene is rejected and the system reports `UNAVAILABLE (Cloud Obscured)`.
3. **Synthetic Aperture Radar (SAR) Fallback (Future):** Sentinel-1 C-band SAR backscatter ($\text{VV}, \text{VH}$) operates through cloud cover and will be deployed in later phases for cloud-free soil moisture and structure monitoring.

---

## 6. Implementation Phasing Roadmap

| Phase | Milestone | Deliverables | Target Timeline |
| :--- | :--- | :--- | :--- |
| **Phase 2.5 (Current)** | Foundation & Schemas | `SatelliteObservation` schema, GeoJSON polygon boundary support, honest `UNAVAILABLE` handling | **Completed** |
| **Phase 3.0** | Real Data Ingest | STAC API integration with Copernicus Data Space Ecosystem, automated tile clipping for farm boundaries | Next Phase |
| **Phase 3.5** | Time-Series Indexing | Automated 5-day NDVI/NDWI calculation and database persistence in `FarmObservationRecord` | Future Phase |
| **Phase 4.0** | Anomaly Alerts | Automated crop water stress warning when NDWI drops $> 2\sigma$ below seasonal baseline | Future Phase |
