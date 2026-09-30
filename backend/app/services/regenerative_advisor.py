"""
AgriN Regenerative Agriculture Advisor
Dedicated service evaluating 8 core regenerative practice classes:
1. Crop Rotation
2. Crop Diversification
3. Cover-Crop Opportunity
4. Soil Organic Matter Improvement
5. Water Conservation
6. Reduced Soil Disturbance
7. Nutrient Management
8. Residue Management

Evaluates farm biophysical state (soil health, water regime, crop history, climate context)
and provides grounded, scientifically backed regenerative plans. Handles missing data honestly.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from backend.app.services.soil_intelligence import assess_soil_health
except ImportError:
    from app.services.soil_intelligence import assess_soil_health

PRACTICES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "knowledge" / "regenerative" / "practices.json"

_cached_practices: Optional[List[Dict[str, Any]]] = None


def load_regenerative_practices() -> List[Dict[str, Any]]:
    global _cached_practices
    if _cached_practices is None:
        if PRACTICES_PATH.exists():
            with open(PRACTICES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _cached_practices = data.get("practices", [])
        else:
            _cached_practices = []
    return _cached_practices


def advise_regenerative_practices(
    farm_data: Dict[str, Any],
    soil_profile: Optional[Dict[str, Any]] = None,
    current_crop: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates farm context and generates prioritized regenerative recommendations across 8 classes.
    
    Parameters:
        farm_data: Farm dictionary containing:
                   - state, district, season, irrigation_available, rainfall, temperature, humidity
                   - soil test metrics (N, P, K, pH, EC, OC, Zn, etc.)
                   - current_crop or previous_crop
        soil_profile: Pre-computed SoilHealthProfile (optional, evaluated if omitted)
        current_crop: Sown or intended crop
    """
    # 1. Check for minimal viable data
    has_location = bool(farm_data.get("state") or farm_data.get("district") or farm_data.get("latitude"))
    has_soil = any(farm_data.get(k) is not None for k in ["OC", "pH", "N", "P", "K", "soil_type"])
    has_water = farm_data.get("irrigation_available") is not None or farm_data.get("rainfall") is not None

    if not has_location and not has_soil and not has_water:
        return {
            "status": "insufficient_data",
            "message": "Insufficient farm profile data to generate scientifically grounded regenerative recommendations.",
            "missing_data_requirements": [
                "Farm location (State or District)",
                "Basic soil parameters (at minimum Organic Carbon % or pH)",
                "Water availability or seasonal rainfall regime"
            ],
            "recommendations": [],
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    # Evaluate soil health if not provided
    if soil_profile is None:
        soil_profile = assess_soil_health(farm_data, soil_type=farm_data.get("soil_type"))

    practices = load_regenerative_practices()
    classified_recs: List[Dict[str, Any]] = []

    # Extract environmental parameters
    oc_val = None
    if farm_data.get("OC") is not None:
        try:
            oc_val = float(farm_data["OC"])
        except (ValueError, TypeError):
            pass

    ph_val = None
    if farm_data.get("pH") is not None:
        try:
            ph_val = float(farm_data["pH"])
        except (ValueError, TypeError):
            pass

    rainfall_val = None
    if farm_data.get("rainfall") is not None:
        try:
            rainfall_val = float(farm_data["rainfall"])
        except (ValueError, TypeError):
            pass

    irrigation_type = str(farm_data.get("irrigation_available", "")).lower()
    is_rainfed = irrigation_type in ["no", "rainfed", "false"]
    crop_name = current_crop or farm_data.get("target_crop") or farm_data.get("crop")

    # --- CLASS 1: CROP ROTATION ---
    if crop_name:
        c_lower = crop_name.lower()
        if c_lower in ["cotton", "rice", "sugarcane", "maize"]:
            classified_recs.append({
                "class": "CROP_ROTATION",
                "title": f"Post-{crop_name.capitalize()} Legume Rotation Sequence",
                "urgency": "HIGH",
                "practice_id": "PRACTICE-001",
                "rationale": f"Continuous monoculture of heavy feeders like {crop_name.capitalize()} depletes soil nitrogen and disrupts sub-soil microbiology. Breaking the cycle with Chickpea, Lentil, or Pigeonpea fixes 30-50 kg/ha atmospheric nitrogen.",
                "actions": [
                    f"Follow {crop_name.capitalize()} with short-duration pulse (Chickpea/Moong/Urad) in the subsequent season.",
                    "Inoculate legume seeds with Rhizobium culture to maximize root nodulation.",
                    "Retain legume root biomass in the soil to enrich root-zone microbial diversity."
                ],
                "expected_benefits": "Natural soil nitrogen replenishment, breaking pest/nematode breeding cycles, improved soil tilth."
            })

    # --- CLASS 2: CROP DIVERSIFICATION ---
    if is_rainfed or (rainfall_val and rainfall_val < 800):
        classified_recs.append({
            "class": "CROP_DIVERSIFICATION",
            "title": "Intercropping & Polyculture Canopy Architecture",
            "urgency": "HIGH" if is_rainfed else "MEDIUM",
            "practice_id": "PRACTICE-005",
            "rationale": "Semi-arid rainfed tracts experience erratic mid-season dry spells. Intercropping a deep-rooted taproot crop with a fibrous root cereal creates resilient canopy cover and reduces drought risk.",
            "actions": [
                "Adopt 1:2 or 2:4 row ratio intercropping (e.g. Cotton + Pigeonpea or Pearl Millet + Green Gram).",
                "Ensure complementary root depths: shallow-feeder cereal with deep-taproot pulse.",
                "Harvest components staggered to optimize moisture and solar radiation capture."
            ],
            "expected_benefits": "Insurance against erratic monsoon failure, enhanced spatial land equivalent ratio (LER > 1.25), suppression of weed seedbeds."
        })

    # --- CLASS 3: COVER-CROP OPPORTUNITY ---
    classified_recs.append({
        "class": "COVER_CROP_OPPORTUNITY",
        "title": "Seasonal Fallow Protection with Short-Duration Cover Crops",
        "urgency": "MEDIUM",
        "practice_id": "PRACTICE-002",
        "rationale": "Leaving soil bare between main cropping seasons accelerates topsoil loss from wind and solar scorching, while degrading root-zone mycorrhizae.",
        "actions": [
            "Broadcast Sunnhemp (Crotalaria juncea) or Cowpea (Vigna unguiculata) @ 25 kg/ha during inter-season windows.",
            "Terminate cover crop at 50% flowering and incorporate into top 10 cm of soil or roll down as mulch.",
            "Allow 10-14 days decomposition period before sowing subsequent main cash crop."
        ],
        "expected_benefits": "Prevents soil crusting, intercepts raindrop impact energy, and adds 15-20 t/ha fresh green biomass."
    })

    # --- CLASS 4: SOIL ORGANIC MATTER IMPROVEMENT ---
    if oc_val is not None and oc_val < 0.75:
        severity = "CRITICAL" if oc_val < 0.50 else "HIGH"
        classified_recs.append({
            "class": "SOIL_ORGANIC_MATTER_IMPROVEMENT",
            "title": "Accelerated Soil Organic Carbon (SOC) Rebuilding Protocol",
            "urgency": severity,
            "practice_id": "PRACTICE-009",
            "rationale": f"Current Soil Organic Carbon is {oc_val:.2f}% (benchmark >= 0.75%). Low organic matter limits microbial respiration, cation exchange capacity (CEC), and moisture holding capacity.",
            "actions": [
                "Apply well-decomposed FYM or enriched compost @ 5-10 tonnes/hectare prior to primary tillage.",
                "Incorporate biochar @ 2-5 t/ha once every 3-5 years to build stable, recalcitrant carbon reservoirs.",
                "Inoculate soil with vesicular arbuscular mycorrhiza (VAM) and Trichoderma bio-agents."
            ],
            "expected_benefits": "Substantial increase in rootzone water retention (1% increase in SOC stores ~150,000 L water/ha) and enhanced fertilizer use efficiency."
        })

    # --- CLASS 5: WATER CONSERVATION ---
    if is_rainfed or (rainfall_val and rainfall_val < 900):
        classified_recs.append({
            "class": "WATER_CONSERVATION",
            "title": "In-situ Moisture Harvesting via Broad Bed Furrow (BBF)",
            "urgency": "HIGH",
            "practice_id": "PRACTICE-004",
            "rationale": "In semi-arid drylands, rain occurs in high-intensity convective showers that cause heavy surface runoff. Broad Bed Furrow systems detain rainwater in furrows, promoting deep percolation.",
            "actions": [
                "Prepare 100-120 cm wide raised beds separated by 30 cm drainage/harvesting furrows along the contour (0.2-0.4% slope).",
                "Sow 2-4 crop rows on the bed, leaving furrows clear for moisture infiltration.",
                "Connect furrow ends to a micro-catchment farm pond for supplemental life-saving irrigation."
            ],
            "expected_benefits": "Reduces runoff velocity by 60%, prevents waterlogging during heavy downpours, and prolongs profile moisture availability by 2-3 weeks."
        })

    # --- CLASS 6: REDUCED SOIL DISTURBANCE ---
    classified_recs.append({
        "class": "REDUCED_SOIL_DISTURBANCE",
        "title": "Conservation Agriculture: Minimum Tillage & Direct Sowing",
        "urgency": "MEDIUM",
        "practice_id": "PRACTICE-003",
        "rationale": "Repeated deep disc ploughing pulverizes soil aggregates, oxidizes organic matter into carbon dioxide, and creates a dense subsoil hardpan.",
        "actions": [
            "Eliminate secondary tillage passes; use a Happy Seeder or Zero-Till drill for direct seed placement.",
            "Restrict tillage to the immediate seeding slot (strip-till) rather than full-field inversion.",
            "Maintain soil surface mulch cover to protect undisturbed earthworm channels and fungal hyphae."
        ],
        "expected_benefits": "Reduces diesel fuel consumption by 40-60%, curtails topsoil erosion, and preserves beneficial soil macro-fauna."
    })

    # --- CLASS 7: NUTRIENT MANAGEMENT ---
    classified_recs.append({
        "class": "NUTRIENT_MANAGEMENT",
        "title": "Integrated Nutrient Management (INM) & Bio-Priming",
        "urgency": "HIGH",
        "practice_id": "PRACTICE-006",
        "rationale": "Exclusive reliance on synthetic chemical fertilizers (Urea + DAP) acidifies or salinizes soil, suppresses mycorrhizae, and causes micronutrient imbalances.",
        "actions": [
            "Adopt the 70:30 formula: 70% nutrients via targeted chemical fertilizers + 30% via organic sources/composts.",
            "Seed treatment with Azotobacter / Azospirillum (nitrogen fixers) and PSB (phosphorus solubilizers) @ 250 g/10 kg seed.",
            "Split nitrogen applications into 3-4 micro-doses guided by leaf color charts (LCC) to avoid volatilization."
        ],
        "expected_benefits": "Improves nutrient uptake efficiency from 35% to 55%, suppresses fertilizer-induced soil acidity/salinity, and reduces input expenditure."
    })

    # --- CLASS 8: RESIDUE MANAGEMENT ---
    classified_recs.append({
        "class": "RESIDUE_MANAGEMENT",
        "title": "Zero-Burn In-Situ Crop Residue Mulching & Bio-Decomposition",
        "urgency": "HIGH",
        "practice_id": "PRACTICE-007",
        "rationale": "Burning straw and stover destroys 100% of organic nitrogen, 75% of phosphorus, and incinerates beneficial topsoil microorganisms.",
        "actions": [
            "Chop and retain crop residues uniformly across the field surface as protective mulch.",
            "Spray ligno-cellulolytic microbial consortium (e.g. Pusa Bio-Decomposer) @ 25 L/ha with 1% urea spray to accelerate field rotting.",
            "Direct-sow into stubble cover using specialized tractor seeders."
        ],
        "expected_benefits": "Prevents air pollution and greenhouse gas emissions, retains 4-5 tonnes/ha organic biomass, and conserves 30% soil moisture."
    })

    # Compute overall regenerative readiness indicators
    return {
        "status": "success",
        "practice_count": len(classified_recs),
        "recommendations": classified_recs,
        "soil_health_summary": {
            "score": soil_profile.get("score"),
            "status": soil_profile.get("status"),
            "constraints_count": len(soil_profile.get("soil_constraints", []))
        },
        "regenerative_dimensions": {
            "soil_organic_matter": "HIGH_NEED" if (oc_val and oc_val < 0.75) else "MAINTENANCE",
            "water_resilience": "HIGH_NEED" if is_rainfed else "MODERATE",
            "crop_diversity": "RECOMMENDED" if crop_name else "EXPLORATORY",
            "residue_stewardship": "CRITICAL"
        },
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
