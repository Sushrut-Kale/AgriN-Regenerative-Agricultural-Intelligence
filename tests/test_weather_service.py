"""
FarmFriend AI — Real-Time Weather Service Test Suite
=====================================================

Tests live real-time weather fetching and fallback behavior.
"""

import pytest
from backend.app.services.weather_service import fetch_live_weather, get_district_info


def test_district_info_lookup():
    info = get_district_info("Parbhani")
    assert info["name"] == "Parbhani"
    assert info["region"] == "Marathwada"
    assert info["lat"] == 19.26

    pune_info = get_district_info("Pune")
    assert pune_info["name"] == "Pune"


def test_fetch_live_weather_parbhani():
    res = fetch_live_weather("Parbhani")
    assert "district" in res
    assert res["district"] == "Parbhani"
    assert "temperature" in res
    assert "humidity" in res
    assert "rainfall" in res
    assert res["temperature"] > 0
    assert res["humidity"] > 0
