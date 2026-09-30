# 🧠 AgriN — Advisory Engine & Intelligence Pipeline Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Active Standard  
> **Core Principle:** Machine Learning Prediction $\neq$ Agricultural Truth

---

## 1. Architectural Philosophy: Decoupling ML from Agronomic Truth

Machine learning models (such as Random Forest, Gradient Boosted Trees, or Neural Networks) are statistical pattern recognizers trained on specific datasets. They produce **conditional probability distributions**, not agronomic truth.

Treating raw ML output as direct agricultural recommendation introduces catastrophic risks:
1. **Out-of-Distribution Vulnerability:** An ML model trained primarily on Alluvial soil may predict Rice in an arid Sandy loam with high statistical probability if inputs align coincidentally with a training cluster.
2. **Missing Hard Constraints:** Statistical models do not inherently respect physical or biological impossibilities (e.g., planting a water-intensive 14-month sugarcane crop in an un-irrigated arid zone).
3. **Black-Box Opacity:** Farmers and agricultural officers cannot accept recommendations without knowing *why* a crop is recommended and *what risks* exist.

In AgriN, **ML prediction is treated as one piece of probabilistic evidence alongside agronomic rules, regional calendars, and environmental observations.**

---

## 2. The AgriN Agricultural Intelligence Pipeline

```text
┌────────────────────────────────────────────────────────┐
│                      Farm Inputs                       │
│    (Soil Test, Farm Location, Water Source, Season)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   ML Model Layer                       │
│             (Random Forest Classifier v1)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   ML Prediction                        │
│          (Multiclass Class Probabilities)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Agricultural Intelligence Layer             │
│                                                        │
│  ML Prediction                                         │
│        +                                               │
│  Regional Knowledge (State Crop Calendar / ACZ)        │
│        +                                               │
│  Live Weather / Historical Climatology                 │
│        +                                               │
│  Biophysical Hard Gates (Season, Water, Critical pH)   │
│        +                                               │
│  Soil Health Card Thresholds (ICAR Standards)          │
│        +                                               │
│  Data Confidence & Provenance Evaluation               │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│          Standard Advisory Synthesis Engine            │
│          (AgriculturalAdvisory Schema)                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 LLM Explanation Layer                  │
│       (Explains & Localizes Validated Advisories)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                Farmer-Facing Advisory                  │
│            (Actionable, Transparent, Traceable)        │
└────────────────────────────────────────────────────────┘
```

---

## 3. The Standard Advisory Object Schema

Every recommendation produced by AgriN conforms to the canonical `AgriculturalAdvisory` structure:

```json
{
  "advisory_id": "adv-crop-7c3e1a8b",
  "farm_id": "parbhani_sess-1249",
  "category": "CROP_SELECTION",
  "priority": "HIGH",
  "title": "Crop Suitability: Cotton (Kapus) (78.2%)",
  "recommendation": "Cotton is classified as 'Highly Suitable' under prevailing deep black soil and Kharif climate conditions.",
  "reasoning": [
    "[ML Model Prediction]: Machine learning model predicted statistical suitability baseline of 79.4%.",
    "[Agronomic Rule Evaluation]: Biophysical compatibility scored at 77.0% against ICAR Vertisol benchmarks.",
    "[Regional Calendar]: Season compatibility confirmed for Kharif season in Parbhani, Maharashtra.",
    "[Eligibility Gates]: Multiplier of 1.00 applied based on critical pH and water balance.",
    "[Supporting Factor]: Adequate Available Potassium (240 kg/ha) supports fiber quality.",
    "[Limiting Factor]: Marginally low Available Nitrogen requires split urea application."
  ],
  "supporting_observations": [
    { "type": "ML_SCORE", "value": 79.4, "unit": "%" },
    { "type": "RULE_SCORE", "value": 77.0, "unit": "%" },
    { "type": "FINAL_SCORE", "value": 78.2, "unit": "%" },
    { "type": "SOIL_PH", "value": 7.4, "unit": "pH" },
    { "type": "RAINFALL", "value": 750, "unit": "mm" }
  ],
  "actions": [
    "Select certified Bt cotton hybrid varieties approved for Marathwada.",
    "Ensure sowing aligns with the onset of Kharif monsoon rains (> 75mm cumulative rain).",
    "Incorporate 5 tonnes/ha FYM prior to last harrowing to improve moisture retention."
  ],
  "confidence": {
    "confidence": 0.78,
    "confidence_level": "HIGH",
    "coverage": "FULL",
    "data_resolution": "DISTRICT",
    "data_timestamp": "2026-09-30T10:30:00Z",
    "sources": [
      {
        "source_name": "AgriN Random Forest Crop Model v1",
        "source_type": "ML_MODEL",
        "coverage": "FULL",
        "resolution": "POINT"
      },
      {
        "source_name": "ICAR National Crop Agronomy Repository",
        "source_type": "AGRONOMIC_RULE",
        "coverage": "FULL",
        "resolution": "NATIONAL"
      }
    ]
  },
  "created_at": "2026-09-30T10:30:00Z",
  "valid_until": "2026-12-30T10:30:00Z"
}
```

---

## 4. Advisory Categories & Multi-Domain Support

| Category | Primary Focus | Supporting Inputs |
| :--- | :--- | :--- |
| `CROP_SELECTION` | Crop species suitability and ranking | Soil chemistry, season, live weather, regional calendar |
| `SOIL_HEALTH` | Nutrient balance, pH amendment, organic matter | Soil Health Card lab test, macro/micronutrient limits |
| `WATER_MANAGEMENT` | Irrigation scheduling, waterlogging avoidance | Rainfall forecast, soil drainage, crop water requirement |
| `WEATHER_RISK` | Extreme heat, unseasonal frost, cloudburst warnings | Live Open-Meteo feed, IMD weather warnings |
| `REGENERATIVE` | Soil building, intercropping, conservation tillage | Soil organic carbon, previous crop, farming system |
| `NUTRIENT` | Precision fertilizer doses (split application) | Stage of growth, soil deficiency, crop uptake curve |
| `HARVEST` | Safe harvest window based on rain forecasts | 7-day precipitation forecast, crop maturity stage |

---

## 5. Role of the LLM Explanation Layer

AgriN strictly demarcates the role of Large Language Models (LLMs):

1. **LLM as Explainer, NOT Truth Source:**
   - The LLM receives pre-validated, structured JSON containing the recommendation, reasoning bullets, and specific actions.
   - The LLM translates and adapts this structured data into conversational, farmer-friendly explanations.
2. **Forbidden LLM Behaviors:**
   - The LLM must **never hallucinate pesticide doses**, chemical concentrations, or seed rates not present in the agronomic knowledge base.
   - The LLM must **never fabricate disease diagnoses** or claim a crop is suitable when the underlying rule engine flagged a hard gate penalty.
   - If requested advice falls outside verified system data, the LLM must explicitly respond: *"This parameter is not verified by current soil/weather data. Please consult your local Krishi Vigyan Kendra (KVK)."`
