import hashlib
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.ai.cleaner import clean_review_text


class ReviewSimilarityDetector:
    """Algorithmic duplicate and near-duplicate review detection engine.
    
    Combines exact hash matching with TF-IDF Vectorization and pairwise Cosine Similarity.
    Treats high similarity as a statistical pattern indicator rather than absolute fraud proof.
    """

    def __init__(self, near_duplicate_threshold: float = 0.82):
        self.near_duplicate_threshold = near_duplicate_threshold

    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute MD5 hash of lowercase cleaned text for exact duplicate detection."""
        norm_text = clean_review_text(text).lower()
        return hashlib.md5(norm_text.encode("utf-8")).hexdigest()

    def analyze_provider_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a collection of reviews for a single provider.
        
        Args:
            reviews: List of dicts, each with 'id' and 'review_text'
            
        Returns:
            Dict containing:
                - per_review_max_sim: mapping review_id -> float (0.0 to 1.0)
                - similar_pairs: list of (id1, id2, score, snippet)
                - exact_duplicate_count: int
                - near_duplicate_count: int
                - duplicate_penalty: float (0.0 to 100.0)
        """
        n = len(reviews)
        if n < 2:
            return {
                "per_review_max_sim": {r["id"]: 0.0 for r in reviews},
                "similar_pairs": [],
                "exact_duplicate_count": 0,
                "near_duplicate_count": 0,
                "duplicate_penalty": 0.0,
            }

        texts = [clean_review_text(r.get("review_text", "")).lower() for r in reviews]
        review_ids = [r["id"] for r in reviews]

        # 1. Exact Duplicate Check via Hash
        seen_hashes = {}
        exact_duplicate_ids = set()
        for idx, text in enumerate(texts):
            h = hashlib.md5(text.encode("utf-8")).hexdigest()
            if h in seen_hashes:
                exact_duplicate_ids.add(review_ids[idx])
                exact_duplicate_ids.add(review_ids[seen_hashes[h]])
            else:
                seen_hashes[h] = idx

        # 2. Near-Duplicate Check via TF-IDF & Cosine Similarity
        per_review_max = {r_id: (1.0 if r_id in exact_duplicate_ids else 0.0) for r_id in review_ids}
        similar_pairs = []

        try:
            # Word-level TF-IDF with n-grams (1, 2) to catch phrase reuse
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
            tfidf_matrix = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_matrix)

            for i in range(n):
                for j in range(i + 1, n):
                    score = float(sim_matrix[i, j])
                    if score > per_review_max[review_ids[i]]:
                        per_review_max[review_ids[i]] = score
                    if score > per_review_max[review_ids[j]]:
                        per_review_max[review_ids[j]] = score

                    if score >= self.near_duplicate_threshold:
                        similar_pairs.append({
                            "review_id_1": review_ids[i],
                            "review_id_2": review_ids[j],
                            "similarity_score": round(score, 3),
                            "sample_text_1": texts[i][:80] + "...",
                            "sample_text_2": texts[j][:80] + "...",
                        })
        except Exception:
            # Fallback if vocabulary is completely empty
            pass

        near_dup_count = len(similar_pairs)
        exact_dup_count = len(exact_duplicate_ids) // 2

        # Duplicate penalty formula:
        # Scale proportion of near-duplicate or exact pairs relative to total reviews
        ratio = (len(similar_pairs) * 2 + len(exact_duplicate_ids)) / max(1, n)
        duplicate_penalty = min(100.0, ratio * 75.0)

        return {
            "per_review_max_sim": {k: round(v, 2) for k, v in per_review_max.items()},
            "similar_pairs": similar_pairs,
            "exact_duplicate_count": exact_dup_count,
            "near_duplicate_count": near_dup_count,
            "duplicate_penalty": round(duplicate_penalty, 1),
        }
