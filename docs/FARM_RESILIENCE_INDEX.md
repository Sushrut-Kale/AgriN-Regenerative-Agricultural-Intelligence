# 🛡️ Farm Resilience Index Specification — Prototype

> **Module:** `backend/app/services/farm_resilience.py`  
> **Route:** `POST /api/resilience/score`  
> **Classification:** `AgriN Farm Resilience Index — prototype`  
> **Status:** `IMPLEMENTED` & Fully Verified  

---

## 1. Prototype Framing & Scientific Honesty

The **AgriN Farm Resilience Index — prototype** is an auditable, multi-factorial decision-support index designed to evaluate how well a farm parcel can buffer environmental stress and maintain multi-year productivity.

> [!IMPORTANT]
> This index is explicitly presented as a **prototype model** awaiting multi-year empirical field validation across regional Agricultural Research Stations (ARS). It is never presented as an infallible universal constant.

---

## 2. Multi-Component Mathematical Breakdown

The index completely rejects opaque AI "black-box" scores. The composite score is computed from 5 transparent components:

$$\text{Resilience Score} = \sum (w_i \times C_i)$$

| Component ($C_i$) | Weight ($w_i$) | Evaluation Criteria |
| :--- | :---: | :--- |
| **Soil Health ($C_{\text{soil}}$)** | $0.30$ | Evaluates organic carbon, nutrient balance, pH buffer capacity, and absence of constraints. |
| **Water Context ($C_{\text{water}}$)** | $0.25$ | Evaluates irrigation infrastructure, seasonal precipitation volume, and in-situ drainage. |
| **Climate Context ($C_{\text{climate}}$)** | $0.20$ | Evaluates ambient temperature stability, heat stress risks, and extreme precipitation anomalies. |
| **Crop Diversity ($C_{\text{diversity}}$)** | $0.15$ | Evaluates rotation history, legume presence, and intercropping practices. |
| **Crop Suitability ($C_{\text{suitability}}$)** | $0.10$ | Evaluates the physiological match of current or intended crops to the local agro-ecological niche. |

---

## 3. Data Contract & Transparent Output

```json
{
  "prototype_index_name": "AgriN Farm Resilience Index — prototype",
  "version": "1.0.0-prototype",
  "score": 74.2,
  "confidence": 0.88,
  "resilience_tier": "HIGH_RESILIENCE",
  "components": {
    "soil_health": 82.0,
    "water_context": 75.0,
    "climate_context": 70.0,
    "crop_diversity": 65.0,
    "crop_suitability": 84.0
  },
  "sub_assessments": {
    "soil_assessment": "Soil exhibits favorable organic matter and balanced chemical reaction.",
    "water_assessment": "Secure irrigation access buffers against seasonal rainfall dry spells.",
    "climate_assessment": "Moderate temperature conditions within crop physiological limits.",
    "diversity_assessment": "Single monoculture detected; crop rotation with legumes recommended."
  },
  "improvement_priorities": [
    "Introduce legume intercropping to elevate the Crop Diversity component score above 75."
  ]
}
```

---

## 4. Verification Evidence

Automated test: `tests/test_track4_evolution.py::test_farm_resilience_index_breakdown`
- Verified: Composite score matches weighted sum of all 5 sub-components.
- Verified: Returns explicit sub-assessments and prototype branding.
