import os
from datetime import datetime, timezone
from flask import Flask, render_template
from app.config import config_by_name
from app.models import db, login_manager


def create_app(config_name: str = None) -> Flask:
    """Application factory for Tifinify."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure the instance directory exists for SQLite
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.provider import provider_bp
    from app.routes.review import review_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(provider_bp, url_prefix="/providers")
    app.register_blueprint(review_bp, url_prefix="/reviews")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Global template context
    @app.context_processor
    def inject_globals():
        from flask import session
        api_key = session.get("google_maps_api_key") or app.config.get("GOOGLE_MAPS_API_KEY", "") or os.environ.get("GOOGLE_MAPS_API_KEY", "")
        return {
            "current_year": datetime.now(timezone.utc).year,
            "demo_mode": app.config.get("DEMO_MODE", True),
            "google_maps_api_key": api_key,
        }

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html", error=error), 500

    # Auto-create tables in development mode
    with app.app_context():
        db.create_all()

    return app
