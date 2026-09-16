from datetime import datetime
from app.models import db


class Provider(db.Model):
    """Tiffin or Mess Service provider model."""
    __tablename__ = "providers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(30), nullable=False, index=True)  # 'tiffin', 'mess', 'both'
    food_type = db.Column(db.String(30), nullable=False, index=True)  # 'veg', 'non-veg', 'both', 'jain_available'
    meal_types = db.Column(db.String(50), nullable=False, default="both")  # 'lunch', 'dinner', 'both'
    
    # Location coordinates & address
    address = db.Column(db.Text, nullable=False)
    locality = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False, index=True)
    longitude = db.Column(db.Float, nullable=False, index=True)
    
    # Contact & Operational Details
    phone = db.Column(db.String(30), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    opening_hours = db.Column(db.Text, nullable=True)
    price_per_month = db.Column(db.Integer, nullable=True, index=True)
    price_per_meal = db.Column(db.Integer, nullable=True)
    delivery_available = db.Column(db.Boolean, default=True, index=True)
    pickup_available = db.Column(db.Boolean, default=True)
    
    # Rating & AI Trust Metrics
    source_rating = db.Column(db.Float, default=0.0, index=True)  # External/platform rating
    source_review_count = db.Column(db.Integer, default=0)
    review_trust_score = db.Column(db.Integer, default=0, index=True)  # Tifinify Trust Score 0-100
    trust_badge = db.Column(db.String(30), default="unrated", index=True)  # 'likely_authentic', 'potentially_suspicious', 'highly_suspicious', 'unrated'
    
    # Status & Flags
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sources = db.relationship("ProviderSource", backref="provider", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="provider", lazy="dynamic", cascade="all, delete-orphan")
    analysis_summary = db.relationship("ProviderAnalysisSummary", backref="provider", uselist=False, cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="provider", lazy="dynamic", cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="provider", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_reviews: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            "food_type": self.food_type,
            "meal_types": self.meal_types,
            "address": self.address,
            "locality": self.locality,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "website": self.website,
            "opening_hours": self.opening_hours,
            "price_per_month": self.price_per_month,
            "price_per_meal": self.price_per_meal,
            "delivery_available": self.delivery_available,
            "pickup_available": self.pickup_available,
            "source_rating": self.source_rating,
            "source_review_count": self.source_review_count,
            "review_trust_score": self.review_trust_score,
            "trust_badge": self.trust_badge,
            "is_active": self.is_active,
            "is_demo": self.is_demo,
        }
        if self.analysis_summary:
            data["analysis"] = self.analysis_summary.to_dict()
        if include_reviews:
            data["reviews"] = [r.to_dict() for r in self.reviews.order_by(db.desc("review_date")).all()]
        return data

    def __repr__(self) -> str:
        return f"<Provider {self.name} ({self.locality})>"


class ProviderSource(db.Model):
    """Upstream source tracking (e.g. Google Places, user submission, seed)."""
    __tablename__ = "provider_sources"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # 'google_places', 'manual_user', 'seed_demo'
    external_id = db.Column(db.String(255), nullable=True, index=True)
    raw_metadata = db.Column(db.Text, nullable=True)  # JSON payload
    last_synced_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProviderSource {self.source_type} for Provider {self.provider_id}>"
