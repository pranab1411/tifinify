import json
from datetime import datetime
from app.models import db


class Review(db.Model):
    """Normalized customer review record."""
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source = db.Column(db.String(50), nullable=False, default="tifinify_user")  # 'google', 'tifinify_user', 'demo'
    external_review_id = db.Column(db.String(255), nullable=True, index=True)
    reviewer_name = db.Column(db.String(120), default="Anonymous")
    rating = db.Column(db.Float, nullable=False, index=True)  # 1.0 - 5.0
    review_text = db.Column(db.Text, nullable=False)
    clean_text = db.Column(db.Text, nullable=True)
    review_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    analysis = db.relationship("ReviewAnalysis", backref="review", uselist=False, cascade="all, delete-orphan")
    aspects = db.relationship("ReviewAspect", backref="review", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "provider_id": self.provider_id,
            "reviewer_name": self.reviewer_name,
            "source": self.source,
            "rating": self.rating,
            "review_text": self.review_text,
            "review_date": self.review_date.strftime("%b %d, %Y") if self.review_date else None,
        }
        if self.analysis:
            data["analysis"] = self.analysis.to_dict()
        if self.aspects:
            data["aspects"] = [a.to_dict() for a in self.aspects.all()]
        return data

    def __repr__(self) -> str:
        return f"<Review id={self.id} provider_id={self.provider_id} rating={self.rating}>"


class ReviewAnalysis(db.Model):
    """Granular algorithmic & AI trust analysis per review."""
    __tablename__ = "review_analysis"

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)  # 'positive', 'neutral', 'negative'
    sentiment_score = db.Column(db.Float, nullable=False, default=0.0)  # -1.0 to 1.0
    suspicion_level = db.Column(db.String(30), nullable=False, index=True)  # 'likely_authentic', 'potentially_suspicious', 'highly_suspicious'
    authenticity_score = db.Column(db.Integer, nullable=False, default=100)  # 0 to 100
    duplicate_similarity_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    rating_text_inconsistency = db.Column(db.Boolean, default=False)
    suspicious_signals = db.Column(db.Text, nullable=True)  # JSON list
    ai_notes = db.Column(db.Text, nullable=True)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_signals_list(self) -> list:
        if not self.suspicious_signals:
            return []
        try:
            return json.loads(self.suspicious_signals)
        except Exception:
            return [self.suspicious_signals]

    def set_signals_list(self, signals: list) -> None:
        self.suspicious_signals = json.dumps(signals)

    def to_dict(self) -> dict:
        return {
            "sentiment": self.sentiment,
            "sentiment_score": round(self.sentiment_score, 2),
            "suspicion_level": self.suspicion_level,
            "authenticity_score": self.authenticity_score,
            "duplicate_similarity_score": round(self.duplicate_similarity_score, 2),
            "rating_text_inconsistency": self.rating_text_inconsistency,
            "signals": self.get_signals_list(),
            "ai_notes": self.ai_notes,
        }


class ReviewAspect(db.Model):
    """Aspect-based sentiment analysis data point."""
    __tablename__ = "review_aspects"

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect = db.Column(db.String(50), nullable=False, index=True)  # 'taste', 'food_quality', 'hygiene', 'quantity', 'delivery', 'value_for_money'
    sentiment = db.Column(db.String(20), nullable=False)  # 'positive', 'neutral', 'negative'
    confidence = db.Column(db.Float, default=0.8)
    mention_snippet = db.Column(db.String(255), nullable=True)

    def to_dict(self) -> dict:
        return {
            "aspect": self.aspect,
            "sentiment": self.sentiment,
            "confidence": round(self.confidence, 2),
            "mention_snippet": self.mention_snippet,
        }
