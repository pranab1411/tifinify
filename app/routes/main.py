from flask import Blueprint, render_template, request
from app.models import Provider

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing Page: Hero section, search input, how it works, and featured providers."""
    # Fetch a few featured providers for the landing page demonstration
    featured_providers = Provider.query.filter_by(is_active=True).order_by(
        Provider.review_trust_score.desc(),
        Provider.source_rating.desc()
    ).limit(3).all()

    return render_template(
        "main/index.html",
        featured_providers=[p.to_dict() for p in featured_providers],
    )


@main_bp.route("/about")
def about():
    """About Page: Project objectives, AI review intelligence principles, and disclaimer."""
    return render_template("main/about.html")
