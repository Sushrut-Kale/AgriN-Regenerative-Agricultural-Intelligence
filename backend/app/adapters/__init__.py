"""
AgriN Country Adapters Package
"""

try:
    from backend.app.adapters.base import BaseCountryAdapter
    from backend.app.adapters.india import IndiaAdapter
    from backend.app.adapters.brics import (
        BrazilAdapter, RussiaAdapter, ChinaAdapter, SouthAfricaAdapter
    )
except ImportError:
    from app.adapters.base import BaseCountryAdapter
    from app.adapters.india import IndiaAdapter
    from app.adapters.brics import (
        BrazilAdapter, RussiaAdapter, ChinaAdapter, SouthAfricaAdapter
    )


ADAPTER_REGISTRY = {
    "IND": IndiaAdapter(),
    "BRA": BrazilAdapter(),
    "RUS": RussiaAdapter(),
    "CHN": ChinaAdapter(),
    "ZAF": SouthAfricaAdapter()
}

def get_country_adapter(country_iso3: str = "IND") -> BaseCountryAdapter:
    iso = country_iso3.upper()
    if iso in ADAPTER_REGISTRY:
        return ADAPTER_REGISTRY[iso]
    return ADAPTER_REGISTRY["IND"]
