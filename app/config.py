import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the tifinify package
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "tifinify-dev-secret-key-2026-mca")
    
    # Database
    db_path = BASE_DIR / "instance" / "tifinify.db"
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url and raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url or f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # External APIs
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    
    # Core Application Settings
    DEMO_MODE = os.environ.get("DEMO_MODE", "True").lower() in ("true", "1", "t", "yes")
    MAX_SEARCH_RADIUS_KM = float(os.environ.get("MAX_SEARCH_RADIUS_KM", "15.0"))
    CACHE_ANALYSIS_DAYS = int(os.environ.get("CACHE_ANALYSIS_DAYS", "7"))
    
    # Security / Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = 3600


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
