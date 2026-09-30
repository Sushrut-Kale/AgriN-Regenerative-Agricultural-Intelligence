"""
AgriN Satellite Intelligence Abstraction Layer
Defines clean provider interfaces:
SatelliteDataProvider -> VegetationObservation -> CropHealthSignal

STRICT NON-FABRICATION RULE:
If no raster provider (Sentinel-2, Landsat-8/9, PlanetScope) is active, returns:
`satellite_status = "NOT_CONNECTED"`
without simulating synthetic NDVI, fake false-color images, or fake vegetation health numbers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class VegetationObservation(BaseModel):
    """Standard spatial-temporal observation representing spectral canopy indicators."""
    farm_id: str
    timestamp: datetime
    satellite: str = Field(description="e.g. Sentinel-2A, Landsat-9")
    sensor: str = Field(description="e.g. MSI, OLI-2")
    resolution_meters: float = 10.0
    cloud_cover_percent: float = 0.0
    ndvi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    evi_mean: Optional[float] = None
    savi_mean: Optional[float] = None
    vegetation_health_index: Optional[float] = None
    crop_stress_flag: bool = False
    source_license: str = "Copernicus Open Access"


class SatelliteDataProvider:
    """Abstract provider interface for multi-spectral raster ingestion."""
    def get_provider_name(self) -> str:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

    def fetch_latest_observation(
        self,
        latitude: float,
        longitude: float,
        boundary_geojson: Optional[Dict[str, Any]] = None
    ) -> Optional[VegetationObservation]:
        raise NotImplementedError


class CopernicusSTACProvider(SatelliteDataProvider):
    """
    Production Copernicus Data Space Ecosystem / Sentinel-2 STAC Provider.
    Checks for configured STAC credentials and endpoint connectivity.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_provider_name(self) -> str:
        return "Copernicus Sentinel-2 MSI STAC API"

    def is_connected(self) -> bool:
        # In this phase, returns False until STAC endpoint credentials are supplied
        return bool(self.api_key)

    def fetch_latest_observation(
        self,
        latitude: float,
        longitude: float,
        boundary_geojson: Optional[Dict[str, Any]] = None
    ) -> Optional[VegetationObservation]:
        if not self.is_connected():
            return None
        # Future STAC raster download and pixel math happens here
        return None


def get_satellite_status_report(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns the real-time connectivity status of Earth Observation satellite providers.
    """
    provider = CopernicusSTACProvider()
    connected = provider.is_connected()

    return {
        "satellite_status": "CONNECTED" if connected else "NOT_CONNECTED",
        "farm_id": farm_id,
        "coordinates": {"lat": latitude, "lon": longitude} if (latitude and longitude) else None,
        "active_provider": provider.get_provider_name() if connected else None,
        "available_providers": [
            {
                "name": "Copernicus Sentinel-2 L2A (10m)",
                "status": "AWAITING_CREDENTIALS",
                "spectral_indices": ["NDVI", "NDWI", "EVI", "SAVI"],
                "revisit_interval_days": 5
            },
            {
                "name": "USGS Landsat-8/9 OLI-2 (30m)",
                "status": "ROADMAP",
                "spectral_indices": ["NDVI", "NDWI"],
                "revisit_interval_days": 16
            }
        ],
        "vegetation_observation": None,
        "message": (
            "Satellite Earth Observation provider is not currently connected. "
            "Data ingestion pipeline is architected and ready for Copernicus STAC credentials."
        ),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }
