from collections.abc import Sequence
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def get_embedder() -> SentenceTransformer:
    """Load the local sentence-transformers model once per process."""
    return SentenceTransformer(get_settings().embedding_model)


def embed(texts: list[str]) -> list[Sequence[float]]:
    vectors = get_embedder().encode(texts, normalize_embeddings=True)
    return [vector.tolist() for vector in vectors]
