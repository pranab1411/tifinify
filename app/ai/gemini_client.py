import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class GeminiAnalysisClient:
    """Client for generating grounded natural-language review summaries via Gemini API.
    
    Includes a deterministic fallback when GEMINI_API_KEY is not configured or fails.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google.genai Client: {e}")
                self.client = None

    def generate_review_summary(
        self,
        provider_name: str,
        reviews: List[Dict[str, Any]],
        aspect_scores: Dict[str, float],
        sentiment_pcts: Dict[str, float],
    ) -> str:
        """Generate a factual 2-3 sentence summary grounded solely in available reviews."""
        if len(reviews) < 2:
            return "Not enough review data to generate a reliable summary."

        # If Gemini client is active, attempt generative summarization
        if self.client:
            try:
                review_excerpts = "\n".join([
                    f"- Rating {r.get('rating', 0)}★: \"{r.get('review_text', '')}\""
                    for r in reviews[:15]
                ])

                prompt = (
                    f"You are the review analysis intelligence for Tifinify, an Indian tiffin and mess service discovery app.\n"
                    f"Summarize customer sentiments for '{provider_name}' based EXCLUSIVELY on the review excerpts provided below.\n\n"
                    f"Review Excerpts:\n{review_excerpts}\n\n"
                    f"Aspect Scores: {aspect_scores}\n"
                    f"Sentiment: {sentiment_pcts}\n\n"
                    f"Rules:\n"
                    f"1. Maximum 2 to 3 concise, objective sentences.\n"
                    f"2. Mention the most praised aspect (e.g. taste, quantity) and any recurring customer concern (e.g. late delivery, oiliness).\n"
                    f"3. Do NOT invent dishes, pricing, or operational details not in the excerpts.\n"
                    f"4. If reviews are mixed or conflicting, state this clearly.\n"
                )

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed or timed out: {e}. Using rule-based fallback.")

        # Deterministic Fallback Summary
        return self._generate_fallback_summary(provider_name, reviews, aspect_scores, sentiment_pcts)

    @staticmethod
    def _generate_fallback_summary(
        provider_name: str,
        reviews: List[Dict[str, Any]],
        aspect_scores: Dict[str, float],
        sentiment_pcts: Dict[str, float],
    ) -> str:
        """Generate a clean, grounded summary using rule-based aspect analysis."""
        pos_pct = sentiment_pcts.get("positive", 0.0)
        neg_pct = sentiment_pcts.get("negative", 0.0)

        # Find strongest and weakest aspects
        sorted_aspects = sorted(aspect_scores.items(), key=lambda x: x[1], reverse=True)
        top_aspect = sorted_aspects[0] if sorted_aspects else None
        bottom_aspect = sorted_aspects[-1] if sorted_aspects and len(sorted_aspects) > 1 else None

        sentences = []
        if pos_pct >= 70:
            sentences.append(f"Customers generally express high satisfaction with {provider_name}, noting consistent homestyle meal preparations.")
        elif pos_pct >= 50:
            sentences.append(f"Customers report a balanced experience with {provider_name}, with overall moderate satisfaction.")
        else:
            sentences.append(f"Customer feedback for {provider_name} indicates mixed experiences across recent meal orders.")

        if top_aspect and top_aspect[1] >= 75:
            top_name = top_aspect[0].replace("_", " ").title()
            sentences.append(f"{top_name} is the most frequently praised dimension ({top_aspect[1]}% positive feedback).")

        if bottom_aspect and bottom_aspect[1] < 60:
            bottom_name = bottom_aspect[0].replace("_", " ").title()
            sentences.append(f"{bottom_name} was noted by some customers as an area needing improvement.")

        return " ".join(sentences)
