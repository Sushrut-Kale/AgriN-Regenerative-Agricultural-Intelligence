# 🧪 Soil Intelligence Module Specification

> **Module:** `backend/app/services/soil_intelligence.py`  
> **Reference Standards:** `knowledge/soil_health_standards.json` (ICAR & DAC&FW, GoI)  
> **Status:** `IMPLEMENTED` & Fully Verified  

---

## 1. Overview & Purpose

Soil data in AgriN is elevated from a simple numerical input for crop prediction to a first-class **Soil Health Intelligence Profile**. The module classifies soil across macro, secondary, and micro nutrients, detects chemical and physical constraints, and prescribes targeted agronomic amendments.

---

## 2. Soil Health Profile Hierarchy

```
Soil Health Profile
├── Nutrient Status
│   ├── Macro Nutrients (N, P, K) [kg/ha]
│   ├── Secondary Nutrients (S) [ppm]
│   └── Micro Nutrients (Zn, Fe, Cu, Mn, B) [ppm]
│
├── Chemical Properties
│   ├── Reaction (pH) [classification: Highly Acidic, Acidic, Moderately Acidic, Neutral, Moderately Alkaline, Highly Alkaline]
│   └── Salinity (EC) [dS/m: Non-saline, Slightly Saline, Saline, Highly Saline]
│
├── Organic Matter
│   └── Soil Organic Carbon (OC) [%: Critical, Low, Moderate, Healthy, High]
│
├── Detected Soil Constraints
│   ├── Soil Acidity Hazard (pH < 5.5) -> Agricultural lime
│   ├── Soil Salinity Hazard (EC > 2.0 dS/m) -> Leaching & gypsum
│   ├── Soil Alkalinity / Sodicity Hazard (pH > 8.5) -> Gypsum & organic amendments
│   ├── Severe SOC Depletion (OC < 0.5%) -> FYM & residue retention
│   └── Micronutrient Deficiencies (Zn < 0.6 ppm, B < 0.5 ppm)
│
└── Actionable Outputs
    ├── Status: OPTIMAL | GOOD | MODERATE | DEGRADED | CRITICAL | INSUFFICIENT_DATA
    ├── Numerical Score: [0.0 - 100.0]
    ├── Limiting Factors & Positive Indicators
    ├── Recommended Improvement Areas
    └── Mathematical Confidence Score
```

---

## 3. Centralized Standard Thresholds

AgriN avoids hardcoded magic numbers by centralizing DAC&FW standard rating limits in `knowledge/soil_health_standards.json`:

| Parameter | Unit | Low / Deficient | Medium / Critical | High / Optimal |
| :--- | :---: | :---: | :---: | :---: |
| **Nitrogen (N)** | kg/ha | $< 280$ | $280 - 560$ | $> 560$ |
| **Phosphorus (P)** | kg/ha | $< 10$ | $10 - 25$ | $> 25$ |
| **Potassium (K)** | kg/ha | $< 108$ | $108 - 280$ | $> 280$ |
| **Organic Carbon (OC)**| % | $< 0.50$ | $0.50 - 0.75$ | $> 0.75$ |
| **Sulfur (S)** | ppm | $< 10.0$ | $10.0 - 20.0$ | $> 20.0$ |
| **Zinc (Zn)** | ppm | $< 0.60$ | $0.60 - 1.20$ | $> 1.20$ |
| **Iron (Fe)** | ppm | $< 4.50$ | $4.50 - 9.00$ | $> 9.00$ |
| **Boron (B)** | ppm | $< 0.50$ | $0.50 - 1.00$ | $> 1.00$ |

---

## 4. Verification Evidence

Automated tests:
- `tests/test_track4_evolution.py::test_soil_intelligence_optimal_profile`: Confirms optimal score $\ge 80.0$ and positive indicator generation.
- `tests/test_track4_evolution.py::test_soil_intelligence_constraints_detection`: Confirms acidity (SC-002), carbon depletion (SC-001), and zinc deficiency (SC-005) triggers.
- `tests/test_track4_evolution.py::test_soil_intelligence_missing_and_boundary_handling`: Verifies exact boundary values and empty input graceful degradation.
