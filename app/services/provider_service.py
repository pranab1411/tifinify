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
            # If Google Places API is configured, query and ingest real places
            try:
                import os
                from flask import current_app, session
                from app.integrations.google_places import GooglePlacesAdapter
                api_key = None
                try:
                    api_key = session.get("google_maps_api_key") or current_app.config.get("GOOGLE_MAPS_API_KEY")
                except Exception:
                    pass
                api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")

                g_adapter = GooglePlacesAdapter(api_key=api_key)
                if not current_app.config.get("TESTING") and g_adapter.is_configured():
                    live_places = g_adapter.search_nearby(user_lat, user_lon, radius_meters=int(radius_km * 1000))
                    for lp in live_places:
                        g_adapter.ingest_to_database(lp)
            except Exception:
                pass

            candidate_providers = spatial_query.all()

            # If no providers exist in this location, adaptively seed realistic local providers
            if len(candidate_providers) == 0 and location_name:
                ProviderService.seed_adaptive_providers(user_lat, user_lon, location_name)
                candidate_providers = spatial_query.all()
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
    def seed_adaptive_providers(lat: float, lon: float, location_name: str = "Local Area") -> None:
        """Seed realistic local providers centered around user's requested coordinates."""
        from datetime import datetime, timedelta, timezone
        city_title = location_name.split(",")[0].strip() if location_name else "Local"
        slug_base = "".join(c for c in city_title.lower() if c.isalnum()) or "loc"

        providers_spec = [
            {
                "name": f"{city_title} Homely Tiffin Service",
                "slug": f"{slug_base}-homely-tiffin",
                "category": "tiffin",
                "food_type": "veg",
                "meal_types": "lunch,dinner",
                "address": f"Near Main Market, {city_title}",
                "locality": city_title,
                "latitude": lat + 0.0035,
                "longitude": lon + 0.0025,
                "phone": "+91 98200 44551",
                "opening_hours": "11:30 AM - 3:30 PM, 7:00 PM - 10:30 PM",
                "price_per_month": 2500,
                "price_per_meal": 85,
                "delivery_available": True,
                "pickup_available": True,
                "description": f"Fresh home-cooked pure vegetarian tiffins serving students and professionals in {city_title}.",
                "reviews": [
                    ("Ananya Roy", 5.0, "Superb taste and homestyle preparation. Rotis are very soft and dal is healthy.", -15),
                    ("Siddharth S", 4.5, "Clean packaging and consistent portion sizes. Highly recommended for daily meals.", -10),
                    ("Pooja M", 4.5, "Dependable daily delivery, always warm and on time.", -3),
                ]
            },
            {
                "name": f"{city_title} Student Mess & Thali",
                "slug": f"{slug_base}-student-mess",
                "category": "mess",
                "food_type": "both",
                "meal_types": "lunch,dinner",
                "address": f"College Road, {city_title}",
                "locality": city_title,
                "latitude": lat - 0.0048,
                "longitude": lon + 0.0038,
                "phone": "+91 98311 22334",
                "opening_hours": "12:00 PM - 4:00 PM, 7:30 PM - 11:00 PM",
                "price_per_month": 2200,
                "price_per_meal": 80,
                "delivery_available": True,
                "pickup_available": True,
                "description": f"Affordable student dining hall and mess serving vegetarian and egg/chicken thalis.",
                "reviews": [
                    ("UserA", 5.0, f"Best tiffin service in {city_title} call now for guaranteed discounts today!", -1),
                    ("UserB", 5.0, f"Best tiffin service in {city_title} call now for guaranteed discounts today!", -1),
                    ("Karan D", 2.0, "Food was cold and sabzi was excessively oily. Late delivery.", -8),
                ]
            },
            {
                "name": f"Maa Annapurna Rasoi ({city_title})",
                "slug": f"{slug_base}-annapurna-rasoi",
                "category": "both",
                "food_type": "jain_available",
                "meal_types": "lunch,dinner",
                "address": f"Station Road, {city_title}",
                "locality": city_title,
                "latitude": lat + 0.0075,
                "longitude": lon - 0.0055,
                "phone": "+91 98455 66778",
                "opening_hours": "11:00 AM - 3:00 PM, 6:30 PM - 10:00 PM",
                "price_per_month": 2800,
                "price_per_meal": 100,
                "delivery_available": True,
                "pickup_available": True,
                "description": f"Satvik pure veg food with Jain options available. Steel tiffin delivery across {city_title}.",
                "reviews": [
                    ("Manish Jain", 5.0, "Spotless hygiene and genuine Jain meal preparation without onion or garlic.", -20),
                    ("Ritu Sen", 4.0, "Good quantity and polite delivery staff. Worth the price.", -12),
                    ("Nikhil B", 4.5, "Homely taste and very light on stomach.", -4),
                ]
            },
            {
                "name": f"{city_title} Express Tiffin Hub",
                "slug": f"{slug_base}-express-tiffin",
                "category": "tiffin",
                "food_type": "both",
                "meal_types": "both",
                "address": f"Central Sector, {city_title}",
                "locality": city_title,
                "latitude": lat - 0.0085,
                "longitude": lon - 0.0072,
                "phone": "+91 98765 43210",
                "opening_hours": "12:00 PM - 3:00 PM, 7:00 PM - 11:00 PM",
                "price_per_month": 2400,
                "price_per_meal": 90,
                "delivery_available": True,
                "pickup_available": False,
                "description": f"Doorstep meal box delivery catering to hostellers and working professionals in {city_title}.",
                "reviews": [
                    ("Gaurav K", 4.5, "Great value for money and tasty variety every day.", -14),
                    ("Swati P", 4.0, "Neat packaging and generous rice and roti portions.", -7),
                ]
            }
        ]

        now = datetime.now(timezone.utc)
        for p_info in providers_spec:
            reviews = p_info.pop("reviews")
            existing = Provider.query.filter_by(slug=p_info["slug"]).first()
            if existing:
                continue

            provider = Provider(
                **p_info,
                is_demo=True,
                is_active=True,
            )
            db.session.add(provider)
            db.session.commit()

            for r_name, r_rating, r_text, days_offset in reviews:
                r_date = now + timedelta(days=days_offset)
                ReviewService.add_review(
                    provider_id=provider.id,
                    rating=r_rating,
                    review_text=r_text,
                    reviewer_name=r_name,
                    source="demo",
                    review_date=r_date,
                )

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
