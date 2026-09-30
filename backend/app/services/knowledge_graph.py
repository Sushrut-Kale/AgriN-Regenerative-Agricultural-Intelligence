"""
AgriN Lightweight Agricultural Knowledge Graph & Provenance Layer
===================================================================
A lightweight agronomic relationship graph linking:
Crop <---> Soil Requirements <---> Weather Limits <---> Risks <---> Regenerative Practices

Source-Aware AI Reasoning (Requirement 17):
Constructs fully traceable rationale:
OBSERVATION + RULE / MODEL + KNOWLEDGE SOURCE = RECOMMENDATION
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class AgriculturalKnowledgeGraph:
    """Lightweight relationship and provenance traversal layer."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent / "knowledge"
        self._crop_requirements: Dict[str, Any] = {}
        self._soil_standards: Dict[str, Any] = {}
        self._regenerative_practices: List[Dict[str, Any]] = []
        self._sources_registry: Dict[str, Any] = {}
        self._load_knowledge()

    def _load_knowledge(self):
        # 1. Crop requirements
        cr_path = self.base_dir / "crop_requirements.json"
        if cr_path.exists():
            try:
                with open(cr_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._crop_requirements = data.get("crops", {})
            except Exception:
                pass

        # 2. Soil standards
        sh_path = self.base_dir / "soil_health_standards.json"
        if sh_path.exists():
            try:
                with open(sh_path, "r", encoding="utf-8") as f:
                    self._soil_standards = json.load(f)
            except Exception:
                pass

        # 3. Regenerative practices
        rp_path = self.base_dir / "regenerative_practices.json"
        if rp_path.exists():
            try:
                with open(rp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._regenerative_practices = data if isinstance(data, list) else data.get("practices", [])
            except Exception:
                pass

        # 4. Sources registry
        src_path = self.base_dir / "knowledge_sources.json"
        if src_path.exists():
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    self._sources_registry = json.load(f)
            except Exception:
                pass

    def get_crop_relationships(self, crop_name: str) -> Dict[str, Any]:
        """
        Extracts multi-dimensional biophysical requirements and linked practices for a crop.
        """
        c_key = crop_name.lower().strip()
        crop_data = self._crop_requirements.get(c_key, {})
        
        # Link regenerative practices where this crop is relevant or compatible
        matched_practices = []
        for p in self._regenerative_practices:
            ctx = p.get("crop_context", [])
            if any(c_key in str(item).lower() for item in ctx) or "all" in str(ctx).lower():
                matched_practices.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "category": p.get("category"),
                    "objective": p.get("expected_objective")
                })

        # Water requirement estimation
        water_req = "Medium (600 - 900 mm)"
        if c_key in ["rice", "sugarcane", "banana"]:
            water_req = "High (1200 - 2000 mm)"
        elif c_key in ["sorghum", "pearl_millet", "chickpea", "mustard"]:
            water_req = "Low (350 - 550 mm)"

        return {
            "crop": crop_name,
            "scientific_name": crop_data.get("scientific_name", "Unknown"),
            "category": crop_data.get("category", "Field Crop"),
            "suitable_soil": {
                "preferred_types": crop_data.get("soil", {}).get("preferred_types", ["Loam", "Clay Loam"]),
                "ph_optimal_range": [
                    crop_data.get("ph", {}).get("optimal_min", 6.0),
                    crop_data.get("ph", {}).get("optimal_max", 7.5)
                ]
            },
            "climate_range": {
                "temp_optimal": [
                    crop_data.get("temperature", {}).get("optimal_min", 20.0),
                    crop_data.get("temperature", {}).get("optimal_max", 32.0)
                ],
                "rainfall_annual_mm": crop_data.get("rainfall", {}).get("min", 500)
            },
            "seasons": crop_data.get("seasons", {}).get("general", ["Kharif"]),
            "water_requirement": water_req,
            "risks": [
                "Terminal drought stress during pod-filling or flowering",
                "Foliar fungal pathogens under high humidity (>85% RH)",
                "Waterlogging susceptibility in heavy clay depressions"
            ],
            "linked_regenerative_practices": matched_practices[:3]
        }

    def get_soil_condition_relationships(self, condition: str) -> Dict[str, Any]:
        """Maps an edaphic condition (e.g. salinity, acidity, low_oc) to affected crops and remediation."""
        c = condition.lower()
        if "salin" in c or "ec" in c:
            return {
                "condition": "Soil Salinity (Elevated EC)",
                "affected_crops": ["Pulses (Pigeonpea, Chickpea)", "Vegetables", "Maize"],
                "salt_tolerant_alternatives": ["Barley", "Mustard", "Cotton", "Sorghum"],
                "remediation": "Improve subsoil drainage, leach rootzone with non-saline water, avoid KCl fertilizers.",
                "evidence_source": "ICAR-CSSRI Karnal Guidelines",
                "risk_category": "SOIL_RISK"
            }
        elif "acid" in c or "low_ph" in c:
            return {
                "condition": "Soil Acidity (pH < 5.5)",
                "affected_crops": ["Alfalfa", "Legumes (failed Rhizobium nodulation)", "Wheat"],
                "acid_tolerant_alternatives": ["Tea", "Rice", "Cassava", "Potato"],
                "remediation": "Apply agricultural lime (calcium carbonate) or dolomite based on buffer lime test.",
                "evidence_source": "ICAR Soil Acidity Management Protocol",
                "risk_category": "SOIL_RISK"
            }
        else:
            return {
                "condition": "Soil Organic Carbon Depletion (OC < 0.5%)",
                "affected_crops": ["All primary field crops face reduced nutrient-use efficiency"],
                "salt_tolerant_alternatives": [],
                "remediation": "Apply farmyard manure (FYM), incorporate cover crops, and practice zero-tillage residue retention.",
                "evidence_source": "CRIDA / ICAR Soil Health Mission",
                "risk_category": "SOIL_RISK"
            }

    def get_soil_constraint_regenerative_relationships(self, constraint: str) -> Dict[str, Any]:
        """Maps an agronomic soil constraint to validated regenerative practices and sources."""
        c = constraint.lower()
        if "salin" in c or "ec" in c:
            return {
                "constraint": "Soil Salinity / Elevated EC",
                "recommended_practices": ["Subsurface Drainage", "Green Manuring with Dhaincha (Sesbania aculeata)", "Gypsum / Leaching"],
                "mechanism": "Leaches soluble sodium salts below root zone and enhances soil porosity",
                "evidence_source": "ICAR-CSSRI Karnal Guidelines",
                "time_horizon": "Seasonal"
            }
        elif "acid" in c or "ph" in c:
            return {
                "constraint": "Soil Acidity / Low Base Saturation",
                "recommended_practices": ["Agricultural Liming (CaCO3)", "Biochar Application", "Wood Ash Amendment"],
                "mechanism": "Neutralizes toxic exchangeable aluminum (Al3+) and increases phosphorus bioavailability",
                "evidence_source": "ICAR Central Agricultural University Acidity Protocols",
                "time_horizon": "Seasonal"
            }
        else:
            return {
                "constraint": "Organic Carbon Depletion",
                "recommended_practices": ["Cover Cropping (Sunnhemp / Cowpea)", "In-situ Crop Residue Retention", "Farmyard Manure / Vermicompost"],
                "mechanism": "Builds humic fractions, feeds mycorrhizal fungi, and increases water holding capacity",
                "evidence_source": "CRIDA / ICAR Soil Health Mission",
                "time_horizon": "Long-Term"
            }

    def get_weather_risk_relationships(self, condition: str) -> Dict[str, Any]:
        """Maps an extreme or limiting weather condition to specific agricultural risks."""
        w = condition.lower()
        if "heat" in w or "temp" in w or "hot" in w:
            return {
                "weather_condition": "High Temperature (> 38°C)",
                "risk_type": "HEAT_STRESS",
                "impact": "Pollen sterility, accelerated anthesis, elevated canopy vapor-pressure deficit (VPD)",
                "vulnerable_crops": ["Wheat", "Mustard", "Chickpea", "Tomato"],
                "mitigation": "Protective light micro-sprinkler irrigation, straw mulching to buffer soil temperature",
                "evidence_source": "IMD Agromet Advisory Service"
            }
        elif "drought" in w or "dry" in w or "deficit" in w:
            return {
                "weather_condition": "Prolonged Dry Spell / Rainfall Deficit",
                "risk_type": "DROUGHT_DEFICIT",
                "impact": "Stomatal closure, reduced photosynthetic carbon assimilation, premature leaf senescence",
                "vulnerable_crops": ["Maize", "Cotton", "Soybean", "Rice"],
                "mitigation": "Foliar spray of 1% potassium nitrate (KNO3) or anti-transpirants, life-saving drip irrigation",
                "evidence_source": "CRIDA Dryland Agriculture Compendium"
            }
        else:
            return {
                "weather_condition": "Heavy Precipitation / Inundation",
                "risk_type": "WATERLOGGING_EXCESS",
                "impact": "Root hypoxia, iron toxicity, ethylene accumulation, nitrogen denitrification",
                "vulnerable_crops": ["Cotton", "Maize", "Pulses", "Sesame"],
                "mitigation": "Broad-bed and furrow (BBF) drainage, opening ridge furrows to clear stagnant standing water",
                "evidence_source": "ICAR-IARI Agronomy Division"
            }

    def get_risk_advisory_relationships(self, risk_type: str) -> Dict[str, Any]:
        """Maps an agricultural risk type to a concrete agronomic advisory action."""
        r = risk_type.upper()
        if "HEAT" in r:
            return {
                "risk_type": "HEAT_STRESS",
                "advisory": "Apply light evening irrigation or activate micro-sprinklers to suppress canopy temperature by 2-3°C.",
                "urgency": "IMMEDIATE",
                "evidence_source": "IMD Agromet / ICAR-IARI"
            }
        elif "DROUGHT" in r:
            return {
                "risk_type": "DROUGHT_DEFICIT",
                "advisory": "Apply organic biomass mulch (5 t/ha) across crop inter-rows to curtail evaporative soil moisture loss.",
                "urgency": "IMMEDIATE",
                "evidence_source": "CRIDA Rainfed Technologies"
            }
        elif "WATERLOGGING" in r:
            return {
                "risk_type": "WATERLOGGING_EXCESS",
                "advisory": "Dig emergency field drainage channels to evacuate surface water within 24-48 hours to avert root asphyxiation.",
                "urgency": "IMMEDIATE",
                "evidence_source": "ICAR Agronomy Advisory"
            }
        else:
            return {
                "risk_type": "SOIL_CONSTRAINT",
                "advisory": "Adopt regenerative crop rotation incorporating short-duration nitrogen-fixing pulse legumes.",
                "urgency": "SEASONAL",
                "evidence_source": "ICAR-DAC&FW Soil Health Scheme"
            }

    def build_source_aware_trace(
        self,
        observation_name: str,
        observation_value: Any,
        rule_description: str,
        recommendation: str,
        source_key: str = "ICAR-DAC&FW"
    ) -> Dict[str, Any]:
        """
        Requirement 17: Constructs a fully traceable reasoning rationale:
        OBSERVATION + RULE / MODEL + KNOWLEDGE SOURCE = RECOMMENDATION
        """
        source_meta = self._sources_registry.get(source_key, {
            "name": source_key,
            "type": "AGRONOMIC_STANDARD",
            "coverage": "National",
            "evidence_level": "HIGH"
        })

        return {
            "trace_id": f"trace-{abs(hash(observation_name + str(observation_value))) % 1000000:06d}",
            "observation": {
                "parameter": observation_name,
                "measured_value": observation_value
            },
            "rule_evaluated": rule_description,
            "knowledge_source": {
                "name": source_meta.get("name", source_key),
                "type": source_meta.get("type", "AGRONOMIC_REFERENCE"),
                "coverage": source_meta.get("coverage", "India"),
                "evidence_level": source_meta.get("evidence_level", "HIGH")
            },
            "recommendation": recommendation,
            "full_chain": f"[{observation_name}: {observation_value}] -> Rule: '{rule_description}' [Source: {source_meta.get('name', source_key)}] -> Yields Recommendation: '{recommendation}'"
        }



# Singleton instance
knowledge_graph = AgriculturalKnowledgeGraph()
