from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import Provider, Review, ReviewAnalysis, User, Report

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    """Admin Dashboard showing system metrics and audit stats."""
    if not current_user.is_admin:
        abort(403)

    total_providers = Provider.query.count()
    total_reviews = Review.query.count()
    suspicious_reviews = ReviewAnalysis.query.filter(
        ReviewAnalysis.suspicion_level.in_(["potentially_suspicious", "highly_suspicious"])
    ).count()
    total_users = User.query.count()
    pending_reports = Report.query.filter_by(status="pending").count()

    providers = Provider.query.order_by(Provider.created_at.desc()).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_providers=total_providers,
        total_reviews=total_reviews,
        suspicious_reviews=suspicious_reviews,
        total_users=total_users,
        pending_reports=pending_reports,
        providers=[p.to_dict() for p in providers],
    )
