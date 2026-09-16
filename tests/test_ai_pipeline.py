import pytest
from app.ai.cleaner import clean_review_text
from app.ai.similarity import ReviewSimilarityDetector
from app.ai.heuristics import ReviewHeuristicsAnalyzer
from app.ai.aspect_extractor import AspectSentimentExtractor
from app.ai.trust_engine import ReviewTrustEngine


def test_clean_review_text():
    raw = "   <b>Amazing food!</b> \n\n Tastes like home.   "
    cleaned = clean_review_text(raw)
    assert cleaned == "Amazing food! Tastes like home."


def test_similarity_detection_exact_and_near_duplicates():
    detector = ReviewSimilarityDetector(near_duplicate_threshold=0.80)
    reviews = [
        {"id": 1, "review_text": "Best tiffin service in town call now for discount."},
        {"id": 2, "review_text": "Best tiffin service in town call now for discount."},  # exact dup
        {"id": 3, "review_text": "Best tiffin service in town order now for discount."}, # near dup
        {"id": 4, "review_text": "The dal was extremely bland and packaging was leaky."}, # distinct
    ]
    res = detector.analyze_provider_reviews(reviews)
    assert res["exact_duplicate_count"] >= 1
    assert res["near_duplicate_count"] >= 1
    assert res["per_review_max_sim"][1] > 0.80
    assert res["per_review_max_sim"][4] < 0.50


def test_heuristic_inconsistency_detection():
    analyzer = ReviewHeuristicsAnalyzer()

    # Low rating with positive text mismatch
    res_mismatch = analyzer.analyze_single_review(1.0, "Superb food, absolutely delicious and fresh! Loved it.")
    assert res_mismatch["rating_inconsistency"] is True
    assert "low_rating_positive_text_mismatch" in res_mismatch["signals"]

    # Normal consistent review
    res_normal = analyzer.analyze_single_review(5.0, "Delicious homely food and soft rotis.")
    assert res_normal["rating_inconsistency"] is False
    assert res_normal["sentiment"] == "positive"


def test_aspect_extraction():
    extractor = AspectSentimentExtractor()
    text = "The food taste is amazing and rotis are soft, but delivery was very late and food was cold."
    aspects = extractor.extract_aspects_from_text(text)

    aspect_names = [a["aspect"] for a in aspects]
    assert "taste" in aspect_names
    assert "delivery" in aspect_names

    for a in aspects:
        if a["aspect"] == "taste":
            assert a["sentiment"] == "positive"
        elif a["aspect"] == "delivery":
            assert a["sentiment"] == "negative"


def test_trust_engine_differentiation():
    engine = ReviewTrustEngine()

    # Authentic provider
    authentic_reviews = [
        {"id": 1, "rating": 5.0, "review_text": "The food tastes just like home. Rotis are super soft."},
        {"id": 2, "rating": 4.5, "review_text": "Very hygienic preparations and consistent portion sizes."},
        {"id": 3, "rating": 4.0, "review_text": "Good taste, slightly delayed on rainy days but polite rider."},
    ]
    auth_res = engine.analyze_provider_reviews("Test Authentic", authentic_reviews)
    assert auth_res["overall_trust_score"] >= 80
    assert auth_res["trust_category"] == "likely_authentic"

    # Suspicious provider with copy-paste marketing reviews
    suspicious_reviews = [
        {"id": 10, "rating": 5.0, "review_text": "Best service call now 9890011223 guaranteed discount!"},
        {"id": 11, "rating": 5.0, "review_text": "Best service call now 9890011223 guaranteed discount!"},
        {"id": 12, "rating": 5.0, "review_text": "Best service call today 9890011223 guaranteed discounts!"},
        {"id": 13, "rating": 1.0, "review_text": "Worst experience ever stale food found hair in dal."},
    ]
    susp_res = engine.analyze_provider_reviews("Test Suspicious", suspicious_reviews)
    assert susp_res["overall_trust_score"] < 80
    assert susp_res["suspicious_review_count"] >= 2
