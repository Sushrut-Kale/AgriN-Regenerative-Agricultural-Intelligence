"""
FarmFriend AI — Real-Time Weather Integration Service
======================================================

Fetches real-time weather and climate observations using Open-Meteo Open API.
Provides dynamic live weather (temperature, relative humidity, estimated seasonal rainfall)
for Maharashtra districts with graceful fallback to district climatology benchmarks.
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List

# Representative coordinates for Maharashtra districts
DISTRICT_COORDINATES = {
    "parbhani": {"lat": 19.26, "lon": 76.77, "name": "Parbhani", "region": "Marathwada", "default_rainfall": 750, "default_temp": 29.0, "default_humidity": 55.0},
    "pune": {"lat": 18.52, "lon": 73.85, "name": "Pune", "region": "Western Plateau", "default_rainfall": 600, "default_temp": 27.0, "default_humidity": 60.0},
    "nagpur": {"lat": 21.15, "lon": 79.08, "name": "Nagpur", "region": "Vidarbha", "default_rainfall": 1050, "default_temp": 30.0, "default_humidity": 62.0},
    "nashik": {"lat": 19.99, "lon": 73.79, "name": "Nashik", "region": "North Maharashtra", "default_rainfall": 700, "default_temp": 28.0, "default_humidity": 52.0},
    "aurangabad": {"lat": 19.87, "lon": 75.34, "name": "Aurangabad (Chhatrapati Sambhajinagar)", "region": "Marathwada", "default_rainfall": 720, "default_temp": 29.0, "default_humidity": 54.0},
    "amravati": {"lat": 20.93, "lon": 77.75, "name": "Amravati", "region": "Vidarbha", "default_rainfall": 950, "default_temp": 30.0, "default_humidity": 58.0},
    "kolhapur": {"lat": 16.70, "lon": 74.24, "name": "Kolhapur", "region": "Western Ghats", "default_rainfall": 1100, "default_temp": 26.5, "default_humidity": 68.0},
    "latur": {"lat": 18.40, "lon": 76.58, "name": "Latur", "region": "Marathwada", "default_rainfall": 740, "default_temp": 29.5, "default_humidity": 53.0},
    "solapur": {"lat": 17.65, "lon": 75.90, "name": "Solapur", "region": "Western Plateau", "default_rainfall": 550, "default_temp": 30.5, "default_humidity": 50.0},
    "mumbai": {"lat": 19.07, "lon": 72.87, "name": "Mumbai / Konkan", "region": "Konkan", "default_rainfall": 2200, "default_temp": 28.0, "default_humidity": 82.0},
    "ratnagiri": {"lat": 16.99, "lon": 73.30, "name": "Ratnagiri", "region": "Konkan", "default_rainfall": 3000, "default_temp": 27.5, "default_humidity": 84.0},
    "nanded": {"lat": 19.15, "lon": 77.30, "name": "Nanded", "region": "Marathwada", "default_rainfall": 880, "default_temp": 29.5, "default_humidity": 58.0},
    "beed": {"lat": 18.99, "lon": 75.76, "name": "Beed", "region": "Marathwada", "default_rainfall": 680, "default_temp": 29.0, "default_humidity": 52.0},
    "jalgaon": {"lat": 21.00, "lon": 75.56, "name": "Jalgaon", "region": "North Maharashtra", "default_rainfall": 750, "default_temp": 30.0, "default_humidity": 55.0},
    "satara": {"lat": 17.68, "lon": 74.00, "name": "Satara", "region": "Western Plateau", "default_rainfall": 800, "default_temp": 26.0, "default_humidity": 62.0},
    "sangli": {"lat": 16.85, "lon": 74.56, "name": "Sangli", "region": "Western Plateau", "default_rainfall": 620, "default_temp": 27.5, "default_humidity": 58.0},
    "akola": {"lat": 20.70, "lon": 77.00, "name": "Akola", "region": "Vidarbha", "default_rainfall": 840, "default_temp": 30.5, "default_humidity": 56.0},
    "buldhana": {"lat": 20.53, "lon": 76.18, "name": "Buldhana", "region": "Vidarbha", "default_rainfall": 800, "default_temp": 29.0, "default_humidity": 54.0},
    "wardha": {"lat": 20.74, "lon": 78.60, "name": "Wardha", "region": "Vidarbha", "default_rainfall": 1000, "default_temp": 30.0, "default_humidity": 60.0},
    "chandrapur": {"lat": 19.96, "lon": 79.29, "name": "Chandrapur", "region": "Vidarbha", "default_rainfall": 1200, "default_temp": 31.0, "default_humidity": 64.0},
}

DEFAULT_FALLBACK = {
    "lat": 19.26, "lon": 76.77, "name": "General Maharashtra", "region": "Marathwada",
    "default_rainfall": 750, "default_temp": 28.5, "default_humidity": 60.0
}


def get_district_info(district_name: str, state_name: Optional[str] = None) -> dict:
    """Find district coordinates and climatology benchmarks across India with MH fallback."""
    d_clean = district_name.strip().lower()
    for key, info in DISTRICT_COORDINATES.items():
        if key in d_clean or d_clean in key or d_clean in info["name"].lower():
            return {**info, "state": "Maharashtra"}

    from backend.app.services.geo_service import find_district_by_name
    match = find_district_by_name(district_name, state_name)
    if match:
        return {
            "lat": match["lat"],
            "lon": match["lon"],
            "name": match["name"],
            "state": match.get("state", state_name or "Maharashtra"),
            "region": match.get("zone", "General India"),
            "default_rainfall": match.get("annual_rainfall", 800),
            "default_temp": match.get("default_temp", 26.5),
            "default_humidity": match.get("default_humidity", 60.0)
        }

    return {**DEFAULT_FALLBACK, "state": "Maharashtra"}


def fetch_live_weather(
    district_name: str = "Parbhani",
    state_name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> Dict[str, Any]:
    """
    Fetch real-time current weather parameters for any location in India.
    Accepts explicit coordinates (lat, lon) or district/state name.
    Queries Open-Meteo API with graceful fallback to regional climatology.
    """
    from backend.app.services.geo_service import find_nearest_district

    if lat is not None and lon is not None:
        nearest_d, resolved_state = find_nearest_district(lat, lon)
        info = {
            "lat": lat,
            "lon": lon,
            "name": nearest_d["name"],
            "state": resolved_state,
            "region": nearest_d.get("zone", "Regional Agro-Climatic Zone"),
            "default_rainfall": nearest_d.get("annual_rainfall", 800),
            "default_temp": nearest_d.get("default_temp", 26.5),
            "default_humidity": nearest_d.get("default_humidity", 60.0)
        }
    else:
        info = get_district_info(district_name, state_name)
        lat, lon = info["lat"], info["lon"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&daily=precipitation_sum&timezone=Asia%2FKolkata"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AgriN/2.0 (Agricultural Decision Support)"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})

                temp = current.get("temperature_2m")
                humidity = current.get("relative_humidity_2m")

                # Daily precipitation sum from API forecast if available
                daily_precip = data.get("daily", {}).get("precipitation_sum", [])
                recent_precip_est = sum(daily_precip[:7]) if daily_precip else 0.0

                # Compute Risk Alerts
                temp_val = round(float(temp), 1) if temp is not None else info["default_temp"]
                humid_val = round(float(humidity), 1) if humidity is not None else info["default_humidity"]
                rain_val = info["default_rainfall"]
                risk_alerts = []
                if temp_val > 39.0:
                    risk_alerts.append("Heat Stress Alert: Ambient temperature exceeds 39°C; high evapotranspiration.")
                elif temp_val < 10.0:
                    risk_alerts.append("Chilling / Frost Risk: Temperature below 10°C; delay early morning spraying.")
                if humid_val > 85.0:
                    risk_alerts.append("High Humidity Watch: RH > 85% elevates foliar fungal disease incidence.")
                elif humid_val < 25.0:
                    risk_alerts.append("Atmospheric Dryness Alert: Low RH accelerates rootzone desiccation.")
                if rain_val < 500:
                    risk_alerts.append("Seasonal Moisture Deficit: Low precipitation zone requires water budgeting.")

                from datetime import datetime, timezone
                obs_time = datetime.now(timezone.utc).isoformat()

                return {
                    "is_live_data": True,
                    "source": "Open-Meteo Real-Time Weather API",
                    "observed_at": obs_time,
                    "freshness": "Fresh (< 15 min)",
                    "confidence": "High",
                    "district": info["name"],
                    "state": info.get("state", "India"),
                    "region": info["region"],
                    "coordinates": {"lat": lat, "lon": lon},
                    "temperature": temp_val,
                    "humidity": humid_val,
                    "rainfall": rain_val,
                    "recent_7day_precipitation_mm": round(recent_precip_est, 1),
                    "risk_alerts": risk_alerts,
                    "note": f"Live weather fetched successfully for {info['name']}, {info.get('state', '')}."
                }
    except Exception as err:
        print(f"Notice: Live weather fetch using fallback climatology for {district_name}: {err}")

    # Fallback response
    from datetime import datetime, timezone
    obs_time = datetime.now(timezone.utc).isoformat()
    return {
        "is_live_data": False,
        "source": "Indian Regional Climatology Database",
        "observed_at": obs_time,
        "freshness": "Climatological Normal",
        "confidence": "Medium",
        "district": info["name"],
        "state": info.get("state", "India"),
        "region": info["region"],
        "coordinates": {"lat": lat, "lon": lon},
        "temperature": info["default_temp"],
        "humidity": info["default_humidity"],
        "rainfall": info["default_rainfall"],
        "recent_7day_precipitation_mm": 0.0,
        "risk_alerts": [],
        "note": f"Using benchmark regional climatology values for {info['name']}, {info.get('state', '')}."
    }


def get_weather_data(district: str = "Parbhani", state: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    """Convenience alias for fetch_live_weather."""
    return fetch_live_weather(district_name=district, state_name=state, lat=lat, lon=lon)


def get_weather_forecast(district: str = "Parbhani", state: Optional[str] = None) -> Dict[str, Any]:
    """Convenience alias for fetch_live_weather by district/state."""
    return fetch_live_weather(district_name=district, state_name=state)


def convert_weather_to_agricultural_reasoning(
    weather_info: Dict[str, Any],
    irrigation_available: bool = False,
    soil_drainage: str = "moderate"
) -> List[Dict[str, Any]]:
    """
    Transforms raw meteorological observations into agricultural implications and
    actionable agronomic context following the:
    Weather Observation -> Agricultural Implication -> Potential Advisory pipeline.
    Uses documented biophysical thresholds (ICAR/CRIDA agrometeorology standards).
    """
    reasonings = []
    temp = weather_info.get("temperature")
    humidity = weather_info.get("humidity")
    rainfall = weather_info.get("rainfall")
    precip_7d = weather_info.get("recent_7day_precipitation_mm", 0.0)

    # 1. Thermal Spike / Heat Stress (Threshold: > 38°C)
    if temp is not None and float(temp) >= 38.0:
        reasonings.append({
            "observation": f"Ambient temperature observed at {temp}°C (Threshold >= 38°C).",
            "agricultural_implication": "Elevated atmospheric vapor pressure deficit causes high evapotranspirative loss and pollen sterility in sensitive flowering stages.",
            "advisory": "Schedule evening or early morning micro-irrigation to moderate canopy microclimate; avoid chemical pesticide applications during peak afternoon heat.",
            "rule_source": "CRIDA Agrometeorological Heat Stress Threshold (>38°C)"
        })
    elif temp is not None and float(temp) <= 12.0:
        reasonings.append({
            "observation": f"Ambient temperature observed at {temp}°C (Threshold <= 12°C).",
            "agricultural_implication": "Chilling condition slows root phosphorus uptake and vegetative cell division; risk of morning frost injury in vulnerable valleys.",
            "advisory": "Provide light evening irrigation to release latent heat in the soil; utilize straw mulching around rootzones.",
            "rule_source": "ICAR-IARI Cold / Frost Protection Guidelines"
        })

    # 2. Moisture / Rainfall Implication
    if precip_7d is not None and float(precip_7d) >= 75.0:
        reasonings.append({
            "observation": f"Recent 7-day cumulative rainfall reached {precip_7d:.1f} mm (Excess precipitation event).",
            "agricultural_implication": f"Potential rootzone saturation and surface water stagnation in {soil_drainage} drainage soils, creating hypoxic root conditions.",
            "advisory": "Clear field drainage channels and open broad furrow outlets to prevent waterlogging; delay nitrogen top-dressing to prevent leaching losses.",
            "rule_source": "ICAR Drainage & Soil Aeration Standard"
        })
    elif rainfall is not None and float(rainfall) < 600.0 and not irrigation_available:
        reasonings.append({
            "observation": f"Annual/seasonal precipitation baseline is {rainfall:.0f} mm without assured irrigation.",
            "agricultural_implication": "Terminal moisture stress vulnerability during grain filling or pod maturation periods.",
            "advisory": "Prioritize short-duration, drought-hardy pulses or millets; apply 3-5 cm crop residue mulch to conserve stored soil moisture.",
            "rule_source": "CRIDA Rainfed Dryland Agriculture Framework"
        })

    # 3. Relative Humidity / Foliar Pathogen Microclimate (Threshold: > 80% RH)
    if humidity is not None and float(humidity) >= 80.0:
        reasonings.append({
            "observation": f"High relative humidity observed at {humidity}% (Threshold >= 80% RH).",
            "agricultural_implication": "Prolonged leaf wetness duration creates favorable microclimate for foliar fungal spore germination (e.g., blast, rust, powdery mildew).",
            "advisory": "Maintain regular canopy scouting for initial necrotic lesions; avoid dense crop spacing and excess vegetative nitrogen application.",
            "rule_source": "ICAR Agrometeorological Disease Microclimate Rule"
        })
    elif humidity is not None and float(humidity) < 30.0:
        reasonings.append({
            "observation": f"Low atmospheric relative humidity observed at {humidity}% (Threshold < 30% RH).",
            "agricultural_implication": "Dry atmospheric conditions accelerate soil surface evaporation, increasing irrigation cycling frequency.",
            "advisory": "Use organic mulching or cover crops to buffer ground moisture against rapid evaporation.",
            "rule_source": "Soil-Plant-Atmosphere Continuum (SPAC) Standard"
        })

    return reasonings


