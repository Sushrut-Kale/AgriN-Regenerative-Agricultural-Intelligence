# ♻️ AgriN — Regenerative Agriculture Intelligence Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Active Standard & Implementation Blueprint  
> **Alignment:** Track 4 Core Objective — Regenerative & Climate-Resilient Agricultural Systems

---

## 1. Executive Summary & Philosophy

In conventional agricultural platforms, "regenerative agriculture" is frequently reduced to simplistic slogans like *"use organic fertilizer"* or an arbitrary 0–100 score with no scientific grounding.

AgriN treats Regenerative Agriculture as a **biophysical science of agro-ecosystem restoration**. 

Core architectural tenets:
1. **Decoupled Advisory Domain:** Asking *"What regenerative practice is appropriate for this farm?"* is fundamentally distinct from asking *"Which crop should I grow?"*. Both questions receive independent, specialized intelligence.
2. **Multi-Dimensional Practice Taxonomy:** Practices span 10+ agronomic mechanisms (legume rotation, cover cropping, minimum tillage, residue retention, micro-irrigation, biochar, agroforestry, IPM).
3. **No Arbitrary Composite Scores:** The system reports transparent **Component-Level Indicators** based on measured ground truth. If data for tillage or residue is missing, it is explicitly reported as `UNAVAILABLE`, not fabricated.

---

## 2. Regenerative Recommendation Engine Pipeline

```text
┌────────────────────────────────────────────────────────┐
│                      Farm Profile                      │
│   (Soil Chemistry, Water Regime, ACZ Zone, Season)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Regenerative Knowledge Engine              │
│       (10+ Verified Practices in practices.json)       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                  Candidate Practices                   │
│   (Filter by Regional Ecology & Cropping System)       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Suitability Evaluation                 │
│                                                        │
│  - Soil Organic Carbon deficit trigger                 │
│  - Available Nitrogen biological replenishment         │
│  - Rainfed vs Irrigated moisture balance               │
│  - Implementation complexity & economic tradeoffs     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                    Ranked Practices                    │
│   (Sorted by Biophysical Synergy & Farmer Feasibility) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                Standard Advisory Output                │
│    (AgriculturalAdvisory Category: REGENERATIVE)       │
└────────────────────────────────────────────────────────┘
```

---

## 3. The 7 Dimensions of Regenerative Readiness

Rather than producing an unjustified single composite number, AgriN evaluates 7 structural dimensions:

```text
┌──────────────────────────────────────────────────────────┐
│              7 Regenerative Dimensions                   │
├──────────────────────────┬───────────────────────────────┤
│ 1. Soil Organic Matter   │ Measured OC% vs 0.75% target  │
│ 2. Crop Diversity        │ Monoculture vs Rotation/Inter │
│ 3. Water Conservation    │ Micro-irrigation / In-situ BBF│
│ 4. Nutrient Management   │ INM / Bio-fertilizer balance  │
│ 5. Tillage Intensity     │ Conservation vs Deep ploughing│
│ 6. Residue Management    │ In-situ mulch vs Stubble burn │
│ 7. Biodiversity & Trees  │ Field bund trees / Agroforest │
└──────────────────────────┴───────────────────────────────┘
```

### 3.1 Transparent Component Indicators (Operational Example)

```json
{
  "methodology": "Component-Level Regenerative Indicators (ICAR Soil Quality Framework)",
  "soil_organic_matter": {
    "status": "Moderate (Depleted)",
    "measured_oc_percent": 0.54,
    "target_benchmark": ">= 0.75% for tropical semi-arid soils"
  },
  "crop_diversity": {
    "status": "Active Multi-Season Tracking",
    "previous_crop": "Soybean"
  },
  "water_conservation": {
    "status": "High (Micro-Irrigation Deployed)",
    "irrigation": "yes",
    "water_source": "drip"
  },
  "tillage_intensity": {
    "status": "UNAVAILABLE",
    "note": "Requires on-field observation or farmer management log"
  },
  "residue_management": {
    "status": "UNAVAILABLE",
    "note": "Requires post-harvest farm record or high-res satellite residue index"
  },
  "biodiversity_enhancement": {
    "status": "UNAVAILABLE",
    "note": "Requires farm perimeter tree/hedge inventory"
  }
}
```

---

## 4. Codified Practice Taxonomy (`practices.json`)

All practices are backed by peer-reviewed research from ICAR, CRIDA, and FAO:

1. **Legume-Inclusive Crop Rotation:** Biological Nitrogen fixation (30–60 kg N/ha), breaks root-knot nematode cycles.
2. **Multi-Species Cover Cropping:** Green manuring (Sunnhemp / Dhaincha), 70% erosion reduction on monsoon onset.
3. **Strip Intercropping & Canopy Stratification:** LER 1.25–1.45 (e.g., Pigeonpea + Soybean 1:4), rainfed climate buffer.
4. **Conservation / Minimum Tillage:** Preserves fungal hyphae and macro-aggregates, saves 40–60 L/ha tractor diesel.
5. **In-Situ Residue Retention & Mulching:** Drops summer soil temp by 4–8°C, saves 15–25% water, eliminates stubble burning smog.
6. **Integrated Nutrient Management (INM):** Combines organic manure, biofertilizers (Rhizobium/PSB), and targeted synthetic inputs; boosts NUE by 20–35%.
7. **Micro-Irrigation & Broad Bed Furrow (BBF):** 30–50% water savings, eliminates Vertisol waterlogging in heavy downpours.
8. **Ecological & Integrated Pest Management (IPM):** Pheromone traps, border trap crops, protects pollinator biodiversity.
9. **Agroforestry & Field Bund Plantation:** Perennial boundary trees (Neem, Subabul, Moringa) for windbreak and woody carbon.
10. **Biochar Soil Carbon Amendment:** Recalcitrant carbon from pyrolyzed cotton/pigeonpea stalks; decadal water retention boost.

---

## 5. Decision Rules in `backend/app/services/regenerative_service.py`

* **Low OC Rule:** If $\text{OC} < 0.60\%$, practices that deposit in-situ biomass (`PRACTICE_COVER_CROPS`, `PRACTICE_RESIDUE_RETENTION`, `PRACTICE_INM`) receive a $+15$ point boost.
* **Low Nitrogen Rule:** If $N < 280\text{ kg/ha}$, legume rotation (`PRACTICE_CROP_ROTATION`) receives a $+10$ point boost for biological fixing.
* **Rainfed Aridity Rule:** If farm is rainfed and rainfall $< 600\text{ mm}$, high-water biomass crops receive cautionary penalty so residual soil moisture is not depleted before cash crop sowing.
