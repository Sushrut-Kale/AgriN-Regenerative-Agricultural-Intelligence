"""
AgriN Base Country Adapter Interface
Establishes the contract for country-specific adapters to interface with the core
AgriN Data Exchange (ADE) without polluting the core agricultural engine with national assumptions.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
try:
    from backend.app.services.agri_interoperability import (
        ADE_Location, ADE_SoilObservation, ADE_WeatherObservation, ADE_CropObservation
    )
except ImportError:
    from app.services.agri_interoperability import (
        ADE_Location, ADE_SoilObservation, ADE_WeatherObservation, ADE_CropObservation
    )



class BaseCountryAdapter(ABC):
    """Abstract base adapter for national agricultural systems."""
    
    @property
    @abstractmethod
    def country_iso3(self) -> str:
        """ISO 3166-1 alpha-3 code (e.g. IND, BRA, RUS, CHN, ZAF)."""
        pass

    @property
    @abstractmethod
    def country_name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_reference_implementation(self) -> bool:
        """True if the adapter has fully populated production registries and live services."""
        pass

    @abstractmethod
    def resolve_location(self, raw_location: Dict[str, Any]) -> ADE_Location:
        """Maps country-specific administrative divisions to ADE_Location."""
        pass

    @abstractmethod
    def normalize_soil_test(self, raw_soil_data: Dict[str, Any], farm_uuid: str) -> ADE_SoilObservation:
        """Translates national soil test card format into standardized SI mg/kg observation."""
        pass

    @abstractmethod
    def get_supported_agro_zones(self) -> List[Dict[str, Any]]:
        """Returns the national agro-ecological / climatic classification zones."""
        pass
