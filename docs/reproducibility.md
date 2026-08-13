# FarmFriend AI — Reproducibility & Pipeline Execution Guide

**Document Version**: 2.0  
**Updated**: 2026-08-13  

---

## 1. Environment & Dependencies

- **Python Version**: Python 3.10+
- **Key Package Dependencies**:
  - `pandas`, `numpy`, `scikit-learn`, `joblib`
  - `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`
  - `pytest`, `httpx`

---

## 2. Reproducible Execution Commands

To reproduce the entire dataset building, ML model training, evaluation, and backend verification:

```powershell
# 1. Clean & Build Processed Dataset from Verified Open Data Sources
python data/scripts/build_training_dataset.py

# 2. Run Model Training & Evaluation Pipeline
python ml/train.py

# 3. Execute Automated Pytest Suite
pytest tests/ -v
```

---

## 3. Random Seeds & Determinism

- **Global Random Seed**: `SEED = 42`
- Set in: `ml/train.py`, `data/scripts/build_training_dataset.py`, scikit-learn models (`RandomForestClassifier`, `LogisticRegression`, `train_test_split`).
- Running the training pipeline twice on the same environment yields identical model weights, hashes, and evaluation metrics.
