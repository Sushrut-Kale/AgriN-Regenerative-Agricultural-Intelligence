"""
FarmFriend AI — Feedback API & Database Test Suite
===================================================
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_submit_recommendation_feedback():
    payload = {
        "session_id": "test-session-123",
        "recommended_crop": "cotton",
        "selected_crop": "cotton",
        "suitability_score": 82.5,
        "rating": "helpful",
        "reason": "Soil match",
        "free_text": "Good recommendation for Parbhani Kharif.",
        "model_version": "random_forest_v2",
        "region": "Parbhani",
        "season": "kharif"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "feedback_id" in data


def test_submit_outcome_feedback():
    payload = {
        "session_id": "test-session-123",
        "recommended_crop": "cotton",
        "outcome_status": "harvested",
        "crop_performance": "good",
        "actual_yield": 18.5,
        "yield_unit": "quintals_per_ha",
        "rating": "helpful"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_feedback_summary_analytics():
    response = client.get("/api/feedback/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_feedback" in data
    assert "helpful_percentage" in data
