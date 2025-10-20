"""Sentence Transformers implementation of embedding service."""

import logging
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingService:
    """Sentence Transformers implementation for text embeddings.

    Uses HuggingFace sentence-transformers library for local embedding generation.
    Models are cached locally in ~/.cache/huggingface/
    """

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = "cpu",
    ):
        """Initialize the embedding service.

        Args:
            model_name: HuggingFace model name (uses DEFAULT_MODEL if None)
            device: Device for model ('cpu' or 'cuda')

        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device

        # Lazy loading
        self._model: Optional[SentenceTransformer] = None

        logger.info(
            "Initialized SentenceTransformerEmbeddingService with model: %s",
            self.model_name,
        )

    @property
    def model(self) -> SentenceTransformer:
        """Get or load the embedding model."""
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            logger.info("Embedding model loaded successfully")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts in batch."""
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        # Get a sample embedding to determine dimension
        if self._model is None:
            # Load model to check dimension
            _ = self.model
        return self.model.get_sentence_embedding_dimension()

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model_name

    def get_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics."""
        stats = {
            "service": "SentenceTransformers",
            "model_name": self.model_name,
            "device": self.device,
        }

        # Add dimension if model is loaded
        if self._model is not None:
            stats["embedding_dimension"] = self.get_embedding_dimension()
            stats["model_loaded"] = True
        else:
            stats["model_loaded"] = False

        return stats

    def get_service_name(self) -> str:
        """Get the service name."""
        return "SentenceTransformers"
