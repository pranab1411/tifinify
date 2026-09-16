from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this feature."
login_manager.login_message_category = "info"

# Import models for clean centralized access
from app.models.user import User, UserPreferences
from app.models.provider import Provider, ProviderSource
from app.models.review import Review, ReviewAnalysis, ReviewAspect
from app.models.analysis_summary import ProviderAnalysisSummary
from app.models.favorite import Favorite
from app.models.report import Report, AdminAuditLog

__all__ = [
    "db",
    "login_manager",
    "User",
    "UserPreferences",
    "Provider",
    "ProviderSource",
    "Review",
    "ReviewAnalysis",
    "ReviewAspect",
    "ProviderAnalysisSummary",
    "Favorite",
    "Report",
    "AdminAuditLog",
]
