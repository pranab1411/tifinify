import re
import unicodedata


def clean_review_text(text: str) -> str:
    """Preprocess and normalize review text for analytical comparisons.
    
    Preserves essential semantic meaning while normalizing whitespace,
    removing non-standard control characters, and normalizing unicode accents.
    """
    if not text or not isinstance(text, str):
        return ""

    # Normalize unicode (e.g. accented characters, full-width characters)
    normalized = unicodedata.normalize("NFKC", text)

    # Strip HTML tags if any exist
    clean = re.sub(r"<[^>]+>", " ", normalized)

    # Replace multiple newlines or tabs with single spaces
    clean = re.sub(r"[\r\n\t]+", " ", clean)

    # Collapse repeated whitespace
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean
