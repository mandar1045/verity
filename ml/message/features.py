"""Text features: char 2-5 grams + word 1-2 grams (TF-IDF)."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

# \w misses Devanagari/Tamil vowel signs, so include those blocks explicitly.
TOKEN_PATTERN = r"[\wऀ-ॿ஀-௿]+"


def build_features() -> FeatureUnion:
    return FeatureUnion([
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=50_000,
                                 sublinear_tf=True, min_df=2)),
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), max_features=20_000,
                                 sublinear_tf=True, token_pattern=TOKEN_PATTERN, min_df=1)),
    ])
