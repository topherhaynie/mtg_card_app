"""Base protocol for embedding services.

This defines the interface for any embedding model that can convert text to vectors.
"""

from typing import Any, Dict, List, Protocol


class EmbeddingService(Protocol):
    """Protocol for text embedding services.

    This abstraction allows switching between different embedding models
    (sentence-transformers, OpenAI, Cohere, etc.) without changing the RAG manager.
    """

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        """
        ...

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        """
        ...

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this service.

        Returns:
            Embedding dimension (e.g., 384, 768, 1536)

        """
        ...

    def get_model_name(self) -> str:
        """Get the name of the embedding model.

        Returns:
            Model name/identifier

        """
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding service.

        Returns:
            Dictionary with service-specific statistics

        """
        ...

    def get_service_name(self) -> str:
        """Get the name of the embedding service.

        Returns:
            Service name (e.g., "SentenceTransformers", "OpenAI")

        """
        ...
