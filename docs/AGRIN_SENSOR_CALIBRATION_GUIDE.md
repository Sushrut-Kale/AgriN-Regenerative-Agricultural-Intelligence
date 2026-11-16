# ⚖️ AgriN Sensor Calibration Guide
**System:** AgriSense In-Situ Sensor Suite  
**Document Code:** AGRIN-CALIB-001  

---

## 1. Soil Moisture Probe Calibration (Capacitive)

Capacitive soil moisture sensors measure the dielectric permittivity of the surrounding soil matrix. Because soil bulk density and texture vary across regions, 2-point calibration is recommended:

```
[Dry Air] ── (Zero Water Baseline: ADC Count ~2850)
[Saturated Soil] ── (Field Capacity Baseline: ADC Count ~1350)
```

### Procedure:
1. Connect probe to ADS1115 Channel A0.
2. Hold probe completely dry in ambient air. Run calibration routine and record $ADC_{air}$.
3. Submerge probe in a container of saturated local soil (not pure water, to match dielectric mineral properties). Record $ADC_{sat}$.
4. Input these values into `hardware_profile.json`:
   ```json
   "soil_moisture": {
     "raw_min_dry": 2850,
     "raw_max_wet": 1350
   }
   ```

---

## 2. Soil pH Sensor Calibration (Glass Electrode)

Standard 2-point buffer calibration is mandatory to account for probe membrane aging and zero-point offset:

1. **Rinse**: Rinse glass bulb thoroughly with distilled water and gently blot with lint-free paper.
2. **Buffer 7.00**: Submerge probe in $pH\ 7.00$ standard buffer solution. Allow 60 seconds for thermal equilibration. Record voltage $V_{7}$.
3. **Rinse again**: Rinse probe in distilled water.
4. **Buffer 4.01**: Submerge probe in $pH\ 4.01$ buffer solution. Record voltage $V_{4}$.
5. **Calculate Sensitivity**:
   $$\text{Nernst Sensitivity (mV/pH)} = \frac{V_7 - V_4}{7.00 - 4.01}$$
   If sensitivity is $< 50\text{ mV/pH}$, clean probe in mild acid bath or replace membrane.

---

## 3. Soil Electrical Conductivity (EC) Calibration

Electrical conductivity indicates dissolved ionic salts and salinity hazard:

1. Prepare standard $1413\ \mu\text{S/cm}$ ($1.413\ \text{dS/m}$) potassium chloride ($KCl$) calibration solution.
2. Submerge stainless steel pins into solution at $25^\circ\text{C}$.
3. Record raw voltage $V_{calib}$.
4. Update cell constant $K_{cell}$ in firmware configuration.

---

## 4. Periodic Maintenance Schedule

| Sensor | Maintenance Action | Recommended Frequency |
| :--- | :--- | :--- |
| **Capacitive Moisture** | Inspect conformal coating for scratches or soil compaction cracks | Biannually (Pre-Kharif, Pre-Rabi) |
| **Soil pH** | Re-calibrate in buffer 4.0 and 7.0; clean glass bulb | Every 60 days of continuous soil deployment |
| **Soil EC** | Clean electrode pins with isopropyl alcohol to remove bio-film | Every 90 days |
| **DS18B20 Temp** | Check cable insulation for rodent or moisture damage | Annually |
| **Solar Panel** | Clean glass surface of dust, soil splashes, and bird droppings | Monthly |
