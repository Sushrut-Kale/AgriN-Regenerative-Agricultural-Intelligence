"""
Phase 3 Agricultural Intelligence Quality and Product Maturity Test Suite.

Validates:
1. Agricultural risk detection & severity hierarchy (CRITICAL, HIGH, MEDIUM, LOW)
2. Decoupling of Data Quality from Biological Farm Resilience
3. Progressive missing-data guidance
4. Multi-candidate crop comparison & pairwise trade-off narratives (no arbitrary winner)
5. Temporal intelligence & farm memory (strict >=2 observations rule)
6. Responsible AI guardrails (no yield/profit guarantees, no fabricated satellite/pathology)
7. Country-neutral machine-readable advisory schema
8. Phase 3 API endpoints (/crops/compare, /knowledge/sources, /knowledge/regenerative-practices, /demo/farms)
9. What-If scenario simulation integrity
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.agricultural_risk_engine import assess_agricultural_risks, generate_prioritized_advisories
from backend.app.services.confidence_engine import assess_data_quality, get_missing_data_guidance
from backend.app.services.crop_comparison import compare_candidate_crops
from backend.app.services.farm_memory import record_farm_observation, get_farm_temporal_trends
from backend.app.services.agrin_intelligence import run_full_agricultural_intelligence

client = TestClient(app)


def test_agricultural_risk_engine_salinity_and_drought():
    soil = {"ph": 8.8, "ec": 4.5, "organic_carbon": 0.25, "nitrogen": 110, "phosphorus": 8, "potassium": 90}
    weather = {"temperature": 41.5, "relative_humidity": 22.0, "rainfall": 0.0}
    farm_data = {"crop": "cotton", "irrigation_available": "no"}
    risks = assess_agricultural_risks(farm_data=farm_data, soil_profile=soil, weather_info=weather)
    
    severities = [r["severity"] for r in risks]
    assert "CRITICAL" in severities or "HIGH" in severities
    
    # Check salinity risk detected with evidence
    salinity_risks = [r for r in risks if "salin" in r["risk"].lower() or "alkali" in r["risk"].lower() or "ec" in r["evidence"].lower()]
    assert len(salinity_risks) > 0
    assert salinity_risks[0]["confidence"] in ["HIGH", "MEDIUM"]
    assert "recommended_action" in salinity_risks[0]
    
    # Prioritized advisories
    advisories = generate_prioritized_advisories(risks=risks, soil_profile=soil)
    assert len(advisories) > 0
    assert advisories[0]["priority"] in ["CRITICAL", "HIGH"]
    assert "trigger" in advisories[0]
    assert "limitations" in advisories[0]


def test_data_quality_decoupled_from_resilience():
    # Complete measurement data for an exhausted/degraded soil
    degraded_soil = {
        "ph": 4.8,
        "ec": 3.2,
        "organic_carbon": 0.2,
        "nitrogen": 90,
        "phosphorus": 6,
        "potassium": 80,
        "state": "Maharashtra",
        "district": "Parbhani",
        "season": "Kharif",
        "irrigation_available": "no"
    }
    
    # Data quality should be HIGH because data is complete, fresh, and standard
    dq = assess_data_quality(degraded_soil, {"temperature": 28.0, "rainfall": 10.0}, {"lat": 19.26, "lon": 76.77})
    assert dq["data_quality_rating"] in ["HIGH", "MEDIUM"]
    assert dq["completeness_pct"] >= 75.0
    
    # Missing data guidance on incomplete profile
    partial_soil = {"ph": 6.5}
    guidance = get_missing_data_guidance(partial_soil)
    assert any("carbon" in p.lower() for p in guidance["missing_parameters"])
    assert "pH" in guidance["known_parameters"]
    assert len(guidance["impact_statement"]) > 0


def test_crop_comparison_and_tradeoffs():
    soil = {"ph": 7.5, "nitrogen": 220, "phosphorus": 22, "potassium": 210, "organic_carbon": 0.65}
    weather = {"temperature": 29.0, "rainfall": 85.0}
    farm_data = {"state": "Maharashtra", "district": "Parbhani", "latitude": 19.26, "longitude": 76.77}
    
    comparison = compare_candidate_crops(["cotton", "soybean", "sorghum"], farm_data, soil, weather)
    assert comparison["status"] == "success"
    assert comparison["total_compared"] == 3
    assert "comparison_matrix" in comparison
    assert "trade_off_analysis" in comparison
    
    # Must contain trade-off explanations without an arbitrary absolute winner
    assert len(comparison["trade_off_analysis"]["pairwise_trade_offs"]) >= 2
    assert "AgriN does not pick an absolute winner" in comparison["trade_off_analysis"]["disclaimer"]


def test_temporal_intelligence_minimum_observations_rule():
    farm_id = "test-temporal-farm-001"
    
    # Single observation must return insufficient history
    record_farm_observation(farm_id, {"ph": 7.0, "organic_carbon": 0.5, "ec": 1.0, "resilience_score": 55})
    trends_1 = get_farm_temporal_trends(farm_id)
    assert trends_1["status"] == "insufficient_history"
    assert "minimum of 2 chronological observations" in trends_1["rule"]
    
    # Second observation: diverging pH, improving organic carbon
    record_farm_observation(farm_id, {"ph": 8.5, "organic_carbon": 0.8, "ec": 1.0, "resilience_score": 62})
    trends_2 = get_farm_temporal_trends(farm_id)
    assert trends_2["status"] == "trend_computed"
    assert trends_2["trends"]["soil_ph"]["direction"] == "Declining"
    assert trends_2["trends"]["organic_carbon"]["direction"] == "Improving"
    assert trends_2["trends"]["resilience"]["direction"] == "Improving"


def test_responsible_ai_guardrails_in_unified_report():
    farm_data = {
        "farm_id": "audit-farm-resp-ai",
        "state": "Maharashtra",
        "district": "Nagpur",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "soil": {"ph": 7.8, "organic_carbon": 0.45, "nitrogen": 180.0, "phosphorus": 14.0, "potassium": 240.0},
        "crop": "cotton",
        "irrigation_available": "no"
    }
    
    res = run_full_agricultural_intelligence(farm_data)
    
    # Guardrail 1: Unified report exists and covers 6 canonical sections
    report = res["farm_intelligence_report"]
    assert report is not None
    assert "crop_opportunity" in report
    assert "soil_health" in report
    assert "regenerative_opportunities" in report
    assert "climate_and_weather" in report
    assert "farm_resilience" in report
    assert "data_confidence" in report
    
    # Guardrail 2: Responsible AI Guardrails explicit compliance
    audit = report["audit_and_transparency"]
    assert audit["yield_guarantee_issued"] is False
    assert audit["profit_guarantee_issued"] is False
    assert audit["satellite_observation_linked"] is False
    assert audit["disease_model_linked"] is False
    assert audit["missing_data_imputed"] is False
    
    # Guardrail 3: Machine readable advisory output conforms to country-neutral format
    advisory = res["country_neutral_advisory"]
    assert advisory["advisory_id"].startswith("adv-")
    assert advisory["farm_id"] == "audit-farm-resp-ai"
    assert len(advisory["limitations"]) > 0
    assert "responsible_ai_notice" in advisory


def test_phase3_api_endpoints():
    # 1. Candidate crop comparison endpoint
    payload = {
        "candidate_crops": ["cotton", "soybean", "pigeonpea"],
        "soil_data": {"ph": 7.6, "nitrogen": 200, "phosphorus": 18, "potassium": 220, "organic_carbon": 0.55},
        "env_data": {"temperature": 30.5, "rainfall": 60.0},
        "farm_data": {"state": "Maharashtra", "district": "Yavatmal", "latitude": 20.38, "longitude": 78.12}
    }
    r = client.post("/api/crops/compare", json=payload)
    assert r.status_code == 200
    comp_data = r.json()
    assert comp_data["total_compared"] == 3
    assert len(comp_data["trade_off_analysis"]["pairwise_trade_offs"]) >= 2

    # 2. Knowledge sources registry endpoint
    r = client.get("/api/knowledge/sources")
    assert r.status_code == 200
    sources = r.json()
    assert "CRIDA" in sources or "sources" in sources

    # 3. Regenerative practices knowledge base endpoint
    r = client.get("/api/knowledge/regenerative-practices")
    assert r.status_code == 200
    practices = r.json()
    assert len(practices) >= 8 or "practices" in practices

    # 4. Realistic demo farms endpoint
    r = client.get("/api/demo/farms")
    assert r.status_code == 200
    demo_data = r.json()
    farm_list = demo_data.get("demo_farms", []) if isinstance(demo_data, dict) else demo_data
    assert len(farm_list) >= 5
    for df in farm_list:
        assert df["synthetic"] is True  # Guardrail: synthetic data must be explicitly marked


def test_what_if_scenario_simulation_labeling():
    payload = {
        "crop_name": "cotton",
        "original_soil": {
            "N": 180.0,
            "P": 15.0,
            "K": 200.0,
            "pH": 7.2,
            "EC": 1.2,
            "OC": 0.45
        },
        "original_env": {
            "temperature": 32.0,
            "humidity": 55.0,
            "rainfall": 40.0
        },
        "farm_data": {
            "state": "Maharashtra",
            "district": "Parbhani",
            "soil_type": "Black",
            "season": "Kharif",
            "irrigation_available": "no"
        },
        "simulated_changes": {
            "pH": 7.0,
            "OC": 0.8
        },
        "session_id": "sim-sess-001"
    }
    r = client.post("/api/whatif", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["is_simulation"] is True
    assert "Scenario simulation" in data["disclaimer"]
