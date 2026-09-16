import logging
from typing import Dict, Any, List
from datetime import datetime
from app.models import db, Review, ReviewAnalysis, ReviewAspect, Provider, ProviderAnalysisSummary
from app.ai.trust_engine import ReviewTrustEngine

logger = logging.getLogger(__name__)


class ReviewService:
    """Service to handle review ingestion and orchestrate the AI trust analysis pipeline."""

    @staticmethod
    def add_review(
        provider_id: int,
        rating: float,
        review_text: str,
        reviewer_name: str = "Anonymous",
        user_id: int = None,
        source: str = "tifinify_user",
        review_date: datetime = None,
    ) -> Review:
        """Create a new review and immediately trigger provider re-analysis."""
        review = Review(
            provider_id=provider_id,
            user_id=user_id,
            source=source,
            reviewer_name=reviewer_name or "Anonymous",
            rating=float(rating),
            review_text=review_text.strip(),
            review_date=review_date or datetime.utcnow(),
        )
        db.session.add(review)
        db.session.commit()

        # Re-run pipeline for this provider to update Trust Score and aspect profiles
        ReviewService.analyze_provider(provider_id)
        return review

    @staticmethod
    def analyze_provider(provider_id: int) -> Dict[str, Any]:
        """Run complete AI review analysis pipeline for a provider and persist results."""
        provider = db.session.get(Provider, provider_id)
        if not provider:
            return {}

        reviews = Review.query.filter_by(provider_id=provider_id).all()
        reviews_data = [
            {
                "id": r.id,
                "rating": r.rating,
                "review_text": r.review_text,
                "review_date": r.review_date,
            }
            for r in reviews
        ]

        engine = ReviewTrustEngine()
        analysis_result = engine.analyze_provider_reviews(
            provider_name=provider.name,
            reviews_data=reviews_data,
        )

        # 1. Update/Create individual review analysis records
        per_review = analysis_result["per_review_analysis"]
        for r in reviews:
            rev_res = per_review.get(r.id)
            if not rev_res:
                continue

            r.clean_text = rev_res.get("clean_text")

            # Check if analysis record exists
            analysis_record = ReviewAnalysis.query.filter_by(review_id=r.id).first()
            if not analysis_record:
                analysis_record = ReviewAnalysis(review_id=r.id)
                db.session.add(analysis_record)

            analysis_record.sentiment = rev_res["sentiment"]
            analysis_record.sentiment_score = rev_res["sentiment_score"]
            analysis_record.suspicion_level = rev_res["suspicion_level"]
            analysis_record.authenticity_score = rev_res["authenticity_score"]
            analysis_record.duplicate_similarity_score = rev_res["duplicate_similarity_score"]
            analysis_record.rating_text_inconsistency = rev_res["rating_text_inconsistency"]
            analysis_record.set_signals_list(rev_res["signals"])
            analysis_record.analyzed_at = datetime.utcnow()

            # Clear old aspects and insert newly extracted
            ReviewAspect.query.filter_by(review_id=r.id).delete()
            for asp in rev_res.get("aspects", []):
                aspect_row = ReviewAspect(
                    review_id=r.id,
                    provider_id=provider_id,
                    aspect=asp["aspect"],
                    sentiment=asp["sentiment"],
                    confidence=asp["confidence"],
                    mention_snippet=asp["mention_snippet"],
                )
                db.session.add(aspect_row)

        # 2. Update Provider top-level fields
        provider.review_trust_score = analysis_result["overall_trust_score"]
        provider.trust_badge = analysis_result["trust_category"]
        if reviews:
            provider.source_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
            provider.source_review_count = len(reviews)

        # 3. Update ProviderAnalysisSummary cache
        summary = ProviderAnalysisSummary.query.filter_by(provider_id=provider_id).first()
        if not summary:
            summary = ProviderAnalysisSummary(provider_id=provider_id)
            db.session.add(summary)

        summary.overall_trust_score = analysis_result["overall_trust_score"]
        summary.trust_category = analysis_result["trust_category"]
        summary.sentiment_positive_pct = analysis_result["sentiment_distribution"]["positive"]
        summary.sentiment_neutral_pct = analysis_result["sentiment_distribution"]["neutral"]
        summary.sentiment_negative_pct = analysis_result["sentiment_distribution"]["negative"]
        summary.set_aspect_breakdown(analysis_result["aspect_scores"])
        summary.ai_summary = analysis_result["ai_summary"]
        summary.set_detected_signals([s["text"] for s in analysis_result["transparent_signals"]])
        summary.total_analyzed_reviews = analysis_result["total_analyzed_reviews"]
        summary.suspicious_review_count = analysis_result["suspicious_review_count"]
        summary.last_analyzed_at = datetime.utcnow()

        db.session.commit()
        return analysis_result
