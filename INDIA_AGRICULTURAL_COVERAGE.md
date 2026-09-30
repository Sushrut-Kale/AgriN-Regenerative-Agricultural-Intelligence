# 🇮🇳 AgriN — Pan-India Agricultural Coverage Matrix

> **System Name:** AgriN: Regenerative Agricultural Intelligence  
> **Registry Version:** 2.0.0  
> **Geographic Scope:** All 28 Indian States & 8 Union Territories  
> **Integrity Policy:** Zero-Fabrication Standard (Strict differentiation between *Full*, *Partial*, *Basic*, and *Unavailable* data).

---

## 1. Coverage Classification Taxonomy

- 🟢 **Full**: Localized district-level dataset, verified soil health baselines, regional crop calendar, and empirical field verification records available.
- 🟡 **Partial**: State and district geographic mapping configured, centroid coordinates active, regional climate benchmarks available, standard national/zonal crop calendar applied.
- 🔵 **Basic**: State/UT coordinates mapped, Agro-Climatic Zone (ACZ) identified, national fallback agronomic rules and Open-Meteo live weather operational.
- ⚪ **Unavailable**: High-altitude uncultivated territories or non-agricultural urban enclaves where agricultural intelligence is omitted.

---

## 2. States & Union Territories Coverage Matrix

| State / Union Territory | Administrative Status | ICAR Agro-Climatic Zone | District Coverage | Crop Calendar Coverage | Soil Health Baseline | Live Weather & GPS | Agronomic Rules | Confidence Level | Known Gaps / Data Limitations |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Maharashtra** | State | Western Plateau & Hills / West Coast | **Full** (36 Districts) | **Full** (Kharif, Rabi, Summer, Perennial) | **Full** (Vertisols, SHC norms) | **Full** (Live + 20 benchmarks) | **Full** (TNAU/ICAR calibrated) | **High** | Micronutrient defaults applied if user test has only NPK. |
| **Punjab** | State | Trans-Gangetic Plain | **Partial** (7 Major Districts) | **Full** (Kharif Rice/Maize, Rabi Pulses) | **Partial** (Alluvial standards) | **Full** (Live + Centroids) | **Full** (Trans-Gangetic rules) | **High** | Tubewell water salinity data not yet linked. |
| **Haryana** | State | Trans-Gangetic Plain | **Partial** (5 Major Districts) | **Full** (Kharif/Rabi/Zaid) | **Partial** (Alluvial standards) | **Full** (Live + Centroids) | **Full** (Trans-Gangetic rules) | **High** | Groundwater depletion index not yet incorporated. |
| **Rajasthan** | State | Western Dry / Central Plateau | **Partial** (7 Major Districts) | **Full** (Arid Kharif pulses, Zaid) | **Partial** (Arid / Sandy norms) | **Full** (Live + Centroids) | **Full** (Drought-hardy logic) | **High** | Canal vs desert dunes differentiation requires sub-district input. |
| **Madhya Pradesh** | State | Central & Western Plateau | **Partial** (6 Major Districts) | **Full** (Soybean/Gram heartland) | **Partial** (Black/Mixed Red-Black) | **Full** (Live + Centroids) | **Full** (Central Plateau rules) | **High** | Micro-watershed boundaries estimated. |
| **Gujarat** | State | Gujarat Plains & Hills | **Partial** (7 Major Districts) | **Full** (Cotton/Oilseeds/Horticulture) | **Partial** (Black/Alluvial/Saline) | **Full** (Live + Centroids) | **Full** (Semi-arid rules) | **High** | Coastal salinity intrusion requires local EC tests. |
| **Karnataka** | State | Southern Plateau & West Coast | **Partial** (8 Major Districts) | **Full** (Kharif/Rabi/Perennial) | **Partial** (Red Loam / Black) | **Full** (Live + Centroids) | **Full** (Southern Plateau rules) | **High** | Tank irrigation schedule not yet dynamically synchronized. |
| **Tamil Nadu** | State | East Coast / Southern Plateau | **Partial** (7 Major Districts) | **Full** (Kuruvai, Samba, Thaladi) | **Partial** (Alluvial delta / Red soil) | **Full** (Live + Centroids) | **Full** (Cauvery delta rules) | **High** | Northeast monsoon distribution shifts handled via live IMD sync. |
| **Kerala** | State | West Coast Plains & Ghats | **Partial** (5 Major Districts) | **Full** (Plantation & Multi-season Rice) | **Partial** (Laterite / Acidic norms) | **Full** (Live + Centroids) | **Full** (High-rainfall rules) | **High** | Hill slope terracing and altitude microclimates estimated. |
| **Andhra Pradesh** | State | East Coast & Southern Plateau | **Partial** (11 Major Districts) | **Full** (Kharif/Rabi cycles) | **Partial** (Deltaic Alluvial / Red) | **Full** (Live + Centroids) | **Full** (East Coast rules) | **High** | Cyclone risk index currently relies on live wind/precipitation. |
| **Telangana** | State | Southern Plateau & Hills | **Partial** (5 Major Districts) | **Full** (Cotton/Maize/Pigeonpeas) | **Partial** (Red Sandy / Deep Black) | **Full** (Live + Centroids) | **Full** (Deccan Plateau rules) | **High** | Tank water level integration planned for Phase 3. |
| **Uttar Pradesh** | State | Upper & Middle Gangetic Plain | **Partial** (9 Major Districts) | **Full** (Gangetic Kharif/Rabi) | **Partial** (Deep Alluvial norms) | **Full** (Live + Centroids) | **Full** (Gangetic Basin rules) | **High** | Flood inundation duration in lowlands estimated. |
| **Bihar** | State | Middle Gangetic Plain | **Partial** (6 Major Districts) | **Full** (Paddy/Maize/Pulses) | **Partial** (Alluvial fertile norms) | **Full** (Live + Centroids) | **Full** (Middle Gangetic rules) | **High** | North Bihar drainage constraints rely on user drainage input. |
| **West Bengal** | State | Lower Gangetic & East Himalayan | **Partial** (7 Major Districts) | **Full** (Aman, Aus, Boro Rice, Jute) | **Partial** (Deltaic Alluvial / Acidic) | **Full** (Live + Centroids) | **Full** (Humid Delta rules) | **High** | Sundarbans coastal salinity requires measured EC input. |
| **Odisha** | State | Eastern Plateau & East Coast | **Partial** (6 Major Districts) | **Full** (Coastal/Plateau Rice) | **Partial** (Lateritic / Coastal Alluvial) | **Full** (Live + Centroids) | **Full** (Eastern Region rules) | **High** | Red-laterite phosphorus fixation warnings enabled. |
| **Chhattisgarh** | State | Eastern Plateau & Hills | **Partial** (4 Major Districts) | **Full** (Rice bowl Kharif) | **Partial** (Red and Yellow soils) | **Full** (Live + Centroids) | **Full** (Plateau rules) | **High** | Upland bunded paddy vs lowland unbunded distinction estimated. |
| **Assam** | State | Eastern Himalayan Region | **Partial** (6 Major Districts) | **Full** (Brahmaputra Valley seasons) | **Partial** (Acidic Alluvium) | **Full** (Live + Centroids) | **Full** (Humid Subtropical rules) | **High** | River island (Char) micro-soils mapped to alluvial base. |
| **Jharkhand** | State | Eastern Plateau & Hills | **Partial** (4 Major Districts) | **Full** (Plateau Kharif/Rabi) | **Partial** (Red sandy loam / Gravelly) | **Full** (Live + Centroids) | **Full** (Chota Nagpur rules) | **High** | Upland moisture retention estimated. |
| **Himachal Pradesh**| State | Western Himalayan Region | **Partial** (4 Major Districts) | **Partial** (Horticulture/Hills) | **Partial** (Brown Hill / Mountain) | **Full** (Live + Centroids) | **Partial** (Chilling hour logic) | **Medium**| Valley elevation gradient requires accurate altitude. |
| **Uttarakhand** | State | Western Himalayan & Upper Gangetic | **Partial** (4 Major Districts) | **Partial** (Tarai & Hill terrace) | **Partial** (Submontane / Tarai Alluvium) | **Full** (Live + Centroids) | **Partial** (Himalayan rules) | **Medium**| Tarai belt vs high-altitude hill terracing distinct. |
| **Jammu & Kashmir**| UT | Western Himalayan Region | **Partial** (4 Major Districts) | **Partial** (Temperate apple/pulse) | **Partial** (Mountain / Karewa soils) | **Full** (Live + Centroids) | **Partial** (Temperate rules) | **Medium**| Winter snow cover duration handled via temperature thresholds. |
| **Goa** | State | West Coast Plains & Ghats | **Partial** (2 Districts) | **Full** (Coastal Rice/Coconut) | **Partial** (Lateritic Coastal) | **Full** (Live + Centroids) | **Full** (West Coast rules) | **High** | Small territory; complete centroid coverage. |
| **Sikkim** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (Organic hill farming) | **Partial** (Acidic forest / Mountain) | **Full** (Live + Centroids) | **Partial** (Organic norms) | **Medium**| 100% organic certification status noted in advisory. |
| **Tripura** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (Humid Valley seasons) | **Partial** (Red loam / Alluvial) | **Full** (Live + Centroids) | **Partial** (Eastern rules) | **Medium**| Regional pulse benchmarks active. |
| **Manipur** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (Imphal valley vs hills) | **Partial** (Peaty / Alluvial) | **Full** (Live + Centroids) | **Partial** (Eastern rules) | **Medium**| Valley vs hill shifting cultivation distinction noted. |
| **Meghalaya** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (High rainfall hill) | **Partial** (Acidic Laterite) | **Full** (Live + Centroids) | **Partial** (High-precipitation rules) | **Medium**| Very high rainfall (2400-3200mm) bounds verified. |
| **Mizoram** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (Hill terrace seasons) | **Partial** (Red and Yellow hill) | **Full** (Live + Centroids) | **Partial** (Eastern rules) | **Medium**| Terraced hill slope advisory enabled. |
| **Nagaland** | State | Eastern Himalayan Region | **Partial** (2 Districts) | **Partial** (Hill terrace seasons) | **Partial** (Ferruginous red) | **Full** (Live + Centroids) | **Partial** (Eastern rules) | **Medium**| Jhum fallow restoration cycles noted. |
| **Arunachal Pradesh**| State| Eastern Himalayan Region | **Partial** (3 Districts) | **Partial** (Valley subtropical to alpine) | **Partial** (Mountain forest soils) | **Full** (Live + Centroids) | **Partial** (Eastern rules) | **Medium**| Alpine zones flagged as low agricultural viability. |
| **Delhi** | UT | Trans-Gangetic Plain | **Full** (2 Urban/Peri-urban) | **Full** (Peri-urban vegetables/cereal) | **Partial** (Yamuna Alluvium) | **Full** (Live + Centroids) | **Full** (Trans-Gangetic rules) | **High** | Peri-urban horticulture preference configured. |
| **Chandigarh** | UT | Trans-Gangetic Plain | **Full** (1 District) | **Full** (Trans-Gangetic calendar) | **Partial** (Siwalik Alluvium) | **Full** (Live + Centroids) | **Full** (Trans-Gangetic rules) | **High** | Urban/semi-urban territory. |
| **Puducherry** | UT | East Coast Plains & Hills | **Full** (2 Districts) | **Full** (Cauvery delta / coastal) | **Partial** (Coastal Alluvial) | **Full** (Live + Centroids) | **Full** (East Coast rules) | **High** | Complete centroid coverage. |
| **Dadra & Nagar Haveli and Daman & Diu** | UT | Gujarat Plains & Hills | **Full** (2 Districts) | **Full** (Coastal/Paddy calendar) | **Partial** (Coastal Alluvium) | **Full** (Live + Centroids) | **Full** (Gujarat Plains rules) | **High** | Complete centroid coverage. |
| **Andaman & Nicobar** | UT | Islands Region | **Basic** (1 District Centroid) | **Basic** (Tropical Island calendar) | **Basic** (Coastal/Marine Alluvium) | **Full** (Live + Centroids) | **Basic** (Island rules) | **Medium**| Island plantation crops prioritized. |
| **Lakshadweep** | UT | Islands Region | **Basic** (1 District Centroid) | **Basic** (Coral Island coconut) | **Basic** (Coral sand) | **Full** (Live + Centroids) | **Basic** (Island rules) | **Medium**| Highly specialized atoll coconut agriculture. |
| **Ladakh** | UT | Western Himalayan Region | **Basic** (2 Districts - Leh, Kargil) | **Basic** (Cold Arid Summer only) | **Basic** (Cold Desert soils) | **Full** (Live + Centroids) | **Basic** (Extreme cold rules) | **Medium**| Strict single-season summer cultivation window. |

---

## 3. Data Integrity & Provenance Summary

1. **Weather Data**: Sourced directly from **Open-Meteo Global API** using exact GPS coordinates or Indian district centroids with IMD climatology fallback.
2. **Crop Requirements**: Calibrated against **ICAR Package of Practices** and **TNAU Agritech Portal**.
3. **Soil Health Standards**: Calibrated against the **Government of India National Soil Health Card (SHC) Scheme**.
4. **Agro-Climatic Zones**: Mapped strictly to the **15 National Planning Commission / ICAR ACZ Definitions**.

---
*Maintained under `docs/INDIA_AGRICULTURAL_COVERAGE.md` and root `INDIA_AGRICULTURAL_COVERAGE.md`.*
