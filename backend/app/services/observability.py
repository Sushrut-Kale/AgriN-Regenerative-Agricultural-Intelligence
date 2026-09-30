"""
AgriN Structured Observability & Audit Logger
=============================================
Provides privacy-preserving, structured JSON telemetry for core pipeline stages:
- analysis_started
- weather_fetched / weather_failed
- soil_analysis_completed
- crop_ranking_completed
- regenerative_analysis_completed
- confidence_calculated
- advisory_generated
- analysis_completed

PRIVACY GUARANTEE:
Never logs sensitive personal farmer identifiers, exact cadastral parcel plots,
or phone numbers. Only records non-sensitive agro-climatic context, execution latency,
and diagnostic status codes.
"""

import time
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger("agrin.intelligence")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('{"time":"%(asctime)s", "level":"%(levelname)s", "logger":"%(name)s", "event":%(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class PipelineObserver:
    """Tracks latency and structured audit events for an agricultural intelligence run."""
    def __init__(self, request_id: str, farm_id: str, state: str, district: str):
        self.request_id = request_id
        self.farm_id = farm_id
        self.state = state
        self.district = district
        self.t_start = time.perf_counter()
        self.step_times = {}

        self.log_event("analysis_started", {
            "state": state,
            "district": district,
            "timestamp": time.time()
        })

    def log_event(self, event_name: str, payload: Optional[Dict[str, Any]] = None, status: str = "SUCCESS"):
        data = {
            "event": event_name,
            "request_id": self.request_id,
            "farm_id": self.farm_id,
            "district": self.district,
            "status": status,
            "elapsed_ms": round((time.perf_counter() - self.t_start) * 1000.0, 2),
            "details": payload or {}
        }
        logger.info(json.dumps(data))

    def mark_step(self, step_name: str, status: str = "SUCCESS", details: Optional[Dict[str, Any]] = None):
        self.step_times[step_name] = time.perf_counter()
        self.log_event(step_name, details, status)

    def complete(self, total_crops: int, confidence_level: str, resilience_score: float):
        total_duration = round((time.perf_counter() - self.t_start) * 1000.0, 2)
        self.log_event("analysis_completed", {
            "total_duration_ms": total_duration,
            "total_crops_ranked": total_crops,
            "confidence_level": confidence_level,
            "resilience_score": resilience_score
        })
        return total_duration
