"""
FarmFriend AI — Unit Tests for ML, Scorer, and Services
=========================================================
"""

import sys
import os
import pytest

# Ensure project root is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict import predictor
from backend.app.services.validation import (
    validate_farm_inputs, validate_soil_inputs, validate_env_inputs,
    validate_whatif_inputs, count_missing_soil_fields, compute_data_confidence
)
from backend.app.services.suitability_scorer import (
    compute_suitability_score, classify_score
)
from backend.app.services.crop_prediction import get_ranked_crops
from backend.app.services.feasibility import analyze_farmer_chosen_crop
from backend.app.services.what_if import run_whatif


# ── Sample Data Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def sample_farm():
    return {
        "state": "Maharashtra",
        "district": "nashik",
        "season": "kharif",
        "soil_type": "black",
        "irrigation_available": "yes",
        "drainage": "good",
    }


@pytest.fixture
def sample_soil():
    return {
        "N": 280.0, "P": 22.0, "K": 210.0, "S": 14.0,
        "Zn": 0.9, "Fe": 6.5, "Cu": 0.5, "Mn": 3.2, "B": 0.7,
        "ph": 6.8, "EC": 0.4, "OC": 0.65
    }


@pytest.fixture
def sample_env():
    return {
        "temperature": 27.5,
        "humidity": 65.0,
        "rainfall": 850.0
    }


# ── ML Predictor Tests ────────────────────────────────────────────────────────

def test_ml_predictor_load():
    predictor.load()
    assert predictor._loaded is True
    assert predictor.model is not None
    assert len(predictor.label_encoder.classes_) >= 22


def test_ml_predictor_predict_top_crops(sample_soil, sample_env):
    predictor.load()
    ml_inputs = {
        "N": sample_soil["N"],
        "P": sample_soil["P"],
        "K": sample_soil["K"],
        "temperature": sample_env["temperature"],
        "humidity": sample_env["humidity"],
        "ph": sample_soil["ph"],
        "rainfall": sample_env["rainfall"],
    }
    top_crops = predictor.predict_top_crops(ml_inputs, top_n=5)
    assert len(top_crops) == 5
    assert "crop" in top_crops[0]
    assert "ml_probability" in top_crops[0]
    assert top_crops[0]["ml_probability"] >= 0.0


def test_ml_predictor_single_crop(sample_soil, sample_env):
    predictor.load()
    ml_inputs = {
        "N": sample_soil["N"],
        "P": sample_soil["P"],
        "K": sample_soil["K"],
        "temperature": sample_env["temperature"],
        "humidity": sample_env["humidity"],
        "ph": sample_soil["ph"],
        "rainfall": sample_env["rainfall"],
    }
    prob = predictor.predict_single_crop("cotton", ml_inputs)
    assert prob is not None
    assert 0.0 <= prob <= 1.0

    # Non-existent crop
    assert predictor.predict_single_crop("invalid_crop", ml_inputs) is None



# ── Validation Tests ──────────────────────────────────────────────────────────

def test_validate_farm_inputs(sample_farm):
    res = validate_farm_inputs(sample_farm)
    assert res.is_valid is True
    assert len(res.errors) == 0

    # Invalid farm area
    invalid_farm = {**sample_farm, "farm_area": -5}
    res_inv = validate_farm_inputs(invalid_farm)
    assert res_inv.is_valid is False
    assert len(res_inv.errors) == 1


def test_validate_soil_inputs(sample_soil):
    res = validate_soil_inputs(sample_soil)
    assert res.is_valid is True

    # Out of range pH
    invalid_soil = {**sample_soil, "ph": 15.0}
    res_inv = validate_soil_inputs(invalid_soil)
    assert res_inv.is_valid is False


def test_validate_env_inputs(sample_env):
    res = validate_env_inputs(sample_env)
    assert res.is_valid is True

    # Extreme rainfall out of range
    res_inv = validate_env_inputs({**sample_env, "rainfall": 9000.0})
    assert res_inv.is_valid is False


def test_count_missing_soil_fields(sample_soil):
    n_missing, missing = count_missing_soil_fields(sample_soil)
    assert n_missing == 0
    assert len(missing) == 0

    partial = {**sample_soil, "N": None, "P": None}
    n_missing_p, missing_p = count_missing_soil_fields(partial)
    assert n_missing_p == 2
    assert "N" in missing_p and "P" in missing_p


def test_compute_data_confidence(sample_soil, sample_env):
    assert compute_data_confidence(sample_soil, sample_env) == "high"

    empty_soil = {k: None for k in sample_soil}
    assert compute_data_confidence(empty_soil, sample_env) == "low"


# ── Suitability Scorer Tests ──────────────────────────────────────────────────

def test_classify_score():
    assert classify_score(85)[0] == "Highly Suitable"
    assert classify_score(65)[0] == "Suitable"
    assert classify_score(45)[0] == "Moderately Suitable"
    assert classify_score(25)[0] == "Low Suitability"


def test_compute_suitability_score(sample_soil, sample_env, sample_farm):
    res = compute_suitability_score(
        crop_name="soybean",
        ml_probability=0.85,
        soil_data=sample_soil,
        env_data=sample_env,
        farm_data=sample_farm,
        missing_fields=[]
    )
    assert res["crop"] == "soybean"
    assert 0 <= res["final_score"] <= 100
    assert "classification" in res
    assert "supporting_factors" in res
    assert "limiting_factors" in res


# ── Full Pipeline & Services Tests ────────────────────────────────────────────

def test_get_ranked_crops(sample_soil, sample_env, sample_farm):
    res = get_ranked_crops(sample_soil, sample_env, sample_farm, top_n=10)
    assert len(res["ranked_crops"]) == 10
    assert res["ranked_crops"][0]["rank"] == 1
    # Check descending order of scores
    scores = [c["final_score"] for c in res["ranked_crops"]]
    assert scores == sorted(scores, reverse=True)


def test_analyze_farmer_chosen_crop(sample_soil, sample_env, sample_farm):
    res = analyze_farmer_chosen_crop(
        chosen_crop="cotton",
        soil_data=sample_soil,
        env_data=sample_env,
        farm_data=sample_farm
    )
    assert res["crop"] == "cotton"
    assert "feasibility_outcome" in res
    assert "feasibility_explanation" in res


def test_run_whatif(sample_soil, sample_env, sample_farm):
    simulated_changes = {"N": 400.0, "rainfall": 1200.0}
    res = run_whatif(
        crop_name="soybean",
        original_soil=sample_soil,
        original_env=sample_env,
        farm_data=sample_farm,
        simulated_changes=simulated_changes
    )
    assert res["is_simulation"] is True
    assert res["crop"] == "soybean"
    assert "before" in res
    assert "after" in res
    assert "score_change" in res
    assert "explanation" in res
    assert "N" in res["changed_params"]
