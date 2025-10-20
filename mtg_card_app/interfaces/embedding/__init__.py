"""Embedding service interfaces for text-to-vector conversion."""

from mtg_card_app.interfaces.embedding.base import EmbeddingService
from mtg_card_app.interfaces.embedding.sentence_transformer_service import (
    SentenceTransformerEmbeddingService,
)

__all__ = [
    "EmbeddingService",
    "SentenceTransformerEmbeddingService",
]
