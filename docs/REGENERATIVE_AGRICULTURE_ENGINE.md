# 🌱 Regenerative Agriculture Engine Specification

> **Module:** `backend/app/services/regenerative_advisor.py`  
> **Evaluation Framework:** ICAR, CRIDA, and FAO Conservation Agriculture Guidelines  
> **Status:** `IMPLEMENTED` & Fully Verified  

---

## 1. Core Principles

The AgriN Regenerative Agriculture Engine shifts agricultural decision support from single-season extractive crop maximization to multi-season agro-ecosystem resilience.

The engine evaluates practices across 8 distinct regenerative categories:
1. **Crop Rotation:** Legume-cereal breaks, root architecture alternation, and pest cycle interruption.
2. **Crop Diversification:** Intercropping (e.g., Cotton + Pigeonpea 4:2, Soybean + Pigeonpea 3:1), boundary crops, and multi-tier canopy utilization.
3. **Cover Crops:** Green manure cultivation (Sesbania, Sunn hemp) during fallow windows to suppress weeds and fix biological nitrogen.
4. **Soil Organic Carbon (SOC) Rebuilding:** Compost, FYM, vermicompost, and biochar applications to reverse sub-0.5% carbon depletion.
5. **Water Conservation:** Broad Bed Furrows (BBF), compartmental bunding, micro-irrigation, and rainwater harvesting.
6. **Reduced Soil Disturbance:** Minimum tillage, zero tillage, and permanent raised beds to preserve soil fungal hyphae and micro-aggregate structure.
7. **Integrated Nutrient Management (INM):** Biofertilizers (Rhizobium, PSB, Azotobacter) combined with site-specific nutrient management.
8. **Residue Management:** In-situ retention of crop biomass, mulching, avoiding stubble burning, and mulcher integration.

---

## 2. Decision Logic & Trigger Conditions

The engine dynamically evaluates:
$$\text{Regenerative Opportunity} = f(\text{Crop Suitability}, \text{Soil Health Constraints}, \text{Water Availability}, \text{Climate Context})$$

```python
# Illustrative Trigger Matrix
if soil_profile.get("organic_matter", {}).get("classification") in ["CRITICAL", "LOW"]:
    recommend(
        category="SOIL_ORGANIC_MATTER",
        practice="In-Situ Crop Residue Incorporation & FYM Enriched Compost",
        priority="HIGH"
    )

if soil_profile.get("chemical_properties", {}).get("pH", {}).get("classification") == "ACIDIC":
    recommend(
        category="SOIL_IMPROVEMENT",
        practice="Agricultural Lime Amendment with Humic Substances",
        priority="HIGH"
    )

if farm_data.get("irrigation_available") == "no" and farm_data.get("rainfall", 0) < 750:
    recommend(
        category="WATER_CONSERVATION",
        practice="Broad Bed and Furrow (BBF) with Residue Mulching",
        priority="HIGH"
    )
```

---

## 3. Strict Missing Data Disclosures (`insufficient_data`)

The engine enforces strict scientific integrity: when critical parameters are missing, it does **NOT** guess or generate generic advice.

```json
{
  "status": "insufficient_data",
  "reason": "Insufficient environmental or soil context provided for regenerative evaluation.",
  "missing_data_requirements": [
    "district or agro_climatic_zone",
    "soil_type or soil chemical parameters (pH, OC)",
    "current_crop or intended crop"
  ],
  "recommendations": []
}
```

---

## 4. Verification Evidence

Automated test: `tests/test_track4_evolution.py::test_regenerative_advisor_classes_and_insufficient_data`
- Verified: Incomplete profile returns `status="insufficient_data"`.
- Verified: Populated profile generates multi-category regenerative recommendations with detailed action items and expected benefits.
