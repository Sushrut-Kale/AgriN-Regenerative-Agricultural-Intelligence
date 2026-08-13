# FarmFriend AI — Showcase Demo & Test Scenarios

**Document Version**: 2.0  
**Updated**: 2026-08-13  

---

## Reproducible Test Scenarios

### Scenario 1: Beed — Kharif — Rainfed (Marathwada Dryland)
- **Location**: Beed, Maharashtra
- **Season**: Kharif
- **Irrigation**: Rainfed (`irrigation_available`: "no")
- **Soil Type**: Heavy Black Soil (Vertisol)
- **Soil Test Values**: N=260, P=16, K=320, S=12, Zn=0.52, Fe=4.8, Cu=0.42, Mn=4.5, B=0.45, pH=7.8, EC=0.45, OC=0.58
- **Climate**: Temp 29°C, Humidity 62%, Rainfall 680 mm
- **Expected Agronomic Ranking**:
  1. **Cotton / Kapas** (High suitability; suited for Kharif black soil)
  2. **Soybean** (High suitability; 680mm rainfed Kharif oilseed)
  3. **Pigeonpea / Tur** (High suitability; deep-rooted drought resilient Kharif pulse)
  4. **Bajra / Jowar** (Suitable; drought tolerant millet/grain)

---

### Scenario 2: Beed — Kharif — Assured Drip Irrigation
- **Location**: Beed, Maharashtra
- **Season**: Kharif
- **Irrigation**: Assured Drip (`irrigation_available`: "yes")
- **Expected Shift**:
  - Drip irrigation enables high-value cash crops and perennial orchards (Pomegranate, Cotton, Sugarcane) with elevated water security confidence.

---

### Scenario 3: Punjab — Rabi — Canal Irrigation
- **Location**: Ludhiana, Punjab
- **Season**: Rabi
- **Irrigation**: Assured Irrigation
- **Soil Test Values**: N=310, P=24, K=240, S=18, Zn=0.85, Fe=7.5, Cu=0.55, Mn=5.8, B=0.65, pH=7.2, EC=0.35, OC=0.72
- **Climate**: Temp 18°C, Humidity 72%, Rainfall 120 mm
- **Expected Agronomic Ranking**:
  1. **Wheat** (Top Rabi cereal)
  2. **Chickpea** (Top Rabi pulse)
  3. **Mustard** (Top Rabi oilseed)
