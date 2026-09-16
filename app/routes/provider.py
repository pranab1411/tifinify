from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user
from app.models import Provider, Favorite
from app.services.provider_service import ProviderService
from app.utils.geo import geocode_location

provider_bp = Blueprint("provider", __name__)


@provider_bp.route("/discovery")
def discovery():
    """Interactive Provider Discovery page with cards, filtering, and map."""
    loc_query = request.args.get("location", "").strip()
    lat_str = request.args.get("lat")
    lon_str = request.args.get("lng")
    radius_str = request.args.get("radius", "5")
    category = request.args.get("category", "all")
    food_type = request.args.get("food_type", "all")
    min_rating = request.args.get("min_rating")
    min_trust = request.args.get("min_trust")
    max_price = request.args.get("max_price")
    sort_by = request.args.get("sort_by", "distance")

    user_lat = None
    user_lon = None

    # 1. If explicit GPS coordinates are provided in query params
    if lat_str and lon_str and lat_str.strip() and lon_str.strip():
        try:
            user_lat = float(lat_str)
            user_lon = float(lon_str)
            loc_query = loc_query or "Current Location (GPS)"
        except ValueError:
            pass

    # 2. If user requested "Current Location" or "GPS" without coordinates, check session coordinates
    if (user_lat is None or user_lon is None) and loc_query and any(k in loc_query.lower() for k in ("current location", "gps", "my location")):
        user_lat = session.get("user_lat")
        user_lon = session.get("user_lon")
        if user_lat is not None and user_lon is not None:
            loc_query = session.get("user_location") or "Current Location (GPS)"

    # 3. If user typed a specific locality / city name
    if (user_lat is None or user_lon is None) and loc_query and not any(k in loc_query.lower() for k in ("current location", "gps", "my location")):
        geo_result = geocode_location(loc_query)
        if geo_result:
            user_lat, user_lon, resolved_name = geo_result
            loc_query = resolved_name

    # 4. Fallback to existing session if no coordinates yet
    if user_lat is None or user_lon is None:
        user_lat = session.get("user_lat")
        user_lon = session.get("user_lon")
        loc_query = session.get("user_location")

    # 5. Default baseline fallback if completely unset
    if user_lat is None or user_lon is None:
        user_lat = 18.5679
        user_lon = 73.9143
        loc_query = "Viman Nagar, Pune"

    # Persist in session so subsequent page visits remember the user's location
    session["user_lat"] = user_lat
    session["user_lon"] = user_lon
    session["user_location"] = loc_query

    try:
        radius_km = float(radius_str)
    except ValueError:
        radius_km = 5.0

    # Execute search with adaptive localized seeding
    providers = ProviderService.search_providers(
        user_lat=user_lat,
        user_lon=user_lon,
        radius_km=radius_km,
        category=category,
        food_type=food_type,
        min_rating=float(min_rating) if min_rating else None,
        min_trust_score=int(min_trust) if min_trust else None,
        max_price=int(max_price) if max_price else None,
        sort_by=sort_by,
        location_name=loc_query,
    )

    # User favorite provider IDs for badge toggles
    user_fav_ids = set()
    if current_user.is_authenticated:
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        user_fav_ids = {f.provider_id for f in favs}

    return render_template(
        "provider/discovery.html",
        providers=providers,
        user_lat=user_lat,
        user_lon=user_lon,
        location_query=loc_query or "Viman Nagar, Pune",
        radius=int(radius_km),
        category=category,
        food_type=food_type,
        min_rating=min_rating or "",
        min_trust=min_trust or "",
        max_price=max_price or "",
        sort_by=sort_by,
        user_fav_ids=user_fav_ids,
    )


@provider_bp.route("/<int:provider_id>")
def details(provider_id: int):
    """Dedicated Provider Details page showing original rating, AI Trust Score, aspects, and reviews."""
    provider_data = ProviderService.get_provider_details(provider_id)
    if not provider_data:
        flash("Provider not found.", "warning")
        return redirect(url_for("provider.discovery"))

    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = bool(
            Favorite.query.filter_by(user_id=current_user.id, provider_id=provider_id).first()
        )

    return render_template(
        "provider/details.html",
        provider=provider_data,
        is_favorite=is_favorite,
    )


@provider_bp.route("/compare", methods=["GET", "POST"])
def compare():
    """Side-by-side comparison of two providers."""
    all_providers = Provider.query.filter_by(is_active=True).all()
    p1_id = request.args.get("p1", type=int)
    p2_id = request.args.get("p2", type=int)

    comparison_data = None
    if p1_id and p2_id:
        comparison_data = ProviderService.compare_providers(p1_id, p2_id)

    return render_template(
        "provider/compare.html",
        all_providers=[p.to_dict() for p in all_providers],
        p1_id=p1_id,
        p2_id=p2_id,
        comparison=comparison_data,
    )
