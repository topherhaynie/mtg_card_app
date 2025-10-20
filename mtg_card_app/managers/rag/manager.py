"""RAG Manager for semantic search of MTG cards using vector embeddings.

This manager provides semantic search capabilities by:
1. Embedding card text using an embedding service
2. Storing embeddings in a vector store
3. Enabling similarity search for finding related cards

The manager is now decoupled from specific implementations:
- Uses EmbeddingService protocol (default: SentenceTransformers)
- Uses VectorStoreService protocol (default: ChromaDB)
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from mtg_card_app.domain.entities import Card
from mtg_card_app.interfaces.embedding import (
    EmbeddingService,
    SentenceTransformerEmbeddingService,
)
from mtg_card_app.interfaces.vector_store import (
    ChromaVectorStoreService,
    VectorStoreService,
)

logger = logging.getLogger(__name__)


class RAGManager:
    """Manages vector embeddings and semantic search for MTG cards.

    This manager is now decoupled from specific implementations:
    - Uses EmbeddingService for text-to-vector conversion
    - Uses VectorStoreService for storage and search

    Default implementations:
    - Embedding: SentenceTransformers (sentence-transformers/all-MiniLM-L6-v2)
    - Vector Store: ChromaDB (local persistent storage)

    Storage:
    - Model: ~80 MB (cached in ~/.cache/huggingface/)
    - Embeddings: ~40 KB per card (includes HNSW index overhead)
    - For 1,000 cards: ~40 MB
    - For 27,000 cards: ~1.1 GB
    """

    def __init__(
        self,
        data_dir: str = "data",
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None,
    ):
        """Initialize the RAG manager.

        Args:
            data_dir: Directory for storing data (used if services not provided)
            embedding_service: Embedding service (uses SentenceTransformers if None)
            vector_store: Vector store service (uses ChromaDB if None)

        """
        self.data_dir = data_dir

        # Initialize embedding service
        self.embedding_service = embedding_service or SentenceTransformerEmbeddingService()

        # Initialize vector store
        self.vector_store = vector_store or ChromaVectorStoreService(
            data_dir=f"{data_dir}/chroma",
            collection_name="mtg_cards",
        )

        logger.info("Initialized RAGManager with data_dir: %s", data_dir)

    def _build_card_text(self, card: Card) -> str:
        """Build searchable text representation of a card.

        Combines relevant card fields for embedding:
        - Name
        - Type line
        - Oracle text
        - Keywords

        Args:
            card: Card entity

        Returns:
            Combined text string

        """
        parts = [
            f"Name: {card.name}",
            f"Type: {card.type_line}",
        ]

        if card.oracle_text:
            parts.append(f"Text: {card.oracle_text}")

        if card.keywords:
            parts.append(f"Keywords: {', '.join(card.keywords)}")

        if card.color_identity:
            colors = ", ".join(card.color_identity)
            parts.append(f"Colors: {colors}")

        return " | ".join(parts)

    def _build_metadata(self, card: Card) -> Dict[str, Any]:
        """Build metadata for a card embedding.

        Metadata is stored alongside embeddings and can be used for filtering.

        Args:
            card: Card entity

        Returns:
            Metadata dictionary

        """
        metadata = {
            "name": card.name,
            "type_line": card.type_line,
            "cmc": card.cmc or 0,
        }

        if card.colors:
            metadata["colors"] = ",".join(card.colors)

        if card.color_identity:
            metadata["color_identity"] = ",".join(card.color_identity)

        if card.keywords:
            metadata["keywords"] = ",".join(card.keywords)

        if card.power:
            metadata["power"] = card.power
        if card.toughness:
            metadata["toughness"] = card.toughness

        return metadata

    def embed_card(self, card: Card) -> bool:
        """Embed a single card and store it.

        Args:
            card: Card entity to embed

        Returns:
            True if successfully embedded, False otherwise

        """
        try:
            # Check if already embedded
            if self.vector_store.exists(card.id):
                logger.debug("Card already embedded: %s", card.name)
                return True

            # Build text and embed
            card_text = self._build_card_text(card)
            embedding = self.embedding_service.embed_text(card_text)

            # Store in vector database
            success = self.vector_store.add_embedding(
                id=card.id,
                embedding=embedding,
                metadata=self._build_metadata(card),
                document=card_text,
            )

            if success:
                logger.debug("Embedded card: %s", card.name)
            return success

        except Exception as e:
            logger.error("Error embedding card %s: %s", card.name, e)
            return False

    def embed_cards(self, cards: List[Card], batch_size: int = 32) -> Dict[str, int]:
        """Embed multiple cards in batches.

        Args:
            cards: List of Card entities
            batch_size: Number of cards to embed at once

        Returns:
            Statistics dictionary with success/failure counts

        """
        stats = {
            "total": len(cards),
            "success": 0,
            "skipped": 0,
            "failed": 0,
        }

        logger.info("Embedding %d cards in batches of %d", len(cards), batch_size)

        for i in range(0, len(cards), batch_size):
            batch = cards[i : i + batch_size]

            for card in batch:
                try:
                    # Check if already exists
                    if self.vector_store.exists(card.id):
                        stats["skipped"] += 1
                        continue

                    # Embed and store
                    if self.embed_card(card):
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1

                except Exception as e:
                    logger.exception("Error in batch processing: %s", e)
                    stats["failed"] += 1

            if (i + batch_size) % 100 == 0:
                logger.info("Processed %d/%d cards", i + batch_size, len(cards))

        logger.info(
            "Embedding complete: %d success, %d skipped, %d failed",
            stats["success"],
            stats["skipped"],
            stats["failed"],
        )

        return stats

    def search_similar(
        self,
        query: str,
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for cards similar to a text query.

        Args:
            query: Search query text
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"colors": "U"})

        Returns:
            List of (card_id, similarity_score, metadata) tuples

        """
        try:
            # Embed the query
            query_embedding = self.embedding_service.embed_text(query)

            # Search in vector store
            similar_cards = self.vector_store.search_similar(
                query_embedding=query_embedding,
                n_results=n_results,
                filters=filters,
            )

            logger.debug("Found %d similar cards for query: %s", len(similar_cards), query)
            return similar_cards

        except Exception as e:
            logger.exception("Error searching similar cards: %s", e)
            return []

    def search_similar_to_card(
        self,
        card: Card,
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Find cards similar to a given card.

        Args:
            card: Card entity to find similar cards for
            n_results: Number of results to return (plus 1 for the card itself)
            filters: Optional metadata filters

        Returns:
            List of (card_id, similarity_score, metadata) tuples

        """
        card_text = self._build_card_text(card)
        results = self.search_similar(card_text, n_results + 1, filters)

        # Filter out the card itself
        return [(cid, score, meta) for cid, score, meta in results if cid != card.id]

    def get_embedding(self, card_id: str) -> Optional[List[float]]:
        """Get the embedding for a specific card.

        Args:
            card_id: Card ID

        Returns:
            Embedding vector or None if not found

        """
        return self.vector_store.get_embedding(card_id)

    def remove_card(self, card_id: str) -> bool:
        """Remove a card's embedding.

        Args:
            card_id: Card ID to remove

        Returns:
            True if removed, False otherwise

        """
        return self.vector_store.delete(card_id)

    def clear_all(self) -> bool:
        """Clear all embeddings from the collection.

        Returns:
            True if successful, False otherwise

        """
        return self.vector_store.clear_all()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system.

        Returns:
            Dictionary with statistics

        """
        # Combine stats from both services
        embedding_stats = self.embedding_service.get_stats()
        vector_stats = self.vector_store.get_stats()

        return {
            **embedding_stats,
            **vector_stats,
        }
