from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseProviderSource(ABC):
    """Abstract Base Class for External Data Sources (Adapter Pattern)."""

    @abstractmethod
    def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        keyword: str = "tiffin",
    ) -> List[Dict[str, Any]]:
        """Search nearby providers and return unified normalized dictionaries."""
        pass

    @abstractmethod
    def fetch_place_details(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information including reviews for a specific external ID."""
        pass
