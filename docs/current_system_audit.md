# FarmFriend AI — Current System Audit

**Audit Date**: 2026-08-13  
**Auditor**: Senior ML Engineer / Agricultural Data Scientist / QA Lead  
**Scope**: Full repository inspection of ML model, API backend, rule engine, knowledge bases, frontend logic, and data flow.

---

## 1. Executive Summary

An exhaustive audit of the existing FarmFriend AI codebase revealed that while a multi-tier service architecture exists (FastAPI + scikit-learn + rule engine), **the underlying ML model and knowledge parameters contain serious flaws, synthetic data dependencies, unit mismatches, and hardcoded/static fallbacks**.

Key findings:
1. **Synthetic Data Dependency**: The ML model (`crop_model_v1.joblib`) was trained on `data/raw/crop_recommendation_synthetic.csv` (a 2,200-row synthetic dataset).
2. **Model Metrics Leakage & Static Display**:
   - In `models/model_metadata.json`, Logistic Regression displays **92.6% Accuracy** and **0.924 F1-Score**.
   - These exact metrics are displayed on the frontend (`Home.jsx` / `Dashboard.jsx`). While dynamically loaded from `model_info`, they represent performance on synthetic, non-realistic data.
3. **Severe Knowledge Mismatch & Bug in Rainfall Thresholds**:
   - `knowledge/crop_requirements.json` defines Cotton rainfall optimal range as `60mm – 110mm` (likely copied from monthly cm/inches), while actual Kharif Cotton requires `600mm – 1000mm` seasonal rainfall.
   - For Rice, optimal rainfall is defined as `150mm – 300mm` (far below actual seasonal paddy requirements of `1000mm – 1500mm+`).
   - Consequently, for a input of **700mm rainfall in Parbhani (Kharif)**:
     - Cotton is heavily penalized (`score = 0.4`), flagging "700mm exceeds optimal range (60-110mm)".
     - Rice receives high suitability (`91.8/100`), even though 700mm rainfed is inadequate for un-irrigated paddy without flooded conditions.
4. **Soil Health Card Critical Levels Audit**:
   - `shc_thresholds.json` lists generic critical levels: Zinc (`Zn = 0.6 ppm`) and Boron (`B = 0.5 ppm`).
   - In the test case (Zn: 0.55 ppm, B: 0.48 ppm), these generic thresholds flag Zn and B as "deficient" regardless of crop-specific requirements or soil type (Vertisols/Black soils in Parbhani have distinct micronutrient availability dynamics).
5. **Disconnected/Simplistic Features**:
   - The ML model only receives 7 features (`N, P, K, temperature, humidity, ph, rainfall`).
   - 5 crucial SHC parameters (`S, Zn, Fe, Cu, Mn, B`), soil type, location (district/agro-climatic zone), irrigation status, and drainage are completely ignored by the ML model and evaluated only post-hoc in a heuristic rule layer (`suitability_scorer.py`).
6. **What-If Engine Contamination**:
   - What-If simulation re-calculates suitability using `predict_single_crop`, but relies on fallback medians whenever inputs are omitted, and shares the same flawed rainfall/micronutrient thresholds.

---

## 2. Component-by-Component Value Source Matrix

| Displayed Value / Component | Current Source | Classification | Action Required |
|---|---|---|---|
| ML Model Choice (`Logistic Regression`) | `models/model_metadata.json` | REAL MODEL (Synthetic Data) | Re-train model on real, verified open data (ICRISAT / data.gov.in / SHC). |
| Accuracy (`92.6%`) | `models/model_metadata.json` | REAL MODEL (Synthetic Data) | Compute macro-F1, weighted F1, and accuracy on real holdout test sets. |
| F1-Score (`0.924`) | `models/model_metadata.json` | REAL MODEL (Synthetic Data) | Compute macro-F1 & per-crop recall on real data. |
| Rice Top Score (`91.8/100`) | `suitability_scorer.py` (0.6 ML + 0.4 Rule) | RULE + SYNTHETIC ML | Rebuild score combining real ML, verified crop requirements & regional context. |
| Cotton Score (`31.7/100` or low) | `suitability_scorer.py` (Rainfall penalty bug) | FLAWED RULE | Fix unit errors in crop rainfall thresholds; ground in agronomic literature. |
| Zn Critical (`0.6 ppm`) | `shc_thresholds.json` | GENERIC RULE | Provide crop-specific and soil-specific DTPA extraction thresholds. |
| B Critical (`0.5 ppm`) | `shc_thresholds.json` | GENERIC RULE | Validate against ICAR/Govt Soil Health Card standards. |
| Rainfall Warning ("Exceeds optimal") | `suitability_scorer.py` (`_check_rainfall`) | HARDCODED WRONG RANGE | Replace single global/flawed range with crop & region-specific seasonal rainfall requirements. |
| AI Explanation Text | `nlg_explainer.py` | RULE-BASED TEMPLATE | Maintain grounded NLG; integrate structured LLM grounding when requested. |
| Supported Crops List (22 crops) | `crop_requirements.json` | KNOWLEDGE BASE | Audit representation in real datasets; mark low-confidence crops. |

---

## 3. Detailed Hardcoded / Flawed Logic Trace

### 3.1 Hardcoded Medians in Inference (`ml/predict.py`)
```python
MEDIANS = {
    "N": 55.0, "P": 48.0, "K": 45.0,
    "temperature": 25.0, "humidity": 72.0,
    "ph": 6.5, "rainfall": 103.0
}
```
*Issue*: Omitting inputs causes hidden fallback to fixed national medians instead of penalizing confidence or asking for user input.

### 3.2 Incorrect Rainfall Penalty Formula (`backend/app/services/suitability_scorer.py`)
```python
def _check_rainfall(crop_req: dict, rainfall_val: Optional[float]):
    ...
    # For Cotton: opt_min=60, opt_max=110
    # For rainfall_val = 700mm:
    excess = (rainfall_val - opt_max) / opt_max  # (700 - 110)/110 = 5.36
    score = max(0.4, 1.0 - excess * 0.5)         # max(0.4, -1.68) = 0.4
```
*Issue*: Arbitrary scale math penalizes Kharif cotton for normal 700mm seasonal rainfall.

### 3.3 Rule Component Weighting
```python
ML_WEIGHT = 0.60
RULE_WEIGHT = 0.40
```
*Issue*: Weights are hardcoded without clear justification or sensitivity configuration.

---

## 4. Remediation Strategy & Next Steps

1. **Data Pipeline**: Ingest open datasets from Government of India (data.gov.in / Soil Health Card), ICRISAT District Level Database, and FAOSTAT.
2. **Knowledge Base Audit**: Correct all rainfall and nutrient ranges in `crop_requirements.json` with documented scientific citations.
3. **ML Training Pipeline**: Build `ml/build_training_dataset.py` and `ml/train.py` using real data, strict train/validation/test splits, and multi-model benchmarking.
4. **Scoring Architecture**: Implement explicit units (`knowledge/units.yaml`), calibrated score combination, and transparent factor attribution.
5. **Feedback System**: Create DB schemas and backend routes for user/farmer outcome feedback without auto-retraining.
