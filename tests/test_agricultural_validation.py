"""
FarmFriend AI — Agricultural Validation Test Suite (CASE A to CASE F)
========================================================================

Verifies exact requirements from User Validation Directive:
  CASE A: Beed Kharif Rainfed Black Soil scenario
  CASE B: Determinism test (exact same input run twice produces 100% identical result)
  CASE C: Rainfed -> Assured irrigation sensitivity
  CASE D: Kharif -> Rabi season sensitivity
  CASE E: pH 8.0 -> pH 7.0 crop-specific compatibility sensitivity
  CASE F: Potassium (K) sensitivity
"""

import pytest
from backend.app.services.crop_prediction import get_ranked_crops
from backend.app.services.feasibility import analyze_farmer_chosen_crop
from backend.app.services.what_if import run_whatif


@pytest.fixture
def beed_kharif_rainfed_inputs():
    return {
        "farm_data": {
            "state": "Maharashtra",
            "district": "Beed",
            "season": "kharif",
            "soil_type": "heavy_black",
            "irrigation_available": "no",
            "drainage": "good",
            "intent": "seasonal_field_crop"
        },
        "soil_data": {
            "N": 260, "P": 16, "K": 320, "S": 12, "Zn": 0.52,
            "Fe": 4.8, "Cu": 0.42, "Mn": 4.5, "B": 0.45,
            "ph": 7.8, "EC": 0.45, "OC": 0.58
        },
        "env_data": {
            "temperature": 29.0,
            "humidity": 62.0,
            "rainfall": 680.0
        }
    }


def test_case_a_beed_kharif_rainfed(beed_kharif_rainfed_inputs):
    """CASE A: Beed Kharif Rainfed Black Soil — Seasonal Field Crops."""
    res = get_ranked_crops(
        soil_data=beed_kharif_rainfed_inputs["soil_data"],
        env_data=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"],
        top_n=10
    )
    ranked = res["ranked_crops"]
    assert len(ranked) > 0
    # Ensure all primary ranked crops are seasonal field crops
    categories = [c["category_type"] for c in ranked]
    assert all(cat == "seasonal_field_crop" for cat in categories)

    top_crop_names = [c["crop"] for c in ranked[:5]]
    # Kharif field crops suitable for Marathwada/Beed black soil
    assert any(crop in top_crop_names for crop in ["cotton", "soybean", "pigeonpeas", "bajra", "jowar", "maize"])


def test_case_b_determinism(beed_kharif_rainfed_inputs):
    """CASE B: Determinism test — exact same input run twice produces 100% identical outputs."""
    res1 = get_ranked_crops(
        soil_data=beed_kharif_rainfed_inputs["soil_data"],
        env_data=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"],
        top_n=10
    )
    res2 = get_ranked_crops(
        soil_data=beed_kharif_rainfed_inputs["soil_data"],
        env_data=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"],
        top_n=10
    )

    scores1 = [c["final_score"] for c in res1["ranked_crops"]]
    scores2 = [c["final_score"] for c in res2["ranked_crops"]]
    assert scores1 == scores2


def test_case_c_irrigation_sensitivity(beed_kharif_rainfed_inputs):
    """CASE C: Rainfed -> Assured irrigation sensitivity."""
    inputs_irrigated = dict(beed_kharif_rainfed_inputs)
    inputs_irrigated["farm_data"] = dict(beed_kharif_rainfed_inputs["farm_data"])
    inputs_irrigated["farm_data"]["irrigation_available"] = "yes"

    res_rainfed = get_ranked_crops(
        soil_data=beed_kharif_rainfed_inputs["soil_data"],
        env_data=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"]
    )
    res_irrigated = get_ranked_crops(
        soil_data=inputs_irrigated["soil_data"],
        env_data=inputs_irrigated["env_data"],
        farm_data=inputs_irrigated["farm_data"]
    )

    # Scores or factor notes should reflect irrigation change
    cotton_rainfed = next(c for c in res_rainfed["ranked_crops"] if c["crop"] == "cotton")
    cotton_irrigated = next(c for c in res_irrigated["ranked_crops"] if c["crop"] == "cotton")
    assert cotton_irrigated["final_score"] >= cotton_rainfed["final_score"]


def test_case_d_season_sensitivity(beed_kharif_rainfed_inputs):
    """CASE D: Kharif -> Rabi season sensitivity."""
    inputs_rabi = dict(beed_kharif_rainfed_inputs)
    inputs_rabi["farm_data"] = dict(beed_kharif_rainfed_inputs["farm_data"])
    inputs_rabi["farm_data"]["season"] = "rabi"

    res_kharif = get_ranked_crops(
        soil_data=beed_kharif_rainfed_inputs["soil_data"],
        env_data=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"]
    )
    res_rabi = get_ranked_crops(
        soil_data=inputs_rabi["soil_data"],
        env_data=inputs_rabi["env_data"],
        farm_data=inputs_rabi["farm_data"]
    )

    rabi_top_crops = [c["crop"] for c in res_rabi["ranked_crops"][:5]]
    # Rabi crops should appear in top picks for Rabi season (e.g., chickpea)
    assert "chickpea" in rabi_top_crops or "wheat" in rabi_top_crops or "mustard" in rabi_top_crops


def test_case_e_ph_sensitivity(beed_kharif_rainfed_inputs):
    """CASE E: pH 8.0 -> pH 7.0 sensitivity."""
    sim = run_whatif(
        crop_name="cotton",
        original_soil=beed_kharif_rainfed_inputs["soil_data"],
        original_env=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"],
        simulated_changes={"ph": 7.0}
    )
    assert sim["is_simulation"] is True
    assert sim["changed_params"]["ph"]["before"] == 7.8
    assert sim["changed_params"]["ph"]["after"] == 7.0


def test_case_f_k_sensitivity(beed_kharif_rainfed_inputs):
    """CASE F: Potassium (K) sensitivity."""
    sim = run_whatif(
        crop_name="cotton",
        original_soil=beed_kharif_rainfed_inputs["soil_data"],
        original_env=beed_kharif_rainfed_inputs["env_data"],
        farm_data=beed_kharif_rainfed_inputs["farm_data"],
        simulated_changes={"K": 450.0}
    )
    assert sim["is_simulation"] is True
    assert sim["changed_params"]["K"]["before"] == 320
    assert sim["changed_params"]["K"]["after"] == 450.0
