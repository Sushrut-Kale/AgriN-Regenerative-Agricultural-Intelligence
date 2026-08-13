# FarmFriend AI — Model Validation & Sensitivity Report

**Document Version**: 2.0  
**Updated**: 2026-08-13  
**Status**: Verification Complete  

---

## 1. Validation Test Suites & Results

### 1.1 Test Case 01: Parbhani Kharif Rainfed Black Soil
- **Location**: Parbhani, Maharashtra | **Season**: Kharif | **Soil**: Black Vertisol
- **Rainfall**: 700 mm | **Temp**: 28°C | **Humidity**: 65%
- **Soil Test**: N=280, P=18, K=310, S=14, Zn=0.55, Fe=5.2, Cu=0.45, Mn=4.8, B=0.48, pH=6.8
- **Expected Scientific Outcome**:
  - Cotton, Soybean, Pigeonpea rank highly as suitable crops.
  - Rice ranks lower for rainfed conditions due to high water/flooding requirement.
  - Corrected rainfall threshold (600–1100 mm for Cotton) prevents spurious excess penalties.

### 1.2 Test Case 02: Parbhani Kharif Irrigated vs Rainfed
- **Perturbation**: Toggle `irrigation_available` from `False` to `True`.
- **Expected Outcome**: Suitability for high-water crops (Rice, Sugarcane) increases dynamically, with clear factor attribution.

### 1.3 Test Case 03: pH Sensitivity Sweep (Acidic to Alkaline)
- **Perturbation**: Sweep pH from 4.5 -> 6.5 -> 8.5 on Cotton and Pulses.
- **Expected Outcome**: Score reflects documented crop tolerance limits (Cotton tolerates pH 8.5; Acidic crops suffer at pH 8.5).

### 1.4 Test Case 04: What-If Parameter Isolation
- **Perturbation**: Modify ONLY `K` (Potassium) from 150 kg/ha -> 310 kg/ha while keeping all other inputs identical.
- **Expected Outcome**: Score change direction matches crop K requirement. Original baseline score restores completely when K is reset.

---

## 2. Invariance & Generalization Integrity Checks
- **Geographic Generalization**: Evaluated on holdout districts (Parbhani, Yavatmal, Nashik) to verify that model predictions do not collapse to fixed national defaults.
- **No Hardcoded Winner**: Scores emerge strictly from model inference + validated knowledge rules.
