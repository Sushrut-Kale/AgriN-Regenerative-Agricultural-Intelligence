"""
FarmFriend AI — Integration Tests for FastAPI Endpoints & DB Persistence
===========================================================================
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.database.db import get_db, Base, engine

client = TestClient(app)


# Ensure DB tables exist before running tests
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def sample_payload():
    return {
        "farm_data": {
            "state": "Maharashtra",
            "district": "nashik",
            "season": "kharif",
            "soil_type": "black",
            "irrigation_available": "yes",
            "drainage": "good"
        },
        "soil_data": {
            "N": 280.0, "P": 22.0, "K": 210.0, "S": 14.0,
            "Zn": 0.9, "Fe": 6.5, "Cu": 0.5, "Mn": 3.2, "B": 0.7,
            "ph": 6.8, "EC": 0.4, "OC": 0.65
        },
        "env_data": {
            "temperature": 27.5,
            "humidity": 65.0,
            "rainfall": 850.0
        }
    }


def test_root_and_health():
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "running"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"


def test_reference_data_and_crops():
    res_ref = client.get("/api/reference-data")
    assert res_ref.status_code == 200
    data_ref = res_ref.json()
    assert "districts" in data_ref
    assert "seasons" in data_ref

    res_crops = client.get("/api/crops")
    assert res_crops.status_code == 200
    data_crops = res_crops.json()
    assert data_crops["total"] >= 22
    assert len(data_crops["crops"]) >= 22


def test_validate_endpoint(sample_payload):
    res = client.post("/api/validate", json=sample_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["is_valid"] is True
    assert len(body["errors"]) == 0


def test_analyze_endpoint_and_db_persistence(sample_payload):
    # Fetch initial analytics
    res_analytics_before = client.get("/api/analytics").json()
    count_before = res_analytics_before.get("total_analyses", 0)

    # Run analysis
    res = client.post("/api/analyze", json=sample_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "session_id" in body
    assert len(body["ranked_crops"]) == 10
    assert "recommendation_explanation" in body

    # Fetch updated analytics to verify DB persistence
    res_analytics_after = client.get("/api/analytics").json()
    count_after = res_analytics_after.get("total_analyses", 0)
    assert count_after == count_before + 1


def test_feasibility_endpoint_and_db_persistence(sample_payload):
    res_analytics_before = client.get("/api/analytics").json()
    count_before = res_analytics_before.get("total_feasibility_checks", 0)

    feasibility_payload = {
        **sample_payload,
        "chosen_crop": "cotton"
    }
    res = client.post("/api/feasibility", json=feasibility_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["crop"] == "cotton"
    assert "feasibility_outcome" in body
    assert "feasibility_explanation" in body

    res_analytics_after = client.get("/api/analytics").json()
    count_after = res_analytics_after.get("total_feasibility_checks", 0)
    assert count_after == count_before + 1


def test_whatif_endpoint_and_db_persistence(sample_payload):
    res_analytics_before = client.get("/api/analytics").json()
    count_before = res_analytics_before.get("total_whatif_runs", 0)

    whatif_payload = {
        "crop_name": "soybean",
        "original_soil": sample_payload["soil_data"],
        "original_env": sample_payload["env_data"],
        "farm_data": sample_payload["farm_data"],
        "simulated_changes": {"N": 350.0, "rainfall": 1000.0}
    }
    res = client.post("/api/whatif", json=whatif_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["is_simulation"] is True
    assert body["crop"] == "soybean"
    assert "before" in body
    assert "after" in body
    assert "explanation" in body

    res_analytics_after = client.get("/api/analytics").json()
    count_after = res_analytics_after.get("total_whatif_runs", 0)
    assert count_after == count_before + 1


def test_explain_endpoints(sample_payload):
    analyze_res = client.post("/api/analyze", json=sample_payload).json()
    top_crop = analyze_res["ranked_crops"][0]

    res_explain = client.post("/api/explain", json={
        "crop_result": top_crop,
        "explanation_type": "crop_detail"
    })
    assert res_explain.status_code == 200
    assert res_explain.json()["success"] is True
    assert "explanation" in res_explain.json()

    res_qa = client.post("/api/explain/qa", json={
        "question_type": "why_recommended",
        "crop_result": top_crop,
        "context": {"rank": 1}
    })
    assert res_qa.status_code == 200
    assert res_qa.json()["success"] is True
    assert "answer" in res_qa.json()



def test_model_info():
    res = client.get("/api/model-info")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "model_info" in body
    assert "feature_importance" in body
