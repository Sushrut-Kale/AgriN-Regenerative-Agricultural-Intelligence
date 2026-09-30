"""
AgriN Soil Intelligence Service
Evaluates multi-parameter Soil Health Card observations against official ICAR / DAC&FW standards.
Generates comprehensive Soil Health Profiles, diagnoses limiting constraints, and computes
grounded soil improvement recommendations without synthetic heuristics.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

STANDARDS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "soil_health_standards.json"

_cached_standards: Optional[Dict[str, Any]] = None


def load_soil_standards() -> Dict[str, Any]:
    global _cached_standards
    if _cached_standards is None:
        if STANDARDS_PATH.exists():
            with open(STANDARDS_PATH, "r", encoding="utf-8") as f:
                _cached_standards = json.load(f)
        else:
            _cached_standards = {"nutrients": {}, "constraints_rules": []}
    return _cached_standards


def assess_soil_health(
    soil_data: Dict[str, Any],
    soil_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates soil parameters and generates a structured Soil Health Profile.
    
    Parameters:
        soil_data: Dictionary containing: N, P, K, pH, EC, OC, S, Zn, Fe, Cu, Mn, B, moisture
        soil_type: Optional physical soil type (e.g. 'black', 'alluvial', 'red', 'sandy', 'clayey')
        
    Returns:
        Structured dictionary matching the SoilHealthProfile schema.
    """
    standards = load_soil_standards()
    nutrients_spec = standards.get("nutrients", {})
    constraints_rules = standards.get("constraints_rules", [])

    # Extract parameters safely with physical validity bounds checking
    def _get_float(key: str) -> Optional[float]:
        v = soil_data.get(key)
        if v is None and key == "pH":
            v = soil_data.get("ph")
        if v is None or v == "" or v == "unknown":
            return None
        try:
            val = float(v)
            # Physical validity boundaries
            if key == "pH":
                if val < 0.0 or val > 14.0:
                    return None  # Discard physically impossible pH
                return val
            if key == "EC":
                if val < 0.0 or val > 50.0:
                    return None
                return val
            if key == "OC":
                if val < 0.0 or val > 15.0:
                    return None
                return val
            if val < 0.0:
                return None  # Negative nutrient values are physically invalid
            return val
        except (ValueError, TypeError):
            return None

    n_val = _get_float("N")
    p_val = _get_float("P")
    k_val = _get_float("K")
    ph_val = _get_float("pH")
    ec_val = _get_float("EC")
    oc_val = _get_float("OC")
    s_val = _get_float("S")
    zn_val = _get_float("Zn")
    fe_val = _get_float("Fe")
    cu_val = _get_float("Cu")
    mn_val = _get_float("Mn")
    b_val = _get_float("B")
    moisture_val = _get_float("moisture")

    # Evaluate completeness
    core_params = {"N": n_val, "P": p_val, "K": k_val, "pH": ph_val, "EC": ec_val, "OC": oc_val}
    provided_core = sum(1 for v in core_params.values() if v is not None)
    total_core = len(core_params)


    if provided_core == 0:
        return {
            "status": "INSUFFICIENT_DATA",
            "score": 0.0,
            "confidence": 0.0,
            "confidence_level": "INSUFFICIENT",
            "nutrient_status": {},
            "chemical_properties": {},
            "organic_matter": {},
            "soil_constraints": [],
            "limiting_factors": ["No soil parameters provided for assessment"],
            "positive_indicators": [],
            "recommended_improvement_areas": ["Conduct a standard Soil Health Card test covering NPK, pH, EC, OC and micronutrients."],
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    limiting_factors: List[str] = []
    positive_indicators: List[str] = []
    recommended_improvements: List[str] = []
    detected_constraints: List[Dict[str, Any]] = []

    # 1. Nutrient Status Evaluation (N, P, K)
    nutrient_scores = []
    nutrient_status: Dict[str, Any] = {}

    # Nitrogen
    if n_val is not None:
        if n_val < 280.0:
            nutrient_status["N"] = {"value": n_val, "status": "DEFICIENT", "level": "Low", "unit": "kg/ha"}
            limiting_factors.append(f"Available Nitrogen is low ({n_val:.1f} kg/ha < 280 kg/ha benchmark)")
            recommended_improvements.append("Apply 25% extra nitrogen split dose or cultivate short-duration legume green manure (Sunnhemp/Dhaincha).")
            nutrient_scores.append(50.0)
        elif n_val <= 560.0:
            nutrient_status["N"] = {"value": n_val, "status": "OPTIMAL", "level": "Medium", "unit": "kg/ha"}
            positive_indicators.append(f"Available Nitrogen ({n_val:.1f} kg/ha) is in the balanced agronomic zone.")
            nutrient_scores.append(90.0)
        else:
            nutrient_status["N"] = {"value": n_val, "status": "SURPLUS", "level": "High", "unit": "kg/ha"}
            positive_indicators.append(f"Available Nitrogen ({n_val:.1f} kg/ha) is high; protect against leaching.")
            recommended_improvements.append("Reduce chemical nitrogen by 20-25% to prevent vegetative lodging and groundwater nitrate contamination.")
            nutrient_scores.append(75.0)

    # Phosphorus
    if p_val is not None:
        if p_val < 10.0:
            nutrient_status["P"] = {"value": p_val, "status": "DEFICIENT", "level": "Low", "unit": "kg/ha"}
            limiting_factors.append(f"Available Phosphorus is deficient ({p_val:.1f} kg/ha < 10 kg/ha)")
            recommended_improvements.append("Band-place single superphosphate (SSP) with organic manure and inoculate with Phosphate Solubilizing Bacteria (PSB).")
            nutrient_scores.append(50.0)
        elif p_val <= 25.0:
            nutrient_status["P"] = {"value": p_val, "status": "OPTIMAL", "level": "Medium", "unit": "kg/ha"}
            positive_indicators.append(f"Available Phosphorus ({p_val:.1f} kg/ha) is optimal for root development.")
            nutrient_scores.append(95.0)
        else:
            nutrient_status["P"] = {"value": p_val, "status": "SURPLUS", "level": "High", "unit": "kg/ha"}
            nutrient_scores.append(85.0)

    # Potassium
    if k_val is not None:
        if k_val < 108.0:
            nutrient_status["K"] = {"value": k_val, "status": "DEFICIENT", "level": "Low", "unit": "kg/ha"}
            limiting_factors.append(f"Available Potassium is low ({k_val:.1f} kg/ha < 108 kg/ha)")
            recommended_improvements.append("Incorporate Muriate of Potash (MOP) or apply wood ash / composted biomass.")
            nutrient_scores.append(55.0)
        elif k_val <= 280.0:
            nutrient_status["K"] = {"value": k_val, "status": "OPTIMAL", "level": "Medium", "unit": "kg/ha"}
            positive_indicators.append(f"Available Potassium ({k_val:.1f} kg/ha) is optimal for stress tolerance.")
            nutrient_scores.append(95.0)
        else:
            nutrient_status["K"] = {"value": k_val, "status": "SURPLUS", "level": "High", "unit": "kg/ha"}
            positive_indicators.append(f"Soil possesses high natural reserve Potassium ({k_val:.1f} kg/ha).")
            nutrient_scores.append(90.0)

    # 2. Chemical Properties (pH & EC)
    chemical_scores = []
    chemical_status: Dict[str, Any] = {}

    if ph_val is not None:
        if ph_val < 5.5:
            chemical_status["pH"] = {"value": ph_val, "classification": "STRONGLY_ACIDIC", "hazard": True}
            limiting_factors.append(f"Soil is strongly acidic (pH {ph_val:.2f} < 5.5), inducing aluminum/iron toxicity and P-fixation.")
            recommended_improvements.append("Apply agricultural lime or dolomite based on soil buffer capacity; use Rock Phosphate instead of DAP.")
            chemical_scores.append(40.0)
            detected_constraints.append({
                "constraint_id": "SC-002",
                "name": "Soil Acidity Hazard",
                "severity": "CRITICAL",
                "value": ph_val,
                "remediation": "Broadcast agricultural lime (CaCO3) @ 2-4 t/ha with green manuring."
            })
        elif ph_val <= 6.5:
            chemical_status["pH"] = {"value": ph_val, "classification": "SLIGHTLY_ACIDIC", "hazard": False}
            positive_indicators.append(f"Soil pH ({ph_val:.2f}) is moderately acidic, well-suited for pulses, tea, and potato.")
            chemical_scores.append(85.0)
        elif ph_val <= 7.5:
            chemical_status["pH"] = {"value": ph_val, "classification": "NEUTRAL", "hazard": False}
            positive_indicators.append(f"Soil pH ({ph_val:.2f}) is in the ideal neutral availability zone (6.5 - 7.5).")
            chemical_scores.append(100.0)
        elif ph_val <= 8.5:
            chemical_status["pH"] = {"value": ph_val, "classification": "SLIGHTLY_ALKALINE", "hazard": False}
            positive_indicators.append(f"Soil pH ({ph_val:.2f}) is moderately alkaline (typical vertisol/calcareous).")
            chemical_scores.append(80.0)
        else:
            chemical_status["pH"] = {"value": ph_val, "classification": "STRONGLY_ALKALINE_SODIC", "hazard": True}
            limiting_factors.append(f"Soil is strongly alkaline/sodic (pH {ph_val:.2f} > 8.5), causing structural dispersion and micronutrient lockup.")
            recommended_improvements.append("Apply agricultural gypsum (CaSO4.2H2O) @ 2.5-5.0 t/ha followed by fresh-water leaching.")
            chemical_scores.append(35.0)
            detected_constraints.append({
                "constraint_id": "SC-003",
                "name": "Alkalinity & Sodic Hazard",
                "severity": "CRITICAL",
                "value": ph_val,
                "remediation": "Apply gypsum and incorporate Sesbania green manure."
            })

    if ec_val is not None:
        if ec_val <= 1.0:
            chemical_status["EC"] = {"value": ec_val, "classification": "NON_SALINE", "hazard": False, "unit": "dS/m"}
            positive_indicators.append(f"Electrical conductivity ({ec_val:.2f} dS/m) indicates non-saline soil with no osmotic germination barrier.")
            chemical_scores.append(100.0)
        elif ec_val <= 2.0:
            chemical_status["EC"] = {"value": ec_val, "classification": "SLIGHTLY_SALINE", "hazard": False, "unit": "dS/m"}
            limiting_factors.append(f"Mild salinity detected ({ec_val:.2f} dS/m). Sensitive crops may show yield depression.")
            chemical_scores.append(70.0)
        else:
            chemical_status["EC"] = {"value": ec_val, "classification": "SALINITY_HAZARD", "hazard": True, "unit": "dS/m"}
            limiting_factors.append(f"Saline soil hazard ({ec_val:.2f} dS/m > 2.0 dS/m) causing root osmotic stress.")
            recommended_improvements.append("Ensure sub-surface drainage, leach salts using fresh canal water, and avoid saline tube-well irrigation.")
            chemical_scores.append(40.0)
            detected_constraints.append({
                "constraint_id": "SC-004",
                "name": "Salinity Osmotic Stress",
                "severity": "HIGH",
                "value": ec_val,
                "remediation": "Flush rootzone salts with non-saline water and select salt-tolerant crops (Barley/Mustard/Cotton)."
            })

    # 3. Organic Matter (Organic Carbon)
    om_score = 70.0
    om_status: Dict[str, Any] = {}
    if oc_val is not None:
        if oc_val < 0.50:
            om_status = {"value": oc_val, "classification": "DEPLETED", "unit": "%"}
            limiting_factors.append(f"Soil Organic Carbon is depleted ({oc_val:.2f}% < 0.50%), compromising microbial activity and drought buffer.")
            recommended_improvements.append("Apply 5-10 tonnes/ha farmyard manure or vermicompost; mandate crop residue retention and cover crops.")
            om_score = 45.0
            detected_constraints.append({
                "constraint_id": "SC-001",
                "name": "Soil Organic Carbon Depletion",
                "severity": "HIGH",
                "value": oc_val,
                "remediation": "Incorporate FYM/compost, eliminate crop burning, and introduce legume cover cropping."
            })
        elif oc_val <= 0.75:
            om_status = {"value": oc_val, "classification": "MODERATE", "unit": "%"}
            positive_indicators.append(f"Soil Organic Carbon ({oc_val:.2f}%) is moderate; continue organic replenishment.")
            om_score = 80.0
        else:
            om_status = {"value": oc_val, "classification": "HEALTHY", "unit": "%"}
            positive_indicators.append(f"Soil Organic Carbon ({oc_val:.2f}%) is in the high regenerative range (>0.75%).")
            om_score = 98.0

    # 4. Micronutrients Evaluation
    micronutrient_status: Dict[str, Any] = {}
    micros = [
        ("Zn", zn_val, 0.60, "Zinc", "SC-005", "Apply Zinc Sulphate @ 25 kg/ha or foliar spray @ 0.5%"),
        ("B", b_val, 0.50, "Boron", "SC-006", "Soil apply Borax @ 10 kg/ha or foliar Solubor @ 0.2% before flowering"),
        ("Fe", fe_val, 4.50, "Iron", None, "Apply Ferrous Sulphate foliar spray @ 0.5% with citric acid"),
        ("Mn", mn_val, 2.00, "Manganese", None, "Apply Manganese Sulphate foliar spray @ 0.5%"),
        ("Cu", cu_val, 0.20, "Copper", None, "Apply Copper Sulphate @ 5 kg/ha in deficient soils"),
        ("S", s_val, 10.0, "Sulphur", None, "Apply Gypsum @ 200 kg/ha or elemental sulphur for oilseeds/pulses")
    ]
    for sym, val, crit, name, constr_id, remedy in micros:
        if val is not None:
            if val < crit:
                micronutrient_status[sym] = {"value": val, "status": "DEFICIENT", "critical_limit": crit, "unit": "ppm"}
                limiting_factors.append(f"Available {name} ({sym}) is deficient ({val:.2f} ppm < critical limit {crit} ppm)")
                recommended_improvements.append(remedy)
                if constr_id:
                    detected_constraints.append({
                        "constraint_id": constr_id,
                        "name": f"{name} Deficiency Stress",
                        "severity": "MEDIUM",
                        "value": val,
                        "remediation": remedy
                    })
            else:
                micronutrient_status[sym] = {"value": val, "status": "ADEQUATE", "critical_limit": crit, "unit": "ppm"}

    # Moisture indicator if supplied
    if moisture_val is not None:
        if moisture_val < 15.0:
            limiting_factors.append(f"Current soil moisture is low ({moisture_val:.1f}%), indicating high irrigation requirement.")
        elif moisture_val >= 25.0:
            positive_indicators.append(f"Soil moisture ({moisture_val:.1f}%) is favorable for active root uptake.")

    # Composite Soil Health Score Calculation
    sub_scores = []
    if nutrient_scores:
        sub_scores.append(sum(nutrient_scores) / len(nutrient_scores))
    if chemical_scores:
        sub_scores.append(sum(chemical_scores) / len(chemical_scores))
    sub_scores.append(om_score)

    base_score = sum(sub_scores) / len(sub_scores) if sub_scores else 60.0
    
    # Penalize for critical constraints
    critical_count = sum(1 for c in detected_constraints if c.get("severity") == "CRITICAL")
    high_count = sum(1 for c in detected_constraints if c.get("severity") == "HIGH")
    adjusted_score = max(10.0, min(99.0, base_score - (critical_count * 15.0) - (high_count * 8.0)))

    # Classification status
    if adjusted_score >= 80.0:
        overall_status = "OPTIMAL"
    elif adjusted_score >= 60.0:
        overall_status = "SUB_OPTIMAL"
    elif adjusted_score >= 40.0:
        overall_status = "DEGRADED"
    else:
        overall_status = "CRITICAL"

    # Data confidence
    confidence_score = min(1.0, (provided_core / total_core) * 0.8 + (len(micronutrient_status) / 6.0) * 0.2)
    if confidence_score >= 0.8:
        conf_level = "HIGH"
    elif confidence_score >= 0.5:
        conf_level = "MEDIUM"
    else:
        conf_level = "LOW"

    return {
        "status": overall_status,
        "score": round(adjusted_score, 1),
        "confidence": round(confidence_score, 2),
        "confidence_level": conf_level,
        "component_scores": {
            "macronutrients": round(sum(nutrient_scores) / len(nutrient_scores), 1) if nutrient_scores else None,
            "chemical_balance": round(sum(chemical_scores) / len(chemical_scores), 1) if chemical_scores else None,
            "organic_matter": round(om_score, 1)
        },
        "nutrient_status": nutrient_status,
        "chemical_properties": chemical_status,
        "organic_matter": om_status,
        "micronutrient_status": micronutrient_status,
        "soil_constraints": detected_constraints,
        "limiting_factors": limiting_factors,
        "positive_indicators": positive_indicators,
        "recommended_improvement_areas": list(dict.fromkeys(recommended_improvements)),
        "soil_type_context": soil_type,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
