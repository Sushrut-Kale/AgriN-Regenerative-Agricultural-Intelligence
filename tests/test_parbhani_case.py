"""
FarmFriend AI — Parbhani Kharif Test Suite & Validation
=========================================================

Verifies dynamic, data-driven analysis for the Parbhani Kharif test case:
- Location: Parbhani, Maharashtra
- Season: Kharif
- Soil: Black soil (Vertisol)
- Irrigation: Limited / Rainfed
- Rainfall: 700 mm | Temp: 28°C | Humidity: 65%
- Soil test: N=280, P=18, K=310, S=14, Zn=0.55, Fe=5.2, Cu=0.45, Mn=4.8, B=0.48, pH=6.8, EC=0.42, OC=0.62
"""

import pytest
from backend.app.services.crop_prediction import get_ranked_crops
from backend.app.services.feasibility import analyze_farmer_chosen_crop
from backend.app.services.what_if import run_whatif


@pytest.fixture
def parbhani_inputs():
    return {
        "farm_data": {
            "state": "Maharashtra",
            "district": "Parbhani",
            "season": "kharif",
            "soil_type": "heavy_black",
            "irrigation_available": "no",
            "drainage": "good"
        },
        "soil_data": {
            "N": 280, "P": 18, "K": 310, "S": 14, "Zn": 0.55,
            "Fe": 5.2, "Cu": 0.45, "Mn": 4.8, "B": 0.48,
            "ph": 6.8, "EC": 0.42, "OC": 0.62
        },
        "env_data": {
            "temperature": 28.0,
            "humidity": 65.0,
            "rainfall": 700.0
        }
    }


def test_parbhani_cotton_feasibility(parbhani_inputs):
    res = analyze_farmer_chosen_crop(
        chosen_crop="cotton",
        soil_data=parbhani_inputs["soil_data"],
        env_data=parbhani_inputs["env_data"],
        farm_data=parbhani_inputs["farm_data"]
    )
    # Score for Kharif Cotton in Parbhani with 700mm seasonal rain and K=310 should be suitable/moderate
    assert res["final_score"] >= 50.0
    assert res["crop"] == "cotton"
    # Ensure 700mm rainfall for Cotton is recognized as suitable / non-excess with good drainage
    rainfall_factor = next((f for f in res["supporting_factors"] + res["moderate_factors"] if f["factor"] == "Rainfall"), None)
    assert rainfall_factor is not None
    assert "exceeds optimal" not in rainfall_factor["note"].lower() or "mitigates" in rainfall_factor["note"].lower()


def test_parbhani_ranking_diversity(parbhani_inputs):
    res = get_ranked_crops(
        soil_data=parbhani_inputs["soil_data"],
        env_data=parbhani_inputs["env_data"],
        farm_data=parbhani_inputs["farm_data"],
        top_n=10
    )
    ranked = res["ranked_crops"]
    assert len(ranked) == 10
    # Make sure scores are dynamically calculated and not identical across all crops
    scores = [r["final_score"] for r in ranked]
    assert len(set(scores)) > 3


def test_whatif_state_isolation(parbhani_inputs):
    sim = run_whatif(
        crop_name="cotton",
        original_soil=parbhani_inputs["soil_data"],
        original_env=parbhani_inputs["env_data"],
        farm_data=parbhani_inputs["farm_data"],
        simulated_changes={"K": 450.0}
    )
    assert sim["is_simulation"] is True
    assert sim["changed_params"]["K"]["before"] == 310
    assert sim["changed_params"]["K"]["after"] == 450.0
    # Original input dictionary must remain pristine
    assert parbhani_inputs["soil_data"]["K"] == 310
