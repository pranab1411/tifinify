import math
import logging
from typing import Tuple, Optional, Dict
import requests

logger = logging.getLogger(__name__)

# Fast offline coordinates for major Indian cities & educational hubs
INDIAN_CITIES_GEO: Dict[str, Tuple[float, float, str]] = {
    "pune": (18.5204, 73.8567, "Pune, Maharashtra"),
    "viman nagar": (18.5679, 73.9143, "Viman Nagar, Pune, Maharashtra"),
    "kothrud": (18.5074, 73.8077, "Kothrud, Pune, Maharashtra"),
    "hinjawadi": (18.5913, 73.7389, "Hinjawadi, Pune, Maharashtra"),
    "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra"),
    "delhi": (28.6139, 77.2090, "New Delhi, Delhi"),
    "new delhi": (28.6139, 77.2090, "New Delhi, Delhi"),
    "noida": (28.5355, 77.3910, "Noida, Uttar Pradesh"),
    "gurgaon": (28.4595, 77.0266, "Gurugram, Haryana"),
    "gurugram": (28.4595, 77.0266, "Gurugram, Haryana"),
    "bangalore": (12.9716, 77.5946, "Bengaluru, Karnataka"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru, Karnataka"),
    "koramangala": (12.9352, 77.6245, "Koramangala, Bengaluru, Karnataka"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad, Telangana"),
    "kolkata": (22.5726, 88.3639, "Kolkata, West Bengal"),
    "chennai": (13.0827, 80.2707, "Chennai, Tamil Nadu"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad, Gujarat"),
    "jaipur": (26.9124, 75.7873, "Jaipur, Rajasthan"),
    "kota": (25.2138, 75.8648, "Kota, Rajasthan"),
    "indore": (22.7196, 75.8577, "Indore, Madhya Pradesh"),
    "bhopal": (23.2599, 77.4126, "Bhopal, Madhya Pradesh"),
    "lucknow": (26.8467, 80.9462, "Lucknow, Uttar Pradesh"),
    "kanpur": (26.4499, 80.3319, "Kanpur, Uttar Pradesh"),
    "patna": (25.5941, 85.1376, "Patna, Bihar"),
    "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar, Odisha"),
    "ranchi": (23.3441, 85.3096, "Ranchi, Jharkhand"),
    "chandigarh": (30.7333, 76.7794, "Chandigarh"),
    "dehradun": (30.3165, 78.0322, "Dehradun, Uttarakhand"),
    "varanasi": (25.3176, 82.9739, "Varanasi, Uttar Pradesh"),
    "nagpur": (21.1458, 79.0882, "Nagpur, Maharashtra"),
    "coimbatore": (11.0168, 76.9558, "Coimbatore, Tamil Nadu"),
    "kochi": (9.9312, 76.2673, "Kochi, Kerala"),
    "visakhapatnam": (17.6868, 83.2185, "Visakhapatnam, Andhra Pradesh"),
    "jabalpur": (23.1815, 79.9864, "Jabalpur, Madhya Pradesh"),
    "ranjhi": (23.1900, 80.0100, "Ranjhi, Jabalpur, Madhya Pradesh"),
    "jec": (23.1928, 79.9880, "JEC, Ranjhi, Jabalpur, Madhya Pradesh"),
    "jec ranjhi": (23.1928, 79.9880, "JEC Ranjhi, Jabalpur, Madhya Pradesh"),
    "gwalior": (26.2183, 78.1828, "Gwalior, Madhya Pradesh"),
    "ujjain": (23.1765, 75.7885, "Ujjain, Madhya Pradesh"),
    "rewa": (24.5373, 81.3042, "Rewa, Madhya Pradesh"),
    "sagar": (23.8388, 78.7378, "Sagar, Madhya Pradesh"),
    "bilaspur": (22.0797, 82.1409, "Bilaspur, Chhattisgarh"),
    "raipur": (21.2514, 81.6296, "Raipur, Chhattisgarh"),
    "durg": (21.1904, 81.2849, "Durg, Chhattisgarh"),
    "bhilai": (21.2121, 81.3733, "Bhilai, Chhattisgarh"),
    "rourkela": (22.2604, 84.8536, "Rourkela, Odisha"),
    "guwahati": (26.1445, 91.7362, "Guwahati, Assam"),
}


def geocode_location(query: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float, str]]:
    """Geocode a location query string into (lat, lng, display_name).
    
    Checks fast local dictionary first, then Open-Meteo Geocoding API (free, unmetered),
    then Google Geocoding (if key present), then OpenStreetMap Nominatim.
    """
    if not query or not query.strip():
        return None

    cleaned = query.strip().lower()

    # 1. Fast match in local dictionary
    for city_key, geo_data in INDIAN_CITIES_GEO.items():
        if city_key == cleaned or city_key in cleaned or cleaned in city_key:
            return geo_data

    # Check token overlap for academic campuses (e.g. "jec ranjhi" -> jec, ranjhi)
    tokens = [t.strip() for t in cleaned.replace(",", " ").split() if len(t.strip()) >= 3]
    for tok in tokens:
        if tok in INDIAN_CITIES_GEO:
            return INDIAN_CITIES_GEO[tok]

    # 2. Query Open-Meteo Geocoding API (100% free, reliable, no API key required)
    try:
        search_terms = [query.strip()] + [cleaned.replace("jec", "").strip()] + list(reversed(tokens))
        for term in search_terms:
            if not term or len(term) < 3:
                continue
            url = "https://geocoding-api.open-meteo.com/v1/search"
            res = requests.get(url, params={"name": term, "count": 1, "language": "en"}, timeout=3.5)
            if res.status_code == 200:
                data = res.json()
                results = data.get("results")
                if results and len(results) > 0:
                    first = results[0]
                    lat = float(first["latitude"])
                    lon = float(first["longitude"])
                    name = first.get("name", term.title())
                    admin1 = first.get("admin1", "")
                    country = first.get("country", "India")
                    display_name = f"{name}, {admin1}, {country}" if admin1 else f"{name}, {country}"
                    return lat, lon, display_name
    except Exception as e:
        logger.warning(f"Open-Meteo geocoding failed for '{query}': {e}")

    # 3. Try Google Geocoding API if key is present
    if not api_key:
        try:
            import os
            from flask import session, current_app
            api_key = session.get("google_maps_api_key") or current_app.config.get("GOOGLE_MAPS_API_KEY")
        except Exception:
            pass
    if not api_key:
        import os
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")

    if api_key and len(api_key.strip()) > 10:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {"address": query.strip(), "key": api_key.strip()}
            res = requests.get(url, params=params, timeout=4.0)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "OK" and data.get("results"):
                    first = data["results"][0]
                    loc = first.get("geometry", {}).get("location", {})
                    lat = float(loc.get("lat"))
                    lon = float(loc.get("lng"))
                    display_name = first.get("formatted_address", query)
                    short_name = ", ".join(display_name.split(",")[:3]).strip()
                    return lat, lon, short_name
        except Exception as e:
            logger.warning(f"Google Geocoding failed for '{query}': {e}")

    # 4. Try OpenStreetMap Nominatim API
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query.strip(),
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": "TifinifyApp/2.2 (contact: academic@tifinify.local)",
        }
        response = requests.get(url, params=params, headers=headers, timeout=3.5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                display_name = data[0].get("display_name", query)
                short_name = ", ".join(display_name.split(",")[:3]).strip()
                return lat, lon, short_name
    except Exception as e:
        logger.warning(f"Nominatim geocoding failed for '{query}': {e}")

    # 5. Fallback: return default central Indian coordinate if completely unrecognized
    return 23.1815, 79.9864, query.strip().title()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two geographic coordinates in kilometers.
    
    Uses standard Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(R * c, 2)


def get_bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """Calculate approximate min/max latitude and longitude for bounding-box database filtering."""
    # 1 deg latitude ~= 111.0 km
    lat_delta = radius_km / 111.0
    # 1 deg longitude ~= 111.0 km * cos(latitude)
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    return min_lat, max_lat, min_lon, max_lon
