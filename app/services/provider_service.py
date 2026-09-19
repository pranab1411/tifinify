from typing import List, Dict, Any, Optional
from app.models import db, Provider, ProviderAnalysisSummary, Review
from app.utils.geo import haversine_distance, get_bounding_box
from app.services.review_service import ReviewService


class ProviderService:
    """Service to handle provider queries, geo-spatial discovery, filtering, and comparisons."""

    @staticmethod
    def search_providers(
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        radius_km: float = 5.0,
        category: Optional[str] = None,
        food_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        min_trust_score: Optional[int] = None,
        max_price: Optional[int] = None,
        sort_by: str = "distance",
        location_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter and rank nearby tiffin and mess providers with adaptive localized discovery."""
        query = Provider.query.filter_by(is_active=True)

        # Category filter
        if category and category.lower() != "all":
            if category.lower() in ("tiffin", "mess"):
                query = query.filter(
                    (Provider.category == category.lower()) | (Provider.category == "both")
                )

        # Food type filter
        if food_type and food_type.lower() != "all":
            if food_type.lower() == "veg":
                query = query.filter(
                    (Provider.food_type == "veg") | (Provider.food_type == "jain_available")
                )
            elif food_type.lower() == "non-veg":
                query = query.filter(
                    (Provider.food_type == "non-veg") | (Provider.food_type == "both")
                )

        # Minimum rating filter
        if min_rating and min_rating > 0:
            query = query.filter(Provider.source_rating >= float(min_rating))

        # Minimum trust score filter
        if min_trust_score and min_trust_score > 0:
            query = query.filter(Provider.review_trust_score >= int(min_trust_score))

        # Maximum price filter
        if max_price and max_price > 0:
            query = query.filter(
                (Provider.price_per_month <= int(max_price)) | (Provider.price_per_month.is_(None))
            )

        # Bounding box spatial optimization if coordinates are provided
        if user_lat is not None and user_lon is not None:
            min_lat, max_lat, min_lon, max_lon = get_bounding_box(user_lat, user_lon, radius_km)
            spatial_query = query.filter(
                Provider.latitude.between(min_lat, max_lat),
                Provider.longitude.between(min_lon, max_lon),
            )
            candidate_providers = spatial_query.all()

            # If no providers exist in this location, discover real local establishments via Google Search / Gemini / OSM
            if len(candidate_providers) == 0 and location_name:
                try:
                    ProviderService.discover_and_ingest_real_providers(user_lat, user_lon, location_name, radius_km)
                    candidate_providers = spatial_query.all()
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Real place discovery error: {e}")
        else:
            candidate_providers = query.all()

        results = []
        for p in candidate_providers:
            p_dict = p.to_dict()
            distance = None
            if user_lat is not None and user_lon is not None:
                dist = haversine_distance(user_lat, user_lon, p.latitude, p.longitude)
                if dist > radius_km:
                    continue  # Beyond exact circular radius
                distance = dist

            p_dict["distance_km"] = distance
            results.append(p_dict)

        # Sorting
        if sort_by == "distance" and user_lat is not None:
            results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"]))
        elif sort_by == "trust":
            results.sort(key=lambda x: x["review_trust_score"], reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x["source_rating"], reverse=True)
        elif sort_by == "price_asc":
            results.sort(key=lambda x: (x["price_per_month"] is None, x["price_per_month"] or 99999))

        return results

    @staticmethod
    def discover_and_ingest_real_providers(
        lat: float,
        lon: float,
        location_name: str = "Local Area",
        radius_km: float = 5.0,
    ) -> List[Provider]:
        """Discover actual real tiffin and mess providers using Google Search, Gemini AI, and OpenStreetMap."""
        import os
        import logging
        from flask import current_app, session
        from app.integrations.gemini_places import GeminiPlacesAdapter

        log = logging.getLogger(__name__)
        gemini_key = None
        try:
            gemini_key = session.get("gemini_api_key") or current_app.config.get("GEMINI_API_KEY")
        except Exception:
            pass
        gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY")

        adapter = GeminiPlacesAdapter(api_key=gemini_key)
        # discover_places uses Gemini with Google Search if configured,
        # or falls back to WebSearchPlacesAdapter (live Google/DuckDuckGo/OSM search) without API key
        real_places = adapter.discover_places(
            location_name=location_name,
            lat=lat,
            lng=lon,
            count=6,
        )

        ingested = []
        for rp in real_places:
            try:
                p = adapter.ingest_to_database(rp)
                if p:
                    ingested.append(p)
            except Exception as e:
                log.warning(f"Error ingesting discovered real place '{rp.get('name')}': {e}")

        return ingested

    @staticmethod
    def seed_adaptive_providers(lat: float, lon: float, location_name: str = "Local Area") -> None:
        """Backwards-compatible bridge that invokes discover_and_ingest_real_providers."""
        ProviderService.discover_and_ingest_real_providers(lat=lat, lon=lon, location_name=location_name)

    @staticmethod
    def get_provider_details(provider_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve complete provider details, ensuring analysis summary is computed."""
        provider = db.session.get(Provider, provider_id)
        if not provider:
            return None

        # Check if analysis summary exists; if not, trigger on first view
        if not provider.analysis_summary:
            ReviewService.analyze_provider(provider_id)
            # Re-fetch with populated summary
            provider = db.session.get(Provider, provider_id)

        data = provider.to_dict(include_reviews=True)
        return data

    @staticmethod
    def compare_providers(provider_id_1: int, provider_id_2: int, user_lat: float = None, user_lon: float = None) -> Dict[str, Any]:
        """Compare two providers side-by-side with objective, transparent metrics."""
        p1 = ProviderService.get_provider_details(provider_id_1)
        p2 = ProviderService.get_provider_details(provider_id_2)

        if not p1 or not p2:
            return {}

        if user_lat is not None and user_lon is not None:
            p1["distance_km"] = haversine_distance(user_lat, user_lon, p1["latitude"], p1["longitude"])
            p2["distance_km"] = haversine_distance(user_lat, user_lon, p2["latitude"], p2["longitude"])
        else:
            p1["distance_km"] = None
            p2["distance_km"] = None

        aspect_keys = ["taste", "food_quality", "hygiene", "quantity", "delivery", "value_for_money"]
        p1_aspects = p1.get("analysis", {}).get("aspects", {})
        p2_aspects = p2.get("analysis", {}).get("aspects", {})

        aspect_comparison = []
        for key in aspect_keys:
            label = key.replace("_", " ").title()
            val1 = p1_aspects.get(key)
            val2 = p2_aspects.get(key)
            aspect_comparison.append({
                "key": key,
                "label": label,
                "provider1_val": f"{val1}%" if val1 is not None else "N/A",
                "provider2_val": f"{val2}%" if val2 is not None else "N/A",
            })

        return {
            "provider1": p1,
            "provider2": p2,
            "aspect_comparison": aspect_comparison,
        }
