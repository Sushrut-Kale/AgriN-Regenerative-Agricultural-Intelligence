# FarmFriend AI — Screenshot Result Audit

**Audit Date**: 2026-08-13  
**Target Case**: Parbhani, Maharashtra (Kharif Season)  
**Input Test Vector**:
- **Location**: Parbhani, Maharashtra
- **Season**: Kharif
- **Soil Type**: Black soil (Vertisol)
- **Irrigation**: Limited / Rainfed
- **Rainfall**: 700 mm | **Temperature**: 28 °C | **Humidity**: 65%
- **Soil Test**: N=280 kg/ha, P=18 kg/ha, K=310 kg/ha, S=14 ppm, Zn=0.55 ppm, Fe=5.2 ppm, Cu=0.45 ppm, Mn=4.8 ppm, B=0.48 ppm, pH=6.8, EC=0.42 dS/m, OC=0.62%

---

## 1. Tracing Displayed Screenshot Values

| Displayed Metric | Value | Code Source / Formula | Audit Assessment |
|---|---|---|---|
| **Model Name** | `Logistic Regression` | `models/model_metadata.json` -> `"model_type"` | **Misleading**: Trained on synthetic data (`crop_recommendation_synthetic.csv`), not real field observations. |
| **Model Accuracy** | `92.6%` | `models/model_metadata.json` -> `metrics.accuracy = 0.9256` | **Synthetic Metric**: Accuracy calculated on 20% test split of synthetic dataset. |
| **Model F1-Score** | `0.924` | `models/model_metadata.json` -> `metrics.f1_weighted = 0.9242` | **Synthetic Metric**: Weighted F1 score on synthetic data. |
| **Rice Suitability Score** | `91.8 / 100` | `suitability_scorer.py`: `ML(0.6) * prob + Rule(0.4) * rule_score` | **Incorrect Agronomic Finding**: Rice requires 1000–1500+ mm water or standing water irrigation. In rainfed 700mm Parbhani Kharif, rice is not top suitable without heavy irrigation. |
| **Cotton Suitability Score** | `31.7 / 100` | `suitability_scorer.py`: Rainfall penalty severely penalizes Cotton | **Bug / Incorrect Knowledge Threshold**: `crop_requirements.json` incorrectly set Cotton optimal rainfall to 60–110 mm. 700mm seasonal rain was flagged as "exceeding optimal range", driving rule score down to ~30%. In reality, Parbhani is a major cotton-growing district in Marathwada! |
| **Zn Critical Level** | `0.55 ppm (critical: 0.6)` | `shc_thresholds.json`: `Zn critical_level = 0.6` | **Uncalibrated Global Threshold**: DTPA-extractable Zn critical limit in Indian soils ranges 0.5 – 0.7 ppm depending on soil pH and organic matter. Flagged as deficient without crop context. |
| **B Critical Level** | `0.48 ppm (critical: 0.5)` | `shc_thresholds.json`: `B critical_level = 0.5` | **Uncalibrated Global Threshold**: Hot water extractable Boron critical limit is ~0.5 ppm. Marginal deficit, but should be crop-specific (pulses/cotton are more B-sensitive than cereals). |

---

## 2. Root Cause Analysis of the Parbhani Kharif Contradiction

### Why did Rice rank #1 (91.8/100)?
1. **Synthetic ML Probability**: In `crop_recommendation_synthetic.csv`, synthetic rice rows had high probability for `N=280`, `temp=28`, `humidity=65`, `rainfall=700`.
2. **Flawed Rice Rainfall Range**: In `crop_requirements.json`, Rice optimal rainfall was defined as `150–300 mm`. `700 mm` was capped or handled via mild penalty, yielding a high rule score.

### Why did Cotton rank low (31.7/100)?
1. **Unit Error in Knowledge Base**: Cotton rainfall optimal range was set to `60–110 mm` (which is a monthly figure, not seasonal).
2. **Rule Penalty**: 700 mm rainfall produced an excess factor of `(700 - 110)/110 = 5.36`, reducing the rainfall rule score to `0.4` (lowest clamp).
3. **Micronutrient Penalties**: Zn (0.55 < 0.6) and B (0.48 < 0.5) were flagged as limiting factors, further depressing Cotton's rule score.

---

## 3. Agronomic Reality Check for Parbhani, Maharashtra
- **Parbhani Agro-Climatic Zone**: Central Vidarbha / Marathwada Zone (Dry/Semi-arid zone with medium-to-deep Black Vertisols).
- **Major Kharif Crops in Parbhani**: Cotton (Kapas), Soybean, Pigeonpea (Tur), Green Gram (Mung), Black Gram (Urad).
- **Rice in Parbhani**: Rice is NOT a major crop in rainfed Parbhani (Konkan and Bhandara/Gondia are the primary rice belts of Maharashtra).
- **Conclusion**: The current system output was **agronomically inverted** due to dataset synthetic bias and faulty rule thresholds.

---

## 4. Required Fixes
1. Correct all units and ranges in `knowledge/crop_requirements.json` based on ICAR-CICR and Maharashtra Agricultural University (VNMKV Parbhani) guidelines.
2. Ingest real district crop statistics and soil observations from Government open data.
3. Integrate location and soil type directly into regional suitability adjustments.
