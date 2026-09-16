from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models import db, login_manager


class User(UserMixin, db.Model):
    """Registered user model for consumers and admins."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'user', 'admin'
    dietary_preference = db.Column(db.String(30), nullable=True, default="all")  # 'veg', 'non-veg', 'jain', 'all'
    default_radius_km = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviews = db.relationship("Review", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    preferences = db.relationship("UserPreferences", backref="user", uselist=False, cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="reporter", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """Hash and set user password using secure scrypt/pbkdf2 algorithm."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "dietary_preference": self.dietary_preference,
            "default_radius_km": self.default_radius_km,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return db.session.get(User, int(user_id))


class UserPreferences(db.Model):
    """User search preferences and filtering defaults."""
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    budget_min = db.Column(db.Integer, nullable=True)
    budget_max = db.Column(db.Integer, nullable=True)
    max_distance_km = db.Column(db.Float, default=5.0)
    preferred_food_type = db.Column(db.String(30), nullable=True)  # 'veg', 'non-veg', 'both'
    preferred_category = db.Column(db.String(30), nullable=True)   # 'tiffin', 'mess', 'both'
    delivery_only = db.Column(db.Boolean, default=False)
    min_rating = db.Column(db.Float, default=3.5)
    min_trust_score = db.Column(db.Integer, default=70)

    def to_dict(self) -> dict:
        return {
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "max_distance_km": self.max_distance_km,
            "preferred_food_type": self.preferred_food_type,
            "preferred_category": self.preferred_category,
            "delivery_only": self.delivery_only,
            "min_rating": self.min_rating,
            "min_trust_score": self.min_trust_score,
        }
