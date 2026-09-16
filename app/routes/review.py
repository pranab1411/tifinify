from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import Provider
from app.services.review_service import ReviewService

review_bp = Blueprint("review", __name__)


@review_bp.route("/<int:provider_id>/new", methods=["GET", "POST"])
def submit_review(provider_id: int):
    """User review submission page."""
    provider = Provider.query.get_or_404(provider_id)

    if request.method == "POST":
        rating_str = request.form.get("rating", "5.0")
        review_text = request.form.get("review_text", "").strip()
        reviewer_name = request.form.get("reviewer_name", "").strip()

        if not review_text:
            flash("Please enter your review text.", "warning")
            return render_template("review/submit_review.html", provider=provider)

        try:
            rating = float(rating_str)
        except ValueError:
            rating = 5.0

        user_id = current_user.id if current_user.is_authenticated else None
        if current_user.is_authenticated and not reviewer_name:
            reviewer_name = current_user.name

        ReviewService.add_review(
            provider_id=provider.id,
            rating=rating,
            review_text=review_text,
            reviewer_name=reviewer_name or "Anonymous",
            user_id=user_id,
            source="tifinify_user",
        )

        flash("Your review has been submitted and evaluated by the Review Intelligence Engine!", "success")
        return redirect(url_for("provider.details", provider_id=provider.id))

    return render_template("review/submit_review.html", provider=provider)
