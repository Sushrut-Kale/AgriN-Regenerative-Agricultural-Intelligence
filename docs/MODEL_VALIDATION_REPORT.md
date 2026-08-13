# FarmFriend AI — ML Model Validation Report

**Date:** 2026-08-13  
**Model Version:** `logistic_regression_v1`  
**Dataset:** `crop_recommendation_synthetic.csv` (2,420 rows, 22 classes)  
**Evaluation Strategy:** 80/20 Stratified Train/Test Split (Seed: 42) + 5-Fold Cross Validation  

---

## 1. Model Selection & Comparison Summary

Four candidate algorithms were trained and evaluated on the dataset:

| Model | Test Accuracy | Weighted Precision | Weighted Recall | Weighted F1-Score | 5-Fold CV Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | **92.56%** | **92.70%** | **92.56%** | **92.43%** | **91.27% ± 1.99%** |
| **Random Forest** | 92.36% | 92.39% | 92.36% | 92.20% | 91.74% ± 1.85% |
| **Gradient Boosting** | 91.53% | 91.91% | 91.53% | 91.45% | 89.82% ± 2.10% |
| **Decision Tree** | 88.84% | 89.13% | 88.84% | 88.81% | 85.43% ± 2.45% |

**Selected Champion Model:** `Logistic Regression` (Highest F1-score: 0.9243, smooth probabilistic calibration for 22 multi-class crop probability outputs).

---

## 2. Feature Importance (Random Forest Gini Impurity)

| Rank | Feature | Gini Importance | Cumulative |
| :--- | :--- | :--- | :--- |
| 1 | `rainfall` | 0.2092 | 20.92% |
| 2 | `P` (Phosphorus) | 0.2046 | 41.38% |
| 3 | `humidity` | 0.1894 | 60.32% |
| 4 | `N` (Nitrogen) | 0.1301 | 73.33% |
| 5 | `K` (Potassium) | 0.1211 | 85.44% |
| 6 | `temperature` | 0.0881 | 94.25% |
| 7 | `ph` | 0.0575 | 100.00% |

---

## 3. Data Leakage & Reproducibility Verification

- **Train/Test Separation:** `train_test_split` executed with `stratify=y` prior to any transformation.
- **Scaler Fitting:** `StandardScaler` fitted **exclusively on training set (`X_train`)** and applied to test set (`X_test`) via `.transform()`.
- **Target Variable:** Excluded from features.
- **Reproducibility Test:** Independent re-execution in `test_qa_master.py` reproduced exact reported metrics (`Accuracy = 92.56%`, `F1 = 92.43%`).

---

## 4. Hybrid Scoring Architecture (ML + ICAR Rule Engine)

Final crop suitability score $S_{\text{final}}$ is computed via a 60/40 weighted blend:

$$S_{\text{final}} = \left( 0.60 \times P_{\text{ML}} + 0.40 \times S_{\text{Rule}} \right) \times \text{Penalty}_{\text{Missing}}$$

Where:
- $P_{\text{ML}}$: Model probability scaled to 0–100.
- $S_{\text{Rule}}$: Weighted agricultural rule evaluation across pH (20%), NPK (25%), Micronutrients (10%), Temperature (15%), Rainfall (15%), and Regional Context (15%).
- $\text{Penalty}_{\text{Missing}}$: Linear penalty based on missing SHC inputs.
