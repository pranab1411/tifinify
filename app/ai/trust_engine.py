import logging
from typing import List, Dict, Any, Tuple
from app.ai.cleaner import clean_review_text
from app.ai.similarity import ReviewSimilarityDetector
from app.ai.heuristics import ReviewHeuristicsAnalyzer
from app.ai.aspect_extractor import AspectSentimentExtractor
from app.ai.gemini_client import GeminiAnalysisClient

logger = logging.getLogger(__name__)


class ReviewTrustEngine:
    """Core Review Intelligence and Trust Score Engine for Tifinify.
    
    Orchestrates:
    - Text normalization
    - Exact & TF-IDF Cosine similarity detection
    - Rating-sentiment inconsistency & burst heuristics
    - Aspect-based sentiment analysis
    - Gemini AI natural-language synthesis
    - Deterministic, explainable Review Trust Score calculation (0 - 100)
    """

    def __init__(self, gemini_api_key: str = None):
        self.similarity_detector = ReviewSimilarityDetector(near_duplicate_threshold=0.82)
        self.heuristics_analyzer = ReviewHeuristicsAnalyzer()
        self.aspect_extractor = AspectSentimentExtractor()
        self.gemini_client = GeminiAnalysisClient(api_key=gemini_api_key)

    def analyze_provider_reviews(
        self,
        provider_name: str,
        reviews_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive trust analysis across all reviews of a provider.
        
        Args:
            provider_name: Display name of the tiffin/mess service
            reviews_data: List of dicts containing 'id', 'rating', 'review_text', 'review_date'
            
        Returns:
            Dict containing:
                - overall_trust_score: int (0 to 100)
                - trust_category: 'likely_authentic' | 'potentially_suspicious' | 'highly_suspicious'
                - sentiment_distribution: {'positive': float, 'neutral': float, 'negative': float}
                - aspect_scores: {'taste': float, 'hygiene': float, ...}
                - ai_summary: str
                - transparent_signals: List[Dict[str, Any]] (type: 'positive' | 'warning', text: str)
                - per_review_analysis: Dict[review_id, Dict[str, Any]]
                - total_analyzed_reviews: int
                - suspicious_review_count: int
        """
        n = len(reviews_data)
        if n == 0:
            return {
                "overall_trust_score": 100,
                "trust_category": "likely_authentic",
                "sentiment_distribution": {"positive": 0.0, "neutral": 100.0, "negative": 0.0},
                "aspect_scores": {},
                "ai_summary": "Not enough review data to generate a reliable summary.",
                "transparent_signals": [
                    {"type": "info", "text": "No customer reviews submitted yet."}
                ],
                "per_review_analysis": {},
                "total_analyzed_reviews": 0,
                "suspicious_review_count": 0,
            }

        # 1. Similarity Analysis (Exact & TF-IDF Near-Duplicates)
        sim_results = self.similarity_detector.analyze_provider_reviews(reviews_data)
        per_review_sim = sim_results["per_review_max_sim"]
        duplicate_penalty = sim_results["duplicate_penalty"]

        # 2. Heuristic Analysis per review
        per_review_analysis = {}
        inconsistency_count = 0
        sentiment_tallies = {"positive": 0, "neutral": 0, "negative": 0}
        all_extracted_aspects = []
        suspicious_reviews_count = 0

        for r in reviews_data:
            r_id = r["id"]
            rating = float(r.get("rating", 3.0))
            text = r.get("review_text", "")
            clean = clean_review_text(text)

            heuristic_res = self.heuristics_analyzer.analyze_single_review(rating, clean)
            sim_score = per_review_sim.get(r_id, 0.0)

            # Integrate similarity penalty into individual review authenticity
            review_auth_score = heuristic_res["authenticity_score"]
            review_signals = list(heuristic_res["signals"])

            if sim_score >= 0.82:
                review_auth_score -= int(sim_score * 40)
                review_signals.append("high_text_similarity_with_another_review")

            review_auth_score = max(0, min(100, review_auth_score))

            if review_auth_score >= 80:
                suspicion_level = "likely_authentic"
            elif review_auth_score >= 50:
                suspicion_level = "potentially_suspicious"
                suspicious_reviews_count += 1
            else:
                suspicion_level = "highly_suspicious"
                suspicious_reviews_count += 1

            if heuristic_res["rating_inconsistency"]:
                inconsistency_count += 1

            sentiment_tallies[heuristic_res["sentiment"]] += 1

            # Extract aspects
            aspects = self.aspect_extractor.extract_aspects_from_text(clean)
            all_extracted_aspects.extend(aspects)

            per_review_analysis[r_id] = {
                "sentiment": heuristic_res["sentiment"],
                "sentiment_score": heuristic_res["sentiment_score"],
                "suspicion_level": suspicion_level,
                "authenticity_score": review_auth_score,
                "duplicate_similarity_score": sim_score,
                "rating_text_inconsistency": heuristic_res["rating_inconsistency"],
                "signals": review_signals,
                "aspects": aspects,
                "clean_text": clean,
            }

        # 3. Behavioral Temporal Burst & Polarization Checks
        pattern_res = self.heuristics_analyzer.analyze_provider_bursts_and_polarization(reviews_data)
        burst_penalty = pattern_res["burst_penalty"]
        polarization_penalty = pattern_res["polarization_penalty"]

        # Inconsistency penalty scaled
        inconsistency_penalty = min(100.0, (inconsistency_count / max(1, n)) * 120.0)

        # 4. Overall Review Trust Score Calculation
        # Weights: Duplicate (0.35), Inconsistency (0.30), Burst (0.20), Polarization (0.15)
        total_penalty = (
            (duplicate_penalty * 0.35) +
            (inconsistency_penalty * 0.30) +
            (burst_penalty * 0.20) +
            (polarization_penalty * 0.15)
        )
        trust_score = max(0, int(round(100.0 - min(100.0, total_penalty))))

        if trust_score >= 80:
            trust_category = "likely_authentic"
        elif trust_score >= 50:
            trust_category = "potentially_suspicious"
        else:
            trust_category = "highly_suspicious"

        # 5. Aspect-Based Sentiments & Aggregation
        aspect_scores = self.aspect_extractor.aggregate_aspects(all_extracted_aspects)

        # 6. Sentiment Distribution Percentages
        pos_pct = round((sentiment_tallies["positive"] / n) * 100.0, 1)
        neu_pct = round((sentiment_tallies["neutral"] / n) * 100.0, 1)
        neg_pct = round((sentiment_tallies["negative"] / n) * 100.0, 1)

        sentiment_distribution = {
            "positive": pos_pct,
            "neutral": neu_pct,
            "negative": neg_pct,
        }

        # 7. Grounded AI Summary
        ai_summary = self.gemini_client.generate_review_summary(
            provider_name=provider_name,
            reviews=reviews_data,
            aspect_scores=aspect_scores,
            sentiment_pcts=sentiment_distribution,
        )

        # 8. Human-Readable Explainable Signals Checklist
        transparent_signals = []
        if sim_results["near_duplicate_count"] == 0 and sim_results["exact_duplicate_count"] == 0:
            transparent_signals.append({"type": "positive", "text": "Diverse review wording with low similarity"})
        else:
            count = sim_results["near_duplicate_count"] + sim_results["exact_duplicate_count"]
            transparent_signals.append({"type": "warning", "text": f"{count} highly similar or repeated review phrase(s) detected"})

        if inconsistency_count == 0:
            transparent_signals.append({"type": "positive", "text": "Normal rating and textual sentiment consistency"})
        else:
            transparent_signals.append({"type": "warning", "text": f"{inconsistency_count} review(s) with rating-content sentiment conflict"})

        if not pattern_res["burst_detected"]:
            transparent_signals.append({"type": "positive", "text": "Organic submission intervals over time"})
        else:
            transparent_signals.append({"type": "warning", "text": "Temporal review burst detected within a 48-hour window"})

        if not pattern_res["polarization_detected"]:
            transparent_signals.append({"type": "positive", "text": "Balanced rating distribution curve"})
        else:
            transparent_signals.append({"type": "warning", "text": "Bimodal rating polarization (skewed 5-star vs 1-star)"})

        return {
            "overall_trust_score": trust_score,
            "trust_category": trust_category,
            "sentiment_distribution": sentiment_distribution,
            "aspect_scores": aspect_scores,
            "ai_summary": ai_summary,
            "transparent_signals": transparent_signals,
            "per_review_analysis": per_review_analysis,
            "total_analyzed_reviews": n,
            "suspicious_review_count": suspicious_reviews_count,
        }
