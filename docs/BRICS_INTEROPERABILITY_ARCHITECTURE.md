# 🌐 AgriN — BRICS Agricultural Interoperability Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Strategic Architecture Specification (Implementation-Neutral)  
> **Scope:** Interoperability Blueprint across BRICS Member Nations (Brazil, Russia, India, China, South Africa)

---

## 1. Context & Motivation: The BRICS Agricultural Imperative

The BRICS nations represent over **40% of the global population**, **30% of global agricultural land**, and more than **40% of global cereal production**.

Despite immense shared challenges—soil organic matter depletion, climate-induced rainfall variability, emerging trans-boundary pests (such as Fall Armyworm and Desert Locusts), and the transition toward regenerative practices—agricultural intelligence remains siloed within national systems.

Phase 2.5 designs the **AgriN Data Exchange (ADE)** abstraction: a normalized, sovereign-respecting agricultural interchange model that establishes technical interoperability without compromising local data privacy or national data sovereignty laws.

---

## 2. Standardized Measurement & Coordinate System (SI Standards)

A prerequisite for cross-border model and data sharing is uniform measurement normalization:

| Parameter Domain | Standard Interchange Unit | Normalization Rule | Permitted Local Display (Frontend Only) |
| :--- | :--- | :--- | :--- |
| **Geographic Coordinates** | **WGS84 (EPSG:4326)** | Decimal degrees ($[-90.0, 90.0], [-180.0, 180.0]$) | Local grid systems (e.g. UTM, Gauss-Krüger) |
| **Temperature** | **Degrees Celsius (°C)** | Kelvin - 273.15 or Fahrenheit conversion | °F (if requested) |
| **Rainfall / Moisture** | **Millimeters (mm)** | 1 mm = 1 liter / m² | Inches, mm |
| **Land Parcel Area** | **Hectares (ha)** | $1\text{ ha} = 10,000\text{ m}^2 = 2.471\text{ acres}$ | Acres, Guntha, Bigha, Mu (亩) |
| **Soil Macronutrients** | **Milligrams per kilogram (mg/kg)** | Equivalent to parts per million (ppm) | kg/ha, quintals/ha |
| **Soil Electrical Conductivity** | **Decisiemens per meter (dS/m)** | Measured at 25°C ($1\text{ dS/m} = 1\text{ mS/cm}$) | $\mu\text{S/cm}$ |
| **Crop Yield** | **Metric Tonnes per Hectare (t/ha)** | 1 t/ha = 10 quintals/ha = 1000 kg/ha | Quintals/acre, Bushels/acre, Jin/mu |

---

## 3. The AgriN Data Exchange (ADE) Normalized Entities

The ADE schema defines 8 canonical interoperability abstractions:

```text
┌────────────────────────────────────────────────────────┐
│               AgriN Data Exchange (ADE)                │
├────────────────────────┬───────────────────────────────┤
│ 1. ADE_Farm            │ Sovereign ID, WGS84, Hectares │
│ 2. ADE_Crop            │ Botanical Name, FAO Crop Code │
│ 3. ADE_SoilObservation │ mg/kg standardized nutrients  │
│ 4. ADE_WeatherObs      │ °C, mm, relative humidity %   │
│ 5. ADE_SatelliteObs    │ Sentinel-2 / Landsat indices  │
│ 6. ADE_DiseaseObs      │ EPPO Global Pathogen Code     │
│ 7. ADE_Advisory        │ Multi-category advisory JSON  │
│ 8. ADE_Regenerative    │ Standardized practice vector  │
└────────────────────────┴───────────────────────────────┘
```

### 3.1 Entity Specifications

```json
{
  "ade_version": "1.0.0",
  "ade_farm": {
    "sovereignty_country_iso": "IND",
    "farm_uuid": "ade-farm-91-ind-2849",
    "boundary_type": "POINT",
    "coordinates": { "latitude": 19.2612, "longitude": 76.7745 },
    "area_hectares": 2.4,
    "primary_agro_zone_code": "IN_ACZ_07"
  },
  "ade_crop": {
    "fao_crop_code": "01441",
    "botanical_name": "Gossypium hirsutum L.",
    "common_english": "Upland Cotton",
    "local_designation": "Kapus (कापूस)"
  },
  "ade_soil_observation": {
    "timestamp_utc": "2026-09-30T00:00:00Z",
    "laboratory_standard": "ISO_17025",
    "parameters": {
      "ph_water": 7.4,
      "organic_carbon_percent": 0.54,
      "available_nitrogen_mg_kg": 95.0,
      "available_phosphorus_mg_kg": 6.8,
      "available_potassium_mg_kg": 105.0
    }
  }
}
```

---

## 4. Multi-Country Architecture Mapping

Without building custom APIs for foreign systems prematurely, AgriN’s normalized abstractions map directly onto the agricultural datasets of all 5 founding BRICS partners:

```text
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│    BRAZIL     │     │    RUSSIA     │     │     INDIA     │
│  (EMBRAPA /   │     │  (Rosgidromet │     │    (ICAR /    │
│  SICAR Par.)  │     │  Agro-Meteo)  │     │   DAC&FW SHC) │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────────────────────────────────────────────────┐
│                 AgriN Data Exchange (ADE)                 │
│         (Standardized WGS84, SI Units, ISO Codes)         │
└───────────────────────────────────────────────────────────┘
        ▲                     ▲
        │                     │
┌───────┴───────┐     ┌───────┴───────┐
│     CHINA     │     │ SOUTH AFRICA  │
│  (MARA Crop   │     │ (ARC Agro-    │
│  Statistics)  │     │  Climatology) │
└───────────────┘     └───────────────┘
```

### Country-Specific Harmonization Profiles:

1. **India (`IND`):**
   - Source Systems: Soil Health Card (DAC&FW), IMD Gridded Weather, ICAR Packages of Practices.
   - Alignment: Integrated into AgriN’s primary database and services.

2. **Brazil (`BRA`):**
   - Partner Entities: EMBRAPA (Brazilian Agricultural Research Corporation), SICAR (Rural Environmental Registry).
   - Agro-Ecology: Cerrado savannahs, Oxisols/Ferralsols (acidic, high aluminum toxicity, high phosphorus fixation).
   - Harmonization: ADE pH model incorporates SMP buffer index and aluminum saturation ($m\%$).

3. **Russia (`RUS`):**
   - Partner Entities: Russian Academy of Sciences (RAS), Rosgidromet Agrometeorological Service.
   - Agro-Ecology: Chernozem (Black Earth belt), Podzolic soils; short growing seasons, winter wheat vernalization.
   - Harmonization: ADE crop calendar supports winter dormancy cycles and extreme frost risk ($< -20^\circ\text{C}$).

4. **China (`CHN`):**
   - Partner Entities: Ministry of Agriculture and Rural Affairs (MARA), Chinese Academy of Agricultural Sciences (CAAS).
   - Agro-Ecology: Double-cropping paddy-wheat rotations, loess plateau dryland farming, intensive high-density horticulture.
   - Harmonization: Unit adapter translates local *Mu* ($1\text{ ha} = 15\text{ mu}$) and Chinese soil taxonomy classifications.

5. **South Africa (`ZAF`):**
   - Partner Entities: Agricultural Research Council (ARC), Department of Agriculture, Land Reform and Rural Development (DALRRD).
   - Agro-Ecology: Semi-arid Karoo, Highveld maize triangle, Western Cape winter-rainfall Mediterranean orchards.
   - Harmonization: Shares semi-arid vertisol and dryland water conservation profiles with Central India (CRIDA).

---

## 5. Federated Privacy & Cross-Border Sovereign Safeguards

To prevent cross-border data vulnerability:
1. **Federated Model Learning:** Algorithms travel to the data, not raw farm ownership records.
2. **Parcel Anonymization:** Raw cadastral parcel owner IDs are stripped; only spatial polygon geometry and biophysical indicators are exchanged.
3. **Open Standards:** Built on open standards (OGC GeoJSON, ISO 19115 Geospatial Metadata, STAC SpatioTemporal Asset Catalogs).
