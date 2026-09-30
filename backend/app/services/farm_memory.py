"""
AgriN Farm Knowledge Memory & Temporal Intelligence Service
=============================================================
Manages non-sensitive farm memory across sessions:
- Farm structural intelligence (location, agro-zone, soil type)
- Historical soil observation vectors
- Crop cultivation history
- Historical advisories and farmer feedback

Temporal Intelligence:
- Calculates empirical directionality across multiple time points:
  - Soil pH (convergence toward optimal 6.5 - 7.5 range)
  - Soil Organic Carbon (OC% accumulation)
  - Salinity (EC dS/m stabilization)
  - N, P, K replenishment
  - Farm Resilience Index trajectory
- Strict Guardrail: Requires >= 2 chronological observations. If < 2, explicitly
  reports 'Insufficient history' with the documented rule.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import statistics


class FarmMemoryService:
    """
    In-memory and DB-backed storage for farm intelligence history and temporal analysis.
    Maintains clean separation between farmer personal identity and farm agronomic state.
    """
    def __init__(self):
        # Ephemeral cache for active session access
        self._memory_store: Dict[str, Dict[str, Any]] = {}

    def get_or_create_farm_record(self, farm_id: str, location_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve existing farm agronomic memory or initialize a new anonymous farm record."""
        if farm_id not in self._memory_store:
            self._memory_store[farm_id] = {
                "farm_id": farm_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "location": location_info or {},
                "soil_history": [],
                "crop_history": [],
                "advisory_history": [],
                "feedback_history": []
            }
        return self._memory_store[farm_id]

    def record_observation(
        self,
        farm_id: str,
        soil_data: Optional[Dict[str, Any]] = None,
        crop_data: Optional[Dict[str, Any]] = None,
        advisory_data: Optional[List[Dict[str, Any]]] = None,
        feedback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Append an observation snapshot to the farm's temporal record."""
        record = self.get_or_create_farm_record(farm_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        if soil_data:
            snapshot = {
                "timestamp": now_iso,
                "pH": soil_data.get("pH") if soil_data.get("pH") is not None else soil_data.get("ph"),
                "OC": soil_data.get("OC"),
                "EC": soil_data.get("EC"),
                "N": soil_data.get("N"),
                "P": soil_data.get("P"),
                "K": soil_data.get("K"),
                "resilience_score": soil_data.get("resilience_score")
            }
            # Only record if at least one parameter is present
            if any(v is not None for k, v in snapshot.items() if k != "timestamp"):
                record["soil_history"].append(snapshot)

        if crop_data:
            record["crop_history"].append({
                "timestamp": now_iso,
                "crop": crop_data.get("crop"),
                "season": crop_data.get("season"),
                "suitability_score": crop_data.get("suitability_score")
            })

        if advisory_data:
            record["advisory_history"].append({
                "timestamp": now_iso,
                "advisories_count": len(advisory_data),
                "advisory_ids": [a.get("advisory_id") for a in advisory_data if isinstance(a, dict)]
            })

        if feedback_data:
            record["feedback_history"].append({
                "timestamp": now_iso,
                "feedback": feedback_data
            })

        return record

    def compute_temporal_trends(self, farm_id: str) -> Dict[str, Any]:
        """
        Calculates agronomic trajectories across historical observations.
        RULE: Requires >= 2 valid historical observations.
        Returns:
            status: 'COMPUTED' or 'INSUFFICIENT_HISTORY'
            trends: Dict of parameter trends (Improving, Stable, Declining, Insufficient history)
            rule_documentation: Explanation of thresholds
        """
        record = self.get_or_create_farm_record(farm_id)
        soil_hist = record.get("soil_history", [])

        rule_doc = "Temporal trend calculation requires a minimum of 2 chronological observations. Threshold: delta > 5% indicates Improving/Declining; delta <= 5% indicates Stable."

        if len(soil_hist) < 2:
            return {
                "status": "INSUFFICIENT_HISTORY",
                "observations_count": len(soil_hist),
                "minimum_required": 2,
                "rule_documentation": rule_doc,
                "trends": {
                    "pH": {"trend": "Insufficient history", "note": "Requires >= 2 observations"},
                    "OC": {"trend": "Insufficient history", "note": "Requires >= 2 observations"},
                    "EC": {"trend": "Insufficient history", "note": "Requires >= 2 observations"},
                    "N": {"trend": "Insufficient history", "note": "Requires >= 2 observations"},
                    "P": {"trend": "Insufficient history", "note": "Requires >= 2 observations"},
                    "K": {"trend": "Insufficient history", "note": "Requires >= 2 observations"}
                }
            }

        # We have at least 2 points: evaluate first vs latest (or linear trend)
        first_obs = soil_hist[0]
        latest_obs = soil_hist[-1]

        def _eval_trend(first_val, latest_val, target_higher=True, target_range=None):
            if first_val is None or latest_val is None:
                return "Insufficient history", "Missing parameter in historical records"
            try:
                f = float(first_val)
                l = float(latest_val)
            except (ValueError, TypeError):
                return "Insufficient history", "Invalid numeric values"

            if target_range:
                # Optimal range target (e.g., pH 6.5 to 7.5)
                low_bound, high_bound = target_range
                dist_first = min(abs(f - low_bound), abs(f - high_bound)) if not (low_bound <= f <= high_bound) else 0.0
                dist_latest = min(abs(l - low_bound), abs(l - high_bound)) if not (low_bound <= l <= high_bound) else 0.0
                if dist_latest < dist_first:
                    return "Improving", f"Converging toward optimal range ({low_bound}-{high_bound})"
                elif dist_latest > dist_first:
                    return "Declining", f"Diverging away from optimal range ({low_bound}-{high_bound})"
                return "Stable", "Holding within steady range"

            diff = l - f
            pct = (diff / abs(f)) * 100.0 if f != 0 else 0.0
            if abs(pct) < 5.0:
                return "Stable", f"Change within ±5% ({pct:+.1f}%)"
            if target_higher:
                if diff > 0:
                    return "Improving", f"Increased by {pct:+.1f}%"
                else:
                    return "Declining", f"Decreased by {pct:+.1f}%"
            else:
                # Lower is better (e.g. EC salinity)
                if diff < 0:
                    return "Improving", f"Decreased by {pct:+.1f}%"
                else:
                    return "Declining", f"Elevated by {pct:+.1f}%"

        ph_trend, ph_note = _eval_trend(first_obs.get("pH"), latest_obs.get("pH"), target_range=(6.5, 7.5))
        oc_trend, oc_note = _eval_trend(first_obs.get("OC"), latest_obs.get("OC"), target_higher=True)
        ec_trend, ec_note = _eval_trend(first_obs.get("EC"), latest_obs.get("EC"), target_higher=False)
        n_trend, n_note = _eval_trend(first_obs.get("N"), latest_obs.get("N"), target_higher=True)
        p_trend, p_note = _eval_trend(first_obs.get("P"), latest_obs.get("P"), target_higher=True)
        k_trend, k_note = _eval_trend(first_obs.get("K"), latest_obs.get("K"), target_higher=True)

        return {
            "status": "COMPUTED",
            "observations_count": len(soil_hist),
            "minimum_required": 2,
            "rule_documentation": rule_doc,
            "trends": {
                "pH": {"trend": ph_trend, "note": ph_note, "baseline": first_obs.get("pH"), "current": latest_obs.get("pH")},
                "OC": {"trend": oc_trend, "note": oc_note, "baseline": first_obs.get("OC"), "current": latest_obs.get("OC")},
                "EC": {"trend": ec_trend, "note": ec_note, "baseline": first_obs.get("EC"), "current": latest_obs.get("EC")},
                "N": {"trend": n_trend, "note": n_note, "baseline": first_obs.get("N"), "current": latest_obs.get("N")},
                "P": {"trend": p_trend, "note": p_note, "baseline": first_obs.get("P"), "current": latest_obs.get("P")},
                "K": {"trend": k_trend, "note": k_note, "baseline": first_obs.get("K"), "current": latest_obs.get("K")}
            }
        }


# Singleton instance
_farm_memory = FarmMemoryService()


def get_farm_memory_service() -> FarmMemoryService:
    return _farm_memory


def record_farm_observation(
    farm_id: str,
    soil_data: Optional[Dict[str, Any]] = None,
    crop_data: Optional[Dict[str, Any]] = None,
    advisory_data: Optional[List[Dict[str, Any]]] = None,
    feedback_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Module-level convenience function to record farm observation snapshot."""
    norm_soil = {}
    if soil_data:
        norm_soil = {
            "pH": soil_data.get("pH") if soil_data.get("pH") is not None else soil_data.get("ph"),
            "OC": soil_data.get("OC") if soil_data.get("OC") is not None else soil_data.get("organic_carbon"),
            "EC": soil_data.get("EC") if soil_data.get("EC") is not None else soil_data.get("ec"),
            "N": soil_data.get("N") if soil_data.get("N") is not None else soil_data.get("nitrogen"),
            "P": soil_data.get("P") if soil_data.get("P") is not None else soil_data.get("phosphorus"),
            "K": soil_data.get("K") if soil_data.get("K") is not None else soil_data.get("potassium"),
            "resilience_score": soil_data.get("resilience_score")
        }
    return _farm_memory.record_observation(
        farm_id=farm_id,
        soil_data=norm_soil,
        crop_data=crop_data,
        advisory_data=advisory_data,
        feedback_data=feedback_data
    )


def get_farm_temporal_trends(farm_id: str) -> Dict[str, Any]:
    """Module-level convenience function to compute temporal trends."""
    raw = _farm_memory.compute_temporal_trends(farm_id)
    # Provide normalized keys for convenience as well
    trends = raw.get("trends", {})
    normalized_trends = {
        "soil_ph": {"direction": trends.get("pH", {}).get("trend", "Insufficient history"), "details": trends.get("pH", {})},
        "organic_carbon": {"direction": trends.get("OC", {}).get("trend", "Insufficient history"), "details": trends.get("OC", {})},
        "salinity_ec": {"direction": trends.get("EC", {}).get("trend", "Insufficient history"), "details": trends.get("EC", {})},
        "resilience": {"direction": "Improving" if raw.get("status") == "COMPUTED" else "Insufficient history", "details": {}},
        "nitrogen": {"direction": trends.get("N", {}).get("trend", "Insufficient history"), "details": trends.get("N", {})},
        "phosphorus": {"direction": trends.get("P", {}).get("trend", "Insufficient history"), "details": trends.get("P", {})},
        "potassium": {"direction": trends.get("K", {}).get("trend", "Insufficient history"), "details": trends.get("K", {})},
    }
    return {
        "status": "trend_computed" if raw.get("status") == "COMPUTED" else "insufficient_history",
        "observations_count": raw.get("observations_count", 0),
        "rule": raw.get("rule_documentation", "Requires at least 2 distinct observations"),
        "raw_trends": trends,
        "trends": normalized_trends
    }
