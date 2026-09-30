"""
AgriN — Pan-India Geographic & Agro-Climatic Intelligence Service
==================================================================

Handles geographic hierarchy:
  India -> State/UT -> District -> Sub-District (Taluka/Tehsil/Block) -> Village -> Farm

Also maps coordinates and locations to the 15 ICAR / Planning Commission National Agro-Climatic Zones.
"""

import os
import json
import math
from typing import Dict, List, Optional, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
INDIA_DIR = os.path.join(BASE_DIR, "knowledge", "india")

_STATES_DATA = None
_ACZ_DATA = None
_CROP_CALENDAR = None
_MH_DATA = None


def _load_data():
    global _STATES_DATA, _ACZ_DATA, _CROP_CALENDAR, _MH_DATA
    if _STATES_DATA is None:
        path = os.path.join(INDIA_DIR, "states_and_districts.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _STATES_DATA = json.load(f)
        else:
            _STATES_DATA = {"states": {}, "union_territories": {}}

    if _ACZ_DATA is None:
        path = os.path.join(INDIA_DIR, "agro_climatic_zones.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _ACZ_DATA = json.load(f).get("zones", {})
        else:
            _ACZ_DATA = {}

    if _CROP_CALENDAR is None:
        path = os.path.join(INDIA_DIR, "national_crop_calendar.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _CROP_CALENDAR = json.load(f).get("crops", {})
        else:
            _CROP_CALENDAR = {}

    if _MH_DATA is None:
        path = os.path.join(BASE_DIR, "knowledge", "maharashtra_data.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _MH_DATA = json.load(f)
        else:
            _MH_DATA = {}


def get_all_states() -> List[Dict[str, Any]]:
    """Return all 28 States and 8 Union Territories."""
    _load_data()
    result = []
    
    # States
    for state_name, info in _STATES_DATA.get("states", {}).items():
        result.append({
            "name": state_name,
            "type": "State",
            "capital": info.get("capital"),
            "district_count": len(info.get("districts", [])),
            "agro_climatic_zones": info.get("agro_climatic_zones", [])
        })

    # Union Territories
    for ut_name, info in _STATES_DATA.get("union_territories", {}).items():
        result.append({
            "name": ut_name,
            "type": "Union Territory",
            "capital": info.get("capital"),
            "district_count": len(info.get("districts", [])),
            "agro_climatic_zones": info.get("agro_climatic_zones", [])
        })

    return sorted(result, key=lambda x: x["name"])


def get_districts_for_state(state_name: str) -> List[Dict[str, Any]]:
    """Return all districts for a given state or union territory."""
    _load_data()
    if not state_name:
        state_name = "Maharashtra"

    state_clean = state_name.strip().lower()
    
    # Check states
    for s_name, info in _STATES_DATA.get("states", {}).items():
        if s_name.lower() == state_clean:
            return info.get("districts", [])

    # Check UTs
    for ut_name, info in _STATES_DATA.get("union_territories", {}).items():
        if ut_name.lower() == state_clean:
            return info.get("districts", [])

    # Fallback to Maharashtra if unmatched
    if "maharashtra" in state_clean and _MH_DATA:
        return _MH_DATA.get("districts", [])

    return []


def find_district_by_name(district_name: str, state_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Search for a district across all states or within a specific state."""
    _load_data()
    if not district_name:
        return None

    d_clean = district_name.strip().lower().replace("_", " ")

    # If state specified, search in that state first
    if state_name:
        districts = get_districts_for_state(state_name)
        for d in districts:
            if d["id"].lower() == d_clean or d["name"].lower() == d_clean or d_clean in d["name"].lower():
                return {**d, "state": state_name}

    # Search across all states
    all_states = {**_STATES_DATA.get("states", {}), **_STATES_DATA.get("union_territories", {})}
    for s_name, s_info in all_states.items():
        for d in s_info.get("districts", []):
            if d["id"].lower() == d_clean or d["name"].lower() == d_clean or d_clean in d["name"].lower():
                return {**d, "state": s_name}

    return None


def find_nearest_district(lat: float, lon: float) -> Tuple[Dict[str, Any], str]:
    """Find nearest district centroid to the given coordinates (Haversine formula)."""
    _load_data()
    best_dist = float("inf")
    best_district = None
    best_state = "Maharashtra"

    all_states = {**_STATES_DATA.get("states", {}), **_STATES_DATA.get("union_territories", {})}
    for s_name, s_info in all_states.items():
        for d in s_info.get("districts", []):
            d_lat = d.get("lat")
            d_lon = d.get("lon")
            if d_lat is not None and d_lon is not None:
                # Euclidean approximation suitable for regional centroid lookup
                dist = math.hypot(lat - d_lat, lon - d_lon)
                if dist < best_dist:
                    best_dist = dist
                    best_district = d
                    best_state = s_name

    if best_district:
        return best_district, best_state

    # Ultimate fallback to Parbhani
    return {
        "id": "parbhani", "name": "Parbhani", "lat": 19.26, "lon": 76.77,
        "zone": "Western Plateau and Hills", "annual_rainfall": 750,
        "default_temp": 29.0, "default_humidity": 55.0
    }, "Maharashtra"


def get_agro_climatic_zone_info(zone_name: str) -> Optional[Dict[str, Any]]:
    """Get metadata for an ICAR National Agro-Climatic Zone by name or ID."""
    _load_data()
    if not zone_name:
        return None
    # 1. Exact key match
    if zone_name in _ACZ_DATA:
        return {"name": zone_name, **_ACZ_DATA[zone_name]}
    
    # 2. Case-insensitive or normalized ID match (e.g. ACZ-01, IN_ACZ_01, Western Himalayan Region)
    clean_target = zone_name.strip().lower()
    clean_id = clean_target.replace("in_", "").replace("_", "-")
    for k, v in _ACZ_DATA.items():
        if k.lower() == clean_target:
            return {"name": k, **v}
        zid = v.get("id", "").lower()
        if zid == clean_target or zid == clean_id:
            return {"name": k, **v}
    return None


def get_all_agro_climatic_zones() -> List[Dict[str, Any]]:
    """Get all 15 ICAR National Agro-Climatic Zones."""
    _load_data()
    return [{"name": k, "code": v.get("id", k), "id": v.get("id", k), **v} for k, v in _ACZ_DATA.items()]




def get_crop_seasons_for_region(crop_name: str, state_name: Optional[str] = None) -> List[str]:
    """
    Get allowed seasons for a crop in a given state using multi-tier hierarchy:
    State override -> National default -> Maharashtra fallback -> []
    """
    _load_data()
    crop_info = _CROP_CALENDAR.get(crop_name.lower())
    if not crop_info:
        # Check old crop_requirements.json
        from backend.app.services.suitability_scorer import CROP_REQUIREMENTS
        old_req = CROP_REQUIREMENTS.get(crop_name.lower(), {})
        return old_req.get("seasons", {}).get("maharashtra", ["kharif", "rabi"])

    if state_name:
        st_key = state_name.strip().lower().replace(" ", "_")
        regional = crop_info.get("regional_seasons", {})
        if st_key in regional:
            return regional[st_key]

    return crop_info.get("national_seasons", ["kharif", "rabi"])


def get_crop_season_context(
    crop_name: str,
    season: str,
    state_name: Optional[str] = None,
    district_name: Optional[str] = None,
    agro_climatic_zone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates multi-factor seasonal intelligence:
    Location (State + District) + Agro-climatic Zone + Crop + Target Season.
    Returns:
        is_suitable_season: bool
        confidence: 'HIGH' (state-specific rule match), 'MEDIUM' (national baseline), 'LOW' (fallback)
        sowing_window: str
        harvest_window: str
        duration_days: str
        water_profile: str
        notes: str
    """
    _load_data()
    c_clean = crop_name.strip().lower()
    s_clean = season.strip().lower()
    crop_info = _CROP_CALENDAR.get(c_clean)

    if not crop_info:
        # Unknown crop fallback
        return {
            "is_suitable_season": True,
            "confidence": "LOW",
            "sowing_window": "Refer to local KVK advisory",
            "harvest_window": "Refer to local KVK advisory",
            "duration_days": "Unknown",
            "water_profile": "Standard crop water requirement",
            "notes": f"Crop '{crop_name}' not cataloged in primary national crop calendar; fallback heuristic applied."
        }

    st_key = state_name.strip().lower().replace(" ", "_") if state_name else None
    regional = crop_info.get("regional_seasons", {})
    
    if st_key and st_key in regional:
        allowed = [s.lower() for s in regional[st_key]]
        confidence = "HIGH"
        geo_level = f"State-specific calendar ({state_name})"
    else:
        allowed = [s.lower() for s in crop_info.get("national_seasons", ["kharif", "rabi"])]
        confidence = "MEDIUM"
        geo_level = "National agro-climatic baseline (State override not documented)"

    is_suitable = s_clean in allowed

    sowing_win = crop_info.get("sowing_window", {}).get(s_clean, "Season specific window")
    harvest_win = crop_info.get("harvest_window", {}).get(s_clean, "Season specific window")

    return {
        "is_suitable_season": is_suitable,
        "confidence": confidence,
        "allowed_seasons": allowed,
        "calendar_source": geo_level,
        "sowing_window": sowing_win,
        "harvest_window": harvest_win,
        "duration_days": crop_info.get("duration_days", "90-120"),
        "water_profile": crop_info.get("water_profile", "Moderate"),
        "notes": f"Sowing in {season.title()} is {'recommended' if is_suitable else 'sub-optimal/unfavorable'} under {geo_level}."
    }

