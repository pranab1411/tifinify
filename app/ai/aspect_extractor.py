import re
from typing import List, Dict, Any


class AspectSentimentExtractor:
    """Extracts aspect-level feedback and sentiments from tiffin/mess service reviews."""

    ASPECT_KEYWORDS = {
        "taste": [
            "taste", "tasty", "delicious", "flavor", "flavour", "spicy", "bland",
            "yummy", "salt", "sweet", "masala", "mouthwatering", "homely taste"
        ],
        "food_quality": [
            "quality", "fresh", "stale", "oil", "oily", "cooked", "undercooked",
            "ingredients", "texture", "smell", "rotten", "roti", "rice"
        ],
        "hygiene": [
            "hygiene", "hygienic", "unhygienic", "clean", "cleanliness", "dirty",
            "hair", "cockroach", "insect", "fly", "sanitary", "neat", "spotless"
        ],
        "quantity": [
            "quantity", "portion", "portions", "filling", "enough", "less",
            "sufficient", "small portion", "stomach", "heavy", "diet"
        ],
        "delivery": [
            "delivery", "deliver", "delivered", "time", "timing", "on time",
            "late", "delayed", "delay", "rider", "fast delivery", "cold food"
        ],
        "value_for_money": [
            "price", "pricing", "money", "affordable", "expensive", "costly",
            "budget", "worth", "value", "pocket friendly", "cheap", "rates"
        ],
    }

    POSITIVE_CONTEXT_WORDS = {
        "good", "great", "excellent", "superb", "best", "loved", "nice",
        "fresh", "perfect", "generous", "punctual", "clean", "worth", "friendly"
    }

    NEGATIVE_CONTEXT_WORDS = {
        "bad", "worst", "terrible", "poor", "stale", "dirty", "unhygienic",
        "late", "cold", "expensive", "costly", "oily", "hair", "insect", "delay"
    }

    def extract_aspects_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Identify aspects mentioned in a review and assess local polarity."""
        lower_text = text.lower()
        # Split into clauses by punctuation and contrastive conjunctions
        clauses = re.split(r"[,.!?;:\n]+|\b(?:but|while|however|although|though)\b", lower_text)
        found_aspects = []

        for aspect_name, keywords in self.ASPECT_KEYWORDS.items():
            for clause in clauses:
                clause = clause.strip()
                if not clause:
                    continue
                clause_words = set(re.findall(r"\b[a-z]{3,}\b", clause))
                # Check if this clause contains any keyword for this aspect
                if any(kw in clause for kw in keywords):
                    pos_score = len(clause_words.intersection(self.POSITIVE_CONTEXT_WORDS))
                    neg_score = len(clause_words.intersection(self.NEGATIVE_CONTEXT_WORDS))

                    # Specific domain rules for this aspect
                    if aspect_name == "delivery":
                        if "late" in clause or "delay" in clause or "delayed" in clause or "cold" in clause:
                            neg_score += 2
                        if "on time" in clause or "hot" in clause or "punctual" in clause or "fast" in clause:
                            pos_score += 2

                    if aspect_name == "hygiene":
                        if "hair" in clause or "cockroach" in clause or "dirty" in clause or "insect" in clause:
                            neg_score += 3
                        if "clean" in clause or "spotless" in clause or "neat" in clause:
                            pos_score += 2

                    if aspect_name == "taste":
                        if "delicious" in clause or "tasty" in clause or "amazing" in clause or "yummy" in clause:
                            pos_score += 2
                        if "bland" in clause or "worst" in clause or "bad" in clause:
                            neg_score += 2

                    if pos_score > neg_score:
                        sentiment = "positive"
                    elif neg_score > pos_score:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"

                    found_aspects.append({
                        "aspect": aspect_name,
                        "sentiment": sentiment,
                        "confidence": 0.85,
                        "mention_snippet": clause[:100],
                    })
                    break  # One mention per aspect per review is sufficient for aggregation

        return found_aspects

    def aggregate_aspects(self, all_extracted_aspects: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate aspect sentiments across multiple reviews into percentage scores.
        
        Returns a dict e.g. {"taste": 91.0, "hygiene": 82.0, "quantity": 86.0}
        representing the percentage of positive mentions out of (positive + negative).
        """
        tallies = {}
        for item in all_extracted_aspects:
            asp = item["aspect"]
            sent = item["sentiment"]
            if asp not in tallies:
                tallies[asp] = {"positive": 0, "negative": 0, "neutral": 0}
            tallies[asp][sent] += 1

        results = {}
        for asp, counts in tallies.items():
            total = counts["positive"] + counts["negative"] + counts["neutral"]
            if total >= 1:  # Display when at least 1 mention exists
                # Treat positive as 100%, neutral as 50%, negative as 0%
                weighted_pct = ((counts["positive"] * 1.0) + (counts["neutral"] * 0.5)) / total * 100.0
                results[asp] = round(weighted_pct, 1)

        return results
