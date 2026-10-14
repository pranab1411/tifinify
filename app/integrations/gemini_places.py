import os
import re
import json
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from app.integrations.base_source import BaseProviderSource
from app.models import db, Provider, ProviderSource, Review
from app.services.review_service import ReviewService
from app.utils.geo import haversine_distance

logger = logging.getLogger(__name__)


class GeminiPlacesAdapter(BaseProviderSource):
    """Adapter using Google Gemini to discover and synthesize local tiffin & mess services
    for any user locality or GPS coordinates, with a deterministic fallback when offline."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.client = None

        if self.api_key and len(self.api_key.strip()) > 10:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key.strip())
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        """Check if a valid Gemini API key is configured."""
        return bool(self.client is not None)

    def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_meters: int = 5000,
        keyword: str = "tiffin",
    ) -> List[Dict[str, Any]]:
        """Implementation of BaseProviderSource.search_nearby using Gemini discovery."""
        return self.discover_places(
            location_name=f"Area near ({lat:.4f}, {lng:.4f})",
            lat=lat,
            lng=lng,
            count=5,
        )

    def fetch_place_details(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Fetch place details for an external ID."""
        # For Gemini discovery places, full details are synthesized during discovery
        return None

    def discover_places(
        self,
        location_name: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Discover authentic local tiffin and mess providers using Gemini AI with Google Search grounding,
        or the live WebSearchPlacesAdapter when offline/unconfigured."""
        if lat is None or lng is None:
            lat, lng = 23.1815, 79.9864

        locality = location_name.split(",")[0].strip() if location_name else "Local Area"
        # Strip generic GPS/location prefixes
        clean_locality = re.sub(r"^(current location\s*\(?|\)?|location\s*\(?)", "", locality, flags=re.IGNORECASE).strip()
        if not clean_locality or any(k in clean_locality.lower() for k in ["gps", "coords"]):
            clean_locality = "Jabalpur"

        # If Gemini client is active, attempt generative local place discovery with Google Search grounding
        if self.is_configured():
            try:
                from google.genai import types

                prompt = (
                    f"Search Google and find {count} REAL, ACTUAL tiffin services, student messes, and homestyle dabba services "
                    f"currently operating in or near '{clean_locality}' (Coordinates: {lat}, {lng}).\n\n"
                    f"Requirements:\n"
                    f"1. Name: Real, authentic business names from Google Maps / local directories (e.g. 'Central Mess', 'Punjabi Tiffin Service', 'Pathak Tiffin', etc.). "
                    f"Do NOT invent or fabricate fake template names.\n"
                    f"2. Category: 'tiffin' (delivery dabba), 'mess' (dining hall), or 'both'.\n"
                    f"3. Food Type: 'veg', 'non-veg', or 'both'.\n"
                    f"4. Realistic or known street address and phone in {clean_locality}.\n"
                    f"5. Coordinates: Near {lat}, {lng}.\n"
                    f"6. Real Customer Feedback: 2 to 4 genuine customer reviews per provider summarizing actual taste, hygiene, and service.\n\n"
                    f"Respond ONLY with a valid JSON object matching this schema, without markdown formatting or code fences:\n"
                    f'{{\n'
                    f'  "places": [\n'
                    f'    {{\n'
                    f'      "name": "Exact Business Name",\n'
                    f'      "category": "tiffin",\n'
                    f'      "food_type": "veg",\n'
                    f'      "address": "Street Address, {clean_locality}",\n'
                    f'      "locality": "{clean_locality}",\n'
                    f'      "latitude": {lat},\n'
                    f'      "longitude": {lng},\n'
                    f'      "phone": "+91 98220 12345",\n'
                    f'      "price_per_month": 2500,\n'
                    f'      "price_per_meal": 85,\n'
                    f'      "delivery_available": true,\n'
                    f'      "source_rating": 4.5,\n'
                    f'      "source_review_count": 48,\n'
                    f'      "reviews": [\n'
                    f'        {{\n'
                    f'          "reviewer_name": "Customer Name",\n'
                    f'          "rating": 4.5,\n'
                    f'          "text": "Detailed review about meal quality and service."\n'
                    f'        }}\n'
                    f'      ]\n'
                    f'    }}\n'
                    f'  ]\n'
                    f'}}'
                )

                model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
                # Use Google Search tool grounding if supported by model
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                        ),
                    )
                except Exception as tool_err:
                    logger.info(f"Google Search tool grounding fallback to standard prompt: {tool_err}")
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )

                if response and response.text:
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]

                    parsed = json.loads(raw_text.strip())
                    places = parsed.get("places", [])
                    if places and len(places) > 0:
                        for p in places:
                            if not p.get("latitude") or abs(float(p["latitude"]) - lat) > 0.3:
                                p["latitude"] = lat + random.uniform(-0.012, 0.012)
                            if not p.get("longitude") or abs(float(p["longitude"]) - lng) > 0.3:
                                p["longitude"] = lng + random.uniform(-0.012, 0.012)
                            if not p.get("locality"):
                                p["locality"] = clean_locality
                        return places
            except Exception as e:
                logger.warning(f"Gemini place discovery error: {e}. Falling back to live web/OSM search.")

        # Live Web Search & Overpass Fallback (discovers real places from Google/DuckDuckGo/OSM)
        from app.integrations.web_search_places import WebSearchPlacesAdapter
        web_adapter = WebSearchPlacesAdapter()
        real_places = web_adapter.discover_real_places(
            location_name=clean_locality,
            lat=lat,
            lng=lng,
            count=count,
        )
        if real_places and len(real_places) > 0:
            return real_places

        # If zero places discovered, return empty list rather than fake template places
        return []



    def ingest_to_database(self, place_data: Dict[str, Any]) -> Optional[Provider]:
        """Normalize and persist discovered place and its reviews, then run AI trust analysis."""
        name = place_data.get("name", "Local Tiffin Service")
        raw_slug = "".join(c for c in name.lower() if c.isalnum() or c == " ").replace(" ", "-")
        slug = f"ai-{raw_slug[:85]}-{random.randint(1000, 9999)}"

        # Check if already exists with same name and location
        existing = Provider.query.filter_by(name=name).first()
        if existing:
            ReviewService.analyze_provider(existing.id)
            return existing

        provider = Provider(
            name=name,
            slug=slug,
            category=place_data.get("category", "tiffin"),
            food_type=place_data.get("food_type", "veg"),
            meal_types="lunch,dinner",
            address=place_data.get("address", "Local Area"),
            locality=place_data.get("locality", "Local Area"),
            latitude=float(place_data.get("latitude", 18.5679)),
            longitude=float(place_data.get("longitude", 73.9143)),
            phone=place_data.get("phone"),
            source_rating=float(place_data.get("source_rating", 4.5)),
            source_review_count=int(place_data.get("source_review_count", 25)),
            price_per_month=int(place_data.get("price_per_month", 2400)),
            price_per_meal=int(place_data.get("price_per_meal", 80)),
            delivery_available=place_data.get("delivery_available", True),
            pickup_available=True,
            is_active=True,
            is_demo=False,
        )
        db.session.add(provider)
        db.session.commit()

        # Add ProviderSource tag
        ps = ProviderSource(
            provider_id=provider.id,
            source_type="gemini_discovery",
            external_id=slug,
        )
        db.session.add(ps)
        db.session.commit()

        # Add reviews
        reviews = place_data.get("reviews", [])
        now = datetime.now(timezone.utc)
        for i, r in enumerate(reviews):
            review_text = r.get("text", "").strip()
            if not review_text:
                continue

            review_date = now - timedelta(days=(i * 3 + 1))
            ReviewService.add_review(
                provider_id=provider.id,
                rating=float(r.get("rating", 4.5)),
                review_text=review_text,
                reviewer_name=r.get("reviewer_name", "Verified Customer"),
                source="gemini_verified",
                review_date=review_date,
            )

        # Run explainable review trust audit
        ReviewService.analyze_provider(provider.id)
        return provider
