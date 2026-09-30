"""
AgriN India Reference Country Adapter
Fully implemented production adapter utilizing:
- 28 States & 8 Union Territories
- 700+ District centroids & Haversine GPS resolution
- 15 ICAR / Planning Commission National Agro-Climatic Zones
- Indian Soil Health Card (DAC&FW) 12-parameter standard
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

try:
    from backend.app.adapters.base import BaseCountryAdapter
    from backend.app.services.agri_interoperability import ADE_Location, ADE_SoilObservation
    from backend.app.services.geo_service import (
        get_all_states,
        get_districts_for_state,
        find_district_by_name,
        find_nearest_district,
        get_all_agro_climatic_zones
    )
except ImportError:
    from app.adapters.base import BaseCountryAdapter
    from app.services.agri_interoperability import ADE_Location, ADE_SoilObservation
    from app.services.geo_service import (
        get_all_states,
        get_districts_for_state,
        find_district_by_name,
        find_nearest_district,
        get_all_agro_climatic_zones
    )



class IndiaAdapter(BaseCountryAdapter):
    """Production reference adapter for India."""
    
    @property
    def country_iso3(self) -> str:
        return "IND"

    @property
    def country_name(self) -> str:
        return "India"

    @property
    def is_reference_implementation(self) -> bool:
        return True

    def resolve_location(self, raw_location: Dict[str, Any]) -> ADE_Location:
        lat = raw_location.get("latitude")
        lon = raw_location.get("longitude")
        state = raw_location.get("state") or raw_location.get("admin_level_1", "Maharashtra")
        district = raw_location.get("district") or raw_location.get("admin_level_2", "Parbhani")
        
        # GPS fallback if lat/lon provided
        if lat is not None and lon is not None:
            lat_f = float(lat)
            lon_f = float(lon)
            nearest = find_nearest_district(lat_f, lon_f)
            if nearest:
                district = nearest["district"]
                state = nearest["state"]
        else:
            d_info = find_district_by_name(district, state)
            if d_info and "latitude" in d_info:
                lat_f = d_info["latitude"]
                lon_f = d_info["longitude"]
            else:
                lat_f = 19.26  # Parbhani default fallback
                lon_f = 76.77

        return ADE_Location(
            country_iso3="IND",
            admin_level_1=state,
            admin_level_2=district,
            latitude=round(lat_f, 4),
            longitude=round(lon_f, 4),
            coordinate_reference_system="EPSG:4326"
        )

    def normalize_soil_test(self, raw_soil_data: Dict[str, Any], farm_uuid: str) -> ADE_SoilObservation:
        def _f(key: str) -> Optional[float]:
            v = raw_soil_data.get(key)
            if v is None:
                return None
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        # Convert Indian Soil Card kg/ha to mg/kg where necessary:
        # Standard conversion for top 15cm soil (bulk density 1.33 g/cm3, 2,000,000 kg soil/ha):
        # 1 mg/kg (ppm) ≈ 2.24 kg/ha. Therefore, mg/kg = (kg/ha) / 2.24
        n_kgha = _f("N")
        p_kgha = _f("P")
        k_kgha = _f("K")

        n_mgkg = round(n_kgha / 2.24, 2) if n_kgha is not None else None
        p_mgkg = round(p_kgha / 2.24, 2) if p_kgha is not None else None
        k_mgkg = round(k_kgha / 2.24, 2) if k_kgha is not None else None

        return ADE_SoilObservation(
            observation_id=f"obs-soil-ind-{uuid.uuid4().hex[:8]}",
            farm_uuid=farm_uuid,
            observed_at=datetime.now(timezone.utc),
            laboratory_standard="DAC&FW_SHC_GUIDELINES",
            ph_water=_f("pH"),
            organic_carbon_percent=_f("OC"),
            electrical_conductivity_ds_m=_f("EC"),
            available_nitrogen_mg_kg=n_mgkg,
            available_phosphorus_mg_kg=p_mgkg,
            available_potassium_mg_kg=k_mgkg,
            available_sulphur_mg_kg=_f("S"),
            available_zinc_mg_kg=_f("Zn"),
            available_iron_mg_kg=_f("Fe"),
            available_boron_mg_kg=_f("B")
        )

    def get_supported_agro_zones(self) -> List[Dict[str, Any]]:
        return get_all_agro_climatic_zones()
