# 🛰️ Satellite Integration Architecture Specification

> **Module:** `backend/app/services/satellite_service.py`  
> **Route:** `GET /api/satellite/status`  
> **Status:** `ARCHITECTURE READY` (Provider Abstraction Layer Built; Strict `NOT_CONNECTED` Status)  

---

## 1. Abstraction Pipeline

AgriN decouples external Earth Observation (EO) satellite constellations (e.g., ESA Sentinel-2, NASA Landsat-8/9, ISRO EOS-04) from downstream agricultural advisory logic using a clean provider abstraction:

```
               SATELLITE DATA PROVIDER (Interface)
                               ↓
         ┌─────────────────────┼─────────────────────┐
         ↓                     ↓                     ↓
   SENTINEL-2 HUB       LANDSAT-8 OLI          ISRO BHUVAN
 (10m Multi-spectral)  (30m Multi-spectral)   (SAR & Optical)
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ↓
                    VEGETATION OBSERVATION
           (Normalized Multi-Spectral Observation)
                               ↓
                      CROP HEALTH SIGNAL
          (NDVI, NDWI, EVI, SAVI & Anomaly Detectors)
```

---

## 2. Standard Observation Schema

The system standardizes satellite observations via `VegetationObservation`:

```python
class VegetationObservation:
    satellite_constellation: str       # e.g., "Sentinel-2 MSI"
    observation_timestamp: datetime
    coordinates_wgs84: Tuple[float, float]
    spatial_resolution_meters: float   # e.g., 10.0
    cloud_cover_percentage: float      # e.g., 4.2%
    spectral_indices: Dict[str, float] # { "ndvi": 0.68, "ndwi": -0.12, "evi": 0.44 }
    canopy_status: str                 # "VIGOROUS" | "MODERATE" | "STRESSED" | "SENESCENT"
    confidence: float
```

---

## 3. Strict Non-Fabrication Policy

When no live API keys for Copernicus Data Space or AWS Earth Search are configured:
- The system returns `satellite_status = "NOT_CONNECTED"`.
- It reports `spectral_observations = None`.
- No synthetic or mock NDVI values are injected into farmer recommendations.

```json
{
  "satellite_status": "NOT_CONNECTED",
  "active_provider": null,
  "registered_providers": ["Copernicus_Sentinel2_MSI", "Landsat8_OLI", "ISRO_Bhuvan_WMS"],
  "message": "No live Earth observation satellite data provider is currently authenticated in this deployment.",
  "data_available": false
}
```

---

## 4. Verification Evidence

Automated test: `tests/test_track4_evolution.py::test_satellite_status_honesty`
- Verified: `GET /api/satellite/status` returns `NOT_CONNECTED` with `data_available=False`.
