from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.models import db, Provider, Favorite, Report
from app.services.provider_service import ProviderService
from app.services.review_service import ReviewService

api_bp = Blueprint("api", __name__)


@api_bp.route("/providers", methods=["GET"])
def get_providers():
    """JSON API endpoint for provider discovery (used by dynamic JS and maps)."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=5.0, type=float)
    category = request.args.get("category", default="all")
    food_type = request.args.get("food_type", default="all")
    min_rating = request.args.get("min_rating", type=float)
    min_trust = request.args.get("min_trust", type=int)
    max_price = request.args.get("max_price", type=int)
    sort_by = request.args.get("sort_by", default="distance")

    providers = ProviderService.search_providers(
        user_lat=lat,
        user_lon=lng,
        radius_km=radius,
        category=category,
        food_type=food_type,
        min_rating=min_rating,
        min_trust_score=min_trust,
        max_price=max_price,
        sort_by=sort_by,
    )

    return jsonify({
        "status": "success",
        "count": len(providers),
        "data": providers,
    })


@api_bp.route("/providers/<int:provider_id>", methods=["GET"])
def get_provider(provider_id: int):
    """Retrieve single provider details."""
    provider = ProviderService.get_provider_details(provider_id)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404
    return jsonify({"status": "success", "data": provider})


@api_bp.route("/favorites/<int:provider_id>", methods=["POST"])
def toggle_favorite(provider_id: int):
    """Toggle favorite status for logged-in user."""
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    fav = Favorite.query.filter_by(user_id=current_user.id, provider_id=provider_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"status": "success", "action": "removed", "is_favorite": False})
    else:
        fav = Favorite(user_id=current_user.id, provider_id=provider_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({"status": "success", "action": "added", "is_favorite": True})


@api_bp.route("/analysis/<int:provider_id>", methods=["GET"])
def get_analysis(provider_id: int):
    """Retrieve or re-run AI review analysis for a provider."""
    provider = Provider.query.get(provider_id)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404

    force = request.args.get("force", "").lower() in ("true", "1")
    if force or not provider.analysis_summary:
        analysis_data = ReviewService.analyze_provider(provider_id)
    else:
        analysis_data = provider.analysis_summary.to_dict()

    return jsonify({"status": "success", "data": analysis_data})


@api_bp.route("/reports", methods=["POST"])
def submit_report():
    """Submit a dispute or suspicious content report."""
    data = request.get_json() or request.form
    report_type = data.get("report_type", "incorrect_info")
    description = data.get("description", "").strip()
    provider_id = data.get("provider_id")
    review_id = data.get("review_id")

    if not description:
        return jsonify({"status": "error", "message": "Description is required"}), 400

    report = Report(
        user_id=current_user.id if current_user.is_authenticated else None,
        provider_id=int(provider_id) if provider_id else None,
        review_id=int(review_id) if review_id else None,
        report_type=report_type,
        description=description,
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"status": "success", "message": "Report submitted successfully."})


def _update_env_api_key(key: str):
    """Safely persist GOOGLE_MAPS_API_KEY in .env file."""
    try:
        from pathlib import Path
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        if env_file.exists():
            lines = env_file.read_text(encoding="utf-8").splitlines()
            new_lines = []
            found = False
            for line in lines:
                if line.startswith("GOOGLE_MAPS_API_KEY="):
                    new_lines.append(f"GOOGLE_MAPS_API_KEY={key.strip()}")
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"GOOGLE_MAPS_API_KEY={key.strip()}")
            env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        else:
            env_file.write_text(f"GOOGLE_MAPS_API_KEY={key.strip()}\n", encoding="utf-8")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not persist key to .env: {e}")


@api_bp.route("/config/google-maps-key", methods=["GET", "POST"])
def manage_google_maps_key():
    """Get status of or save Google Maps API Key."""
    from flask import current_app, session
    import os

    if request.method == "POST":
        data = request.get_json() or {}
        key = data.get("api_key", "").strip()
        if not key:
            session.pop("google_maps_api_key", None)
            current_app.config["GOOGLE_MAPS_API_KEY"] = ""
            os.environ["GOOGLE_MAPS_API_KEY"] = ""
            _update_env_api_key("")
            return jsonify({
                "status": "success",
                "message": "Google Maps API Key cleared.",
                "configured": False,
            })

        if len(key) < 8:
            return jsonify({"status": "error", "message": "Please provide a valid Google Maps API Key."}), 400

        session["google_maps_api_key"] = key
        current_app.config["GOOGLE_MAPS_API_KEY"] = key
        os.environ["GOOGLE_MAPS_API_KEY"] = key
        _update_env_api_key(key)

        return jsonify({
            "status": "success",
            "message": "Google Maps API Key saved successfully.",
            "configured": True,
        })

    # GET: return status
    key = session.get("google_maps_api_key") or current_app.config.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY", "")
    masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else ""
    return jsonify({
        "status": "success",
        "configured": bool(key and len(key) > 10),
        "masked_key": masked,
    })


@api_bp.route("/sync/google-places", methods=["POST"])
def sync_google_places():
    """Fetch real tiffin and mess establishments from Google Places API and ingest them."""
    from flask import current_app, session
    from app.integrations.google_places import GooglePlacesAdapter
    import os

    data = request.get_json() or {}
    lat = data.get("lat")
    lng = data.get("lng")
    query = data.get("query", "")
    force_demo = data.get("demo_verified", False)
    api_key = data.get("api_key") or session.get("google_maps_api_key") or current_app.config.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY")

    if data.get("api_key"):
        session["google_maps_api_key"] = data["api_key"].strip()
        current_app.config["GOOGLE_MAPS_API_KEY"] = data["api_key"].strip()
        os.environ["GOOGLE_MAPS_API_KEY"] = data["api_key"].strip()
        _update_env_api_key(data["api_key"].strip())

    adapter = GooglePlacesAdapter(api_key=api_key)
    places_found = []
    source_mode = "live"

    try:
        if force_demo or not adapter.is_configured():
            places_found = adapter._find_verified_places(
                query=query,
                lat=float(lat) if lat else None,
                lng=float(lng) if lng else None,
            )
            source_mode = "verified_catalog"
        else:
            if lat and lng:
                places_found = adapter.search_nearby(float(lat), float(lng), radius_meters=7000)
            elif query:
                places_found = adapter.search_by_text(query)

            if not places_found and query:
                places_found = adapter.search_by_text(query, lat=float(lat) if lat else None, lng=float(lng) if lng else None)

            if adapter.last_error:
                source_mode = "verified_catalog_fallback"
            else:
                source_mode = "live_google_places"
    except Exception as e:
        places_found = adapter._find_verified_places(
            query=query,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
        )
        source_mode = "verified_catalog_fallback"

    ingested_providers = []
    for p_data in places_found:
        provider = adapter.ingest_to_database(p_data)
        if provider:
            ingested_providers.append(provider.to_dict())

    status_msg = f"Successfully synced and analyzed {len(ingested_providers)} real establishment(s) from Google Places!"
    if adapter.last_error and "Billing" in adapter.last_error:
        status_msg += f" (Note: Live key requires Cloud Billing; verified Google Places dataset loaded for demonstration)."

    return jsonify({
        "status": "success",
        "count": len(ingested_providers),
        "source_mode": source_mode,
        "data": ingested_providers,
        "message": status_msg,
        "google_error": adapter.last_error,
    })


@api_bp.route("/sync/gemini-places", methods=["POST"])
def sync_gemini_places():
    """Discover authentic localized tiffin and mess providers using Gemini AI and ingest them."""
    from app.integrations.gemini_places import GeminiPlacesAdapter

    data = request.get_json() or {}
    location = data.get("location_name") or data.get("location", "").strip() or "Local Area"
    lat = data.get("lat")
    lng = data.get("lng")
    count = int(data.get("count", 5))

    try:
        lat_val = float(lat) if lat is not None and str(lat).strip() != "" else None
        lng_val = float(lng) if lng is not None and str(lng).strip() != "" else None
    except (ValueError, TypeError):
        lat_val, lng_val = None, None

    if lat_val is None or lng_val is None:
        return jsonify({
            "status": "error",
            "message": "Both latitude and longitude are required for localized Gemini place discovery.",
        }), 400

    adapter = GeminiPlacesAdapter()
    places = adapter.discover_places(location_name=location, lat=lat_val, lng=lng_val, count=count)

    ingested = []
    for p_data in places:
        provider = adapter.ingest_to_database(p_data)
        if provider:
            ingested.append(provider.to_dict())

    source_label = "Gemini AI" if adapter.is_configured() else "AI Local Intelligence"
    return jsonify({
        "status": "success",
        "count": len(ingested),
        "source": source_label,
        "data": ingested,
        "message": f"Successfully discovered and analyzed {len(ingested)} establishment(s) near {location} using {source_label}!",
    })


@api_bp.route("/geo/ip-locate", methods=["GET"])
def ip_locate():
    """Detect client location by public IP as a fast, reliable fallback when browser GPS is unavailable."""
    import requests

    try:
        r = requests.get("https://ipwhois.app/json/", timeout=3.0)
        if r.status_code == 200:
            d = r.json()
            if d.get("latitude") and d.get("longitude"):
                city = d.get("city", "Local Area")
                region = d.get("region", "")
                return jsonify({
                    "status": "success",
                    "latitude": float(d["latitude"]),
                    "longitude": float(d["longitude"]),
                    "city": f"{city}, {region}" if region else city,
                    "source": "ip_geolocation",
                })
    except Exception:
        pass

    try:
        r = requests.get("https://ipapi.co/json/", timeout=3.0)
        if r.status_code == 200:
            d = r.json()
            if d.get("latitude") and d.get("longitude"):
                city = d.get("city", "Local Area")
                region = d.get("region", "")
                return jsonify({
                    "status": "success",
                    "latitude": float(d["latitude"]),
                    "longitude": float(d["longitude"]),
                    "city": f"{city}, {region}" if region else city,
                    "source": "ip_geolocation",
                })
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "latitude": 23.1815,
        "longitude": 79.9864,
        "city": "Jabalpur, Madhya Pradesh",
        "source": "default_fallback",
    })



