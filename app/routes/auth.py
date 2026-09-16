from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, UserPreferences, Favorite
from app.services.provider_service import ProviderService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        dietary_preference = request.form.get("dietary_preference", "all")

        if not name or not email or not password:
            flash("Please fill in all required fields.", "warning")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            name=name,
            email=email,
            dietary_preference=dietary_preference,
            role="user",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create default preferences
        pref = UserPreferences(
            user_id=user.id,
            preferred_food_type=dietary_preference if dietary_preference != "all" else None,
        )
        db.session.add(pref)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to Tifinify, {user.name}!", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate and create user session."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Terminate current user session."""
    logout_user()
    flash("You have been logged out safely.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and update profile & dietary preferences."""
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.dietary_preference = request.form.get("dietary_preference", current_user.dietary_preference)
        current_user.default_radius_km = float(request.form.get("default_radius_km", current_user.default_radius_km))

        db.session.commit()
        flash("Your profile preferences have been updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/favorites")
@login_required
def favorites():
    """List current user's saved favorite providers."""
    fav_records = Favorite.query.filter_by(user_id=current_user.id).all()
    favorite_providers = []
    for f in fav_records:
        details = ProviderService.get_provider_details(f.provider_id)
        if details:
            favorite_providers.append(details)

    return render_template("auth/favorites.html", favorites=favorite_providers)
