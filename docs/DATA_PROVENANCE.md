# 📜 Data Provenance & Confidence Architecture

> **Modules:** `backend/app/services/confidence_engine.py`, `backend/app/models/intelligence_schemas.py`  
> **Status:** `IMPLEMENTED` & Fully Verified  

---

## 1. Principles of Agricultural Data Provenance

In mission-critical agriculture, advice without provenance is unscientific. Every agronomic observation, calculation, and recommendation in AgriN carries an explicit data pedigree:

```json
{
  "source": "live_sensor_or_open_meteo",
  "observed_at": "2026-09-30T10:15:00Z",
  "location": "Pune, Maharashtra (18.5204°N, 73.8567°E)",
  "measurement": {
    "parameter": "temperature",
    "value": 28.4,
    "unit": "°C"
  },
  "confidence": 0.94,
  "method": "Direct satellite downscaling & REST API interpolation"
}
```

---

## 2. Dedicated Data Confidence Engine

The confidence engine computes an objective mathematical confidence metric $S_{\text{conf}} \in [0.0, 1.0]$ based on five weighted dimensions:

$$S_{\text{conf}} = w_{\text{comp}} S_{\text{comp}} + w_{\text{fresh}} S_{\text{fresh}} + w_{\text{geo}} S_{\text{geo}} + w_{\text{model}} S_{\text{model}} + w_{\text{rule}} S_{\text{rule}}$$

| Dimension | Weight | Criteria |
| :--- | :---: | :--- |
| **Data Completeness ($S_{\text{comp}}$)** | $0.30$ | Ratio of provided core agricultural parameters (N, P, K, pH, rainfall, etc.) to expected baseline. |
| **Data Freshness ($S_{\text{fresh}}$)** | $0.20$ | Temporal recency of observations ($<3$ days: 1.0; $<30$ days: 0.85; $>180$ days: 0.50). |
| **Geographic Precision ($S_{\text{geo}}$)** | $0.20$ | Geo-spatial resolution (`PARCEL` GPS: 1.0, `VILLAGE`: 0.85, `DISTRICT`: 0.70, `STATE`: 0.40). |
| **Model Confidence ($S_{\text{model}}$)** | $0.15$ | Output probability from machine learning biophysical model. |
| **Rule Coverage ($S_{\text{rule}}$)** | $0.15$ | ICAR regional agro-climatic rule and season calendar coverage. |

### Categorical Tiers:
- **`HIGH`** ($\ge 0.85$): Highly reliable for immediate operational field decisions.
- **`MEDIUM`** ($0.65 - 0.84$): Sound decision support; minor secondary inputs missing.
- **`LOW`** ($0.45 - 0.64$): Broad indicative advice; key parameters approximated.
- **`INSUFFICIENT`** ($< 0.45$): Critical data missing; actionable advisory suppressed.

---

## 3. Explainability Framework

Every generated advisory enforces a 5-dimension explainability contract:
1. **WHAT?** Precise agricultural action or intervention.
2. **WHY?** Agronomic rationale, soil chemistry triggers, or meteorological stress drivers.
3. **BASED ON?** Exact input features, test vectors, and scientific reference standards.
4. **CONFIDENCE?** Transparent numeric percentage and categorical tier.
5. **LIMITATIONS?** Explicit statement of missing sensors, unmeasured parameters, or seasonal uncertainties.
