import json
from datetime import datetime
from app.models import db


class ProviderAnalysisSummary(db.Model):
    """Cached aggregate AI & NLP review intelligence profile for a provider."""
    __tablename__ = "provider_analysis_summary"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Aggregated Trust Score (0 - 100)
    overall_trust_score = db.Column(db.Integer, nullable=False, default=100, index=True)
    trust_category = db.Column(db.String(30), nullable=False, default="likely_authentic")  # 'likely_authentic', 'potentially_suspicious', 'highly_suspicious'
    
    # Sentiment distribution percentages
    sentiment_positive_pct = db.Column(db.Float, default=0.0)
    sentiment_neutral_pct = db.Column(db.Float, default=0.0)
    sentiment_negative_pct = db.Column(db.Float, default=0.0)
    
    # Aspect-based sentiment scores (JSON dictionary, e.g. {"taste": 91.0, "hygiene": 82.0, ...})
    aspect_breakdown_json = db.Column(db.Text, nullable=True)
    
    # Grounded Gemini AI natural language summary
    ai_summary = db.Column(db.Text, nullable=True)
    
    # High-level detected signals (JSON list)
    detected_signals_json = db.Column(db.Text, nullable=True)
    
    # Counts
    total_analyzed_reviews = db.Column(db.Integer, default=0)
    suspicious_review_count = db.Column(db.Integer, default=0)
    last_analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_aspect_breakdown(self) -> dict:
        if not self.aspect_breakdown_json:
            return {}
        try:
            return json.loads(self.aspect_breakdown_json)
        except Exception:
            return {}

    def set_aspect_breakdown(self, breakdown: dict) -> None:
        self.aspect_breakdown_json = json.dumps(breakdown)

    def get_detected_signals(self) -> list:
        if not self.detected_signals_json:
            return []
        try:
            return json.loads(self.detected_signals_json)
        except Exception:
            return []

    def set_detected_signals(self, signals: list) -> None:
        self.detected_signals_json = json.dumps(signals)

    def to_dict(self) -> dict:
        return {
            "overall_trust_score": self.overall_trust_score,
            "trust_category": self.trust_category,
            "sentiment_distribution": {
                "positive": round(self.sentiment_positive_pct, 1),
                "neutral": round(self.sentiment_neutral_pct, 1),
                "negative": round(self.sentiment_negative_pct, 1),
            },
            "aspects": self.get_aspect_breakdown(),
            "ai_summary": self.ai_summary,
            "detected_signals": self.get_detected_signals(),
            "total_analyzed_reviews": self.total_analyzed_reviews,
            "suspicious_review_count": self.suspicious_review_count,
            "last_analyzed_at": self.last_analyzed_at.strftime("%b %d, %Y %H:%M") if self.last_analyzed_at else None,
        }

    def __repr__(self) -> str:
        return f"<ProviderAnalysisSummary provider_id={self.provider_id} score={self.overall_trust_score}>"
