# FarmFriend AI — Agricultural Knowledge Sources & Provenance

**Document Version**: 2.0  
**Last Updated**: 2026-08-13  
**Scope**: Verified scientific sources for crop requirements, soil health thresholds, agro-climatic classifications, and regional crop applicability.

---

## 1. Verified Core Data & Knowledge Sources

### Primary Government & Research Sources (India & Global)

1. **Government of India — Open Government Data (OGD) Portal**
   - **URL**: `https://www.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0`
   - **Scope**: District-wise, season-wise crop area, production, and yield statistics across Indian states (1997–2020+).
   - **License**: Open Government Data License (OGDL) India.

2. **ICRISAT — District Level Database (VDSA / DLD)**
   - **URL**: `https://data.icrisat.org/district-level-data/`
   - **Scope**: Meso-level agricultural, weather, and soil data for 19 states and ~311 districts in India (1966–2017+).
   - **License**: CC-BY 4.0 / ICRISAT Open Access.

3. **Government of India — Soil Health Card Scheme**
   - **URL**: `https://soilhealth.dac.gov.in/`
   - **Scope**: National standard testing protocols and rating grids for 12 soil parameters (N, P, K, S, Zn, Fe, Cu, Mn, B, pH, EC, OC).
   - **Reference**: Department of Agriculture & Farmers Welfare, Ministry of Agriculture, Govt. of India.

4. **ICAR — Indian Council of Agricultural Research Guidelines**
   - **Institutes**:
     - ICAR-NBSS&LUP (National Bureau of Soil Survey & Land Use Planning), Nagpur (Soil series & agro-climatic zones of Maharashtra).
     - ICAR-CICR (Central Institute for Cotton Research), Nagpur (Cotton agronomy & soil requirements).
     - ICAR-IIPR (Indian Institute of Pulses Research), Kanpur (Chickpea, Pigeonpea, Mungbean, Urad requirements).
     - VNMKV (Vasantrao Naik Marathwada Krishi Vidyapeeth), Parbhani (Marathwada agro-climatic recommendations).

5. **FAOSTAT & FAO Crop Ecology Database**
   - **URL**: `https://www.fao.org/land-water/databases-and-software/crop-information/en/`
   - **Scope**: Ecocrop database for optimal & critical pH, temperature, and rainfall ranges.

---

## 2. Parameter Provenance & Critical Limits

### 2.1 Soil Nutrient Rating Scale (Govt. of India Soil Health Card)

| Parameter | Unit | Low Range | Medium Range | High Range | Critical Limit | Method Source |
|---|---|---|---|---|---|---|
| **N** | kg/ha | < 280 | 280 – 560 | > 560 | — | Alkaline KMnO4 Method |
| **P** | kg/ha | < 11 | 11 – 25 | > 25 | — | Olsen's P (pH > 6.5) / Bray's P |
| **K** | kg/ha | < 118 | 118 – 280 | > 280 | — | Neutral N Ammonium Acetate |
| **S** | ppm | < 10 | 10 – 20 | > 20 | 10.0 ppm | 0.15% CaCl2 Extractable |
| **Zn** | ppm | < 0.6 | 0.6 – 1.2 | > 1.2 | 0.60 ppm | DTPA Extractable |
| **Fe** | ppm | < 4.5 | 4.5 – 9.0 | > 9.0 | 4.50 ppm | DTPA Extractable |
| **Cu** | ppm | < 0.2 | 0.2 – 0.4 | > 0.4 | 0.20 ppm | DTPA Extractable |
| **Mn** | ppm | < 2.0 | 2.0 – 4.0 | > 4.0 | 2.00 ppm | DTPA Extractable |
| **B** | ppm | < 0.5 | 0.5 – 1.0 | > 1.0 | 0.50 ppm | Hot Water Extractable |
| **OC** | % | < 0.5 | 0.5 – 0.75 | > 0.75 | — | Walkley & Black Method |
| **EC** | dS/m | < 1.0 (Normal) | 1.0 – 2.0 | > 2.0 (Saline) | 2.0 dS/m | 1:2.5 Soil-Water Suspension |
| **pH** | scale | < 6.5 (Acidic) | 6.5 – 8.2 (Normal) | > 8.2 (Alkaline)| — | 1:2.5 Soil-Water Suspension |

---

## 3. Crop Requirement Threshold Correction Matrix

The following table summarizes the audit and corrections applied to crop requirement thresholds to resolve unit and range mismatches:

| Crop | Parameter | Old Range (Flawed) | Corrected Range | Scientific Source |
|---|---|---|---|---|
| **Cotton** | Seasonal Rainfall | 60 – 110 mm | 600 – 1100 mm | ICAR-CICR Nagpur / VNMKV Parbhani |
| **Cotton** | Soil Type | Generic | Deep Black (Vertisol), Clay Loam | ICAR-NBSS&LUP Soil Bulletin |
| **Rice** | Seasonal Rainfall | 150 – 300 mm | 1000 – 1600 mm | ICAR Rice Knowledge Management Portal |
| **Rice** | Soil Type | Generic | Clay, Heavy Loam (water-retaining) | TNAU Agronomy Guide |
| **Soybean** | Seasonal Rainfall | 100 – 200 mm | 600 – 900 mm | ICAR-IISR Indore |
| **Chickpea**| Seasonal Rainfall | 40 – 90 mm | 350 – 600 mm | ICAR-IIPR Kanpur |
| **Pigeonpea**| Seasonal Rainfall | 80 – 150 mm | 600 – 1000 mm | ICAR-IIPR Kanpur |

---

## 4. Policy on Missing Scientific Thresholds
If a crop parameter threshold cannot be verified against official agricultural literature:
- The parameter is recorded as `null` / `UNKNOWN`.
- The rule engine emits a `missing` factor status with `0` score impact, reducing data confidence rather than penalizing the crop arbitrarily.
- **NEVER invent or fabricate arbitrary numerical thresholds.**
