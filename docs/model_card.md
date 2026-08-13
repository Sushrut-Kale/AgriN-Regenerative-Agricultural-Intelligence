# FarmFriend AI — Model Card

**Model Title**: Multi-Crop Suitability Prediction Model  
**Model Version**: v2.0  
**Artifact Names**: `models/crop_model_v1.joblib`, `models/scaler_v1.joblib`, `models/label_encoder_v1.joblib`  
**Developer**: FarmFriend AI Engineering Team  
**Model Type**: Ensembled Machine Learning Classifier (Random Forest / HistGradientBoosting)  

---

## 1. Model Details & Intended Use

- **Intended Use**: Decision-support tool for recommending agricultural crops based on 12 Soil Health Card parameters, seasonal weather observations, and farm context.
- **Out of Scope / Not Intended For**:
  - Financial yield guarantees or market price prediction.
  - Replacement of official agricultural extension officer / KVK advisory.
  - Misapplication to regions outside documented training geographic bounds without recalibration.

---

## 2. Training Data & Preprocessing

- **Dataset**: `data/processed/unified_crop_soil_dataset.csv`
- **Train / Validation / Test Split Strategy**:
  - **Stratified Random Split**: 80% Train, 20% Test (Random Seed = 42).
  - **Geographic Holdout Split**: Holdout evaluation on unseen districts (e.g. Parbhani / Nanded) to test spatial generalization.
- **Features Used in Inference**: `[N, P, K, S, Zn, Fe, Cu, Mn, B, ph, EC, OC, temperature, humidity, rainfall]`
- **Scaling**: `StandardScaler` fitted ONLY on training data partition.

---

## 3. Evaluated Metrics & Performance Benchmarks

| Model Architecture | Accuracy | Macro F1-Score | Weighted F1-Score | Per-Class Minimum Recall | CV Mean Accuracy |
|---|---|---|---|---|---|
| **Logistic Regression** | Evaluated | Evaluated | Evaluated | Evaluated | Evaluated |
| **Decision Tree** | Evaluated | Evaluated | Evaluated | Evaluated | Evaluated |
| **Random Forest** | Evaluated | Evaluated | Evaluated | Evaluated | Evaluated |
| **HistGradientBoosting** | Evaluated | Evaluated | Evaluated | Evaluated | Evaluated |

*Note: All metrics reported on the production dashboard reflect true holdout test data performance.*

---

## 4. Model Limitations & Ethical Considerations

1. **Microclimate Variations**: Farm-level microclimates (e.g., hill slopes vs valley bottoms) may differ from district-level weather averages.
2. **Irrigation Context**: Crop suitability for high-water crops (like paddy) depends heavily on irrigation infrastructure, not rainfall alone.
3. **Calibrated Probabilities**: Model output probabilities are combined with agricultural rule constraints (`suitability_scorer.py`) rather than interpreted as raw certainty.
