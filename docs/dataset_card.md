# FarmFriend AI — Dataset Card

**Dataset Title**: FarmFriend Multi-Source Unified Agricultural Dataset  
**Version**: v2.0  
**Release Date**: 2026-08-13  
**Primary Region**: India (Special focus on Maharashtra: Marathwada, Vidarbha, Western Maharashtra, Konkan)  

---

## 1. Dataset Overview & Provenance

This dataset unites real open-access agricultural observations from official Indian sources:
1. **Soil Health Card Scheme Database (Govt. of India)**: Soil nutrient observations across Maharashtra districts.
2. **ICRISAT District Level Database**: Historical district-level crop outcomes, rainfall, and weather parameters (1966–2017+).
3. **Ministry of Agriculture & Farmers Welfare (OGD Portal)**: District-wise crop production statistics (1997–2021).
4. **IMD Climate Observations**: Gridded monthly and seasonal precipitation and temperature data.

---

## 2. Feature Schema & Canonical Units

| Feature Name | Field Description | Unit | Standard Range | Data Source |
|---|---|---|---|---|
| `state` | State name | Categorical | Maharashtra, etc. | GoI District Stats |
| `district` | District name | Categorical | Parbhani, Yavatmal, etc. | GoI District Stats |
| `agro_climatic_zone` | Agro-climatic zone | Categorical | Marathwada, Vidarbha, etc. | ICAR-NBSS&LUP |
| `season` | Cropping season | Categorical | Kharif, Rabi, Summer | GoI District Stats |
| `soil_type` | Dominant soil series | Categorical | Black soil (Vertisol), Clay Loam, etc.| Soil Health Card |
| `N` | Available Nitrogen | kg/ha | 0 – 800 | Soil Health Card |
| `P` | Available Phosphorus | kg/ha | 0 – 300 | Soil Health Card |
| `K` | Available Potassium | kg/ha | 0 – 800 | Soil Health Card |
| `S` | Available Sulphur | ppm | 0 – 100 | Soil Health Card |
| `Zn` | Available Zinc | ppm | 0.0 – 20.0 | Soil Health Card |
| `Fe` | Available Iron | ppm | 0.0 – 100.0 | Soil Health Card |
| `Cu` | Available Copper | ppm | 0.0 – 20.0 | Soil Health Card |
| `Mn` | Available Manganese | ppm | 0.0 – 50.0 | Soil Health Card |
| `B` | Available Boron | ppm | 0.0 – 10.0 | Soil Health Card |
| `ph` | Soil pH | pH scale | 4.0 – 9.5 | Soil Health Card |
| `EC` | Electrical Conductivity | dS/m | 0.0 – 15.0 | Soil Health Card |
| `OC` | Organic Carbon | % | 0.0 – 3.0 | Soil Health Card |
| `temperature` | Seasonal Mean Temp | °C | 10.0 – 45.0 | IMD Climate Data |
| `humidity` | Relative Humidity | % | 20.0 – 95.0 | IMD Climate Data |
| `rainfall` | Total Seasonal Rainfall | mm | 100.0 – 3500.0 | IMD Climate Data |
| `label` / `crop` | Target Crop Class | Categorical | Rice, Cotton, Soybean, Chickpea, etc.| GoI District Stats / ICRISAT |

---

## 3. Data Ingestion & Integrity Rules
- **No Synthetic Oversampling**: No synthetic data generation algorithms (SMOTE, CTGAN) are presented as real observations.
- **Unit Conversions**: All soil values strictly adhere to `knowledge/units.yaml`.
- **Handling Missing Features**: Missing micronutrient values are retained as explicit missing markers to evaluate dataset completeness.
