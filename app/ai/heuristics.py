import re
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ReviewHeuristicsAnalyzer:
    """Heuristic rule engine to detect anomalous behavioral and textual review patterns."""

    # Lexicons for fast heuristic sentiment checks
    STRONG_POSITIVE_WORDS = {
        "amazing", "excellent", "superb", "delicious", "fantastic", "awesome",
        "best", "loved", "tasty", "fresh", "hygienic", "perfect", "mouthwatering",
        "wonderful", "great", "authentic", "homely"
    }

    STRONG_NEGATIVE_WORDS = {
        "worst", "terrible", "horrible", "stale", "spoiled", "unhygienic",
        "disgusting", "pathetic", "raw", "inedible", "rude", "cold", "late",
        "smelly", "hair", "insect", "cockroach", "fraud", "waste"
    }

    # Promotional and generic marketing phrases
    PROMOTIONAL_PATTERNS = [
        r"\b(?:call\s+(?:now|today|us)|contact\s+(?:us|at|now))\b",
        r"\b(?:best\s+(?:tiffin|mess|service)\s+in\s+(?:the\s+)?city|guaranteed\s+satisfaction)\b",
        r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # Phone numbers
        r"\b(?:visit\s+(?:our\s+)?website|order\s+now\s+for\s+discount)\b",
        r"\b(?:100%\s+satisfaction|cheapest\s+rates)\b",
    ]

    def analyze_single_review(self, rating: float, text: str) -> Dict[str, Any]:
        """Analyze individual review for contradictions and promotional phrasing."""
        lower_text = text.lower()
        words = set(re.findall(r"\b[a-z]{3,}\b", lower_text))

        pos_count = len(words.intersection(self.STRONG_POSITIVE_WORDS))
        neg_count = len(words.intersection(self.STRONG_NEGATIVE_WORDS))

        # Basic sentiment determination
        if pos_count > neg_count:
            sentiment = "positive"
            sentiment_score = min(1.0, 0.3 + (pos_count * 0.2))
        elif neg_count > pos_count:
            sentiment = "negative"
            sentiment_score = max(-1.0, -0.3 - (neg_count * 0.2))
        else:
            sentiment = "neutral"
            sentiment_score = 0.0

        # Rating-Content Inconsistency
        rating_inconsistency = False
        signals = []

        if rating <= 2.0 and pos_count >= 2 and neg_count == 0:
            rating_inconsistency = True
            signals.append("low_rating_positive_text_mismatch")
        elif rating >= 4.5 and neg_count >= 2 and pos_count == 0:
            rating_inconsistency = True
            signals.append("high_rating_negative_text_mismatch")

        # Promotional language check
        has_promotional = False
        for pattern in self.PROMOTIONAL_PATTERNS:
            if re.search(pattern, lower_text):
                has_promotional = True
                signals.append("promotional_or_advertisement_wording")
                break

        # Compute authenticity score for this single review (100 is cleanest)
        authenticity_score = 100
        if rating_inconsistency:
            authenticity_score -= 40
        if has_promotional:
            authenticity_score -= 25

        if authenticity_score >= 80:
            suspicion_level = "likely_authentic"
        elif authenticity_score >= 50:
            suspicion_level = "potentially_suspicious"
        else:
            suspicion_level = "highly_suspicious"

        return {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "rating_inconsistency": rating_inconsistency,
            "has_promotional": has_promotional,
            "signals": signals,
            "authenticity_score": max(0, authenticity_score),
            "suspicion_level": suspicion_level,
        }

    def analyze_provider_bursts_and_polarization(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Examine review timestamps and distribution across a provider's reviews."""
        n = len(reviews)
        if n < 3:
            return {
                "burst_detected": False,
                "polarization_detected": False,
                "burst_penalty": 0.0,
                "polarization_penalty": 0.0,
                "signals": [],
            }

        signals = []
        burst_penalty = 0.0
        polarization_penalty = 0.0

        # 1. Temporal Burst Detection
        dates = []
        for r in reviews:
            d = r.get("review_date")
            if isinstance(d, datetime):
                dates.append(d)
            elif isinstance(d, str):
                try:
                    dates.append(datetime.fromisoformat(d.replace("Z", "+00:00")))
                except Exception:
                    pass

        burst_detected = False
        if len(dates) >= 4:
            dates.sort()
            # Check if > 50% of reviews were submitted within any 48-hour rolling window
            window = timedelta(days=2)
            max_in_window = 0
            for i in range(len(dates)):
                in_win = sum(1 for d in dates if dates[i] <= d <= dates[i] + window)
                if in_win > max_in_window:
                    max_in_window = in_win

            if max_in_window / len(dates) >= 0.50:
                burst_detected = True
                burst_penalty = 30.0
                signals.append("temporal_review_burst_detected")

        # 2. Rating Polarization (Bimodal 5-star vs 1-star skew)
        ratings = [r.get("rating", 3.0) for r in reviews]
        count_5 = sum(1 for r in ratings if r >= 4.5)
        count_1 = sum(1 for r in ratings if r <= 1.5)
        count_mid = sum(1 for r in ratings if 2.0 <= r <= 4.0)

        polarization_detected = False
        if n >= 5 and (count_5 + count_1) / n >= 0.85 and count_mid <= 1:
            polarization_detected = True
            polarization_penalty = 20.0
            signals.append("polarized_rating_distribution")

        return {
            "burst_detected": burst_detected,
            "polarization_detected": polarization_detected,
            "burst_penalty": burst_penalty,
            "polarization_penalty": polarization_penalty,
            "signals": signals,
        }
