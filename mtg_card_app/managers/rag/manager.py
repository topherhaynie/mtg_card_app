"""RAG Manager for semantic search of MTG cards using vector embeddings.

This manager provides semantic search capabilities by:
1. Embedding card text using sentence transformers
2. Storing embeddings in ChromaDB
3. Enabling similarity search for finding related cards
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from mtg_card_app.domain.entities import Card

logger = logging.getLogger(__name__)


class RAGManager:
    """Manages vector embeddings and semantic search for MTG cards.

    This manager uses:
    - sentence-transformers for creating embeddings
    - ChromaDB for vector storage and similarity search

    Storage:
    - Model: ~80 MB (cached in ~/.cache/huggingface/)
    - Embeddings: ~16 KB per card
    - For 1,000 cards: ~16 MB
    - For 27,000 cards: ~421 MB
    """

    # Model selection - this one is small, fast, and good quality
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    COLLECTION_NAME = "mtg_cards"

    def __init__(
        self,
        data_dir: str = "data",
        model_name: Optional[str] = None,
        device: str = "cpu",
    ):
        """Initialize the RAG manager.

        Args:
            data_dir: Directory for storing ChromaDB data
            model_name: Embedding model name (uses DEFAULT_MODEL if None)
            device: Device for embedding model ('cpu' or 'cuda')

        """
        self.data_dir = Path(data_dir)
        self.chroma_dir = self.data_dir / "chroma"
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device

        # Initialize components (lazy loading)
        self._embedding_model: Optional[SentenceTransformer] = None
        self._chroma_client: Optional[chromadb.Client] = None
        self._collection: Optional[chromadb.Collection] = None

        logger.info(f"Initialized RAGManager with data_dir: {data_dir}")

    @property
    def embedding_model(self) -> SentenceTransformer:
        """Get or load the embedding model."""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._embedding_model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            logger.info("Embedding model loaded successfully")
        return self._embedding_model

    @property
    def chroma_client(self) -> chromadb.Client:
        """Get or create the ChromaDB client."""
        if self._chroma_client is None:
            logger.info(f"Initializing ChromaDB at: {self.chroma_dir}")
            self._chroma_client = chromadb.PersistentClient(
                path=str(self.chroma_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.debug("ChromaDB client initialized")
        return self._chroma_client

    @property
    def collection(self) -> chromadb.Collection:
        """Get or create the card embeddings collection."""
        if self._collection is None:
            try:
                self._collection = self.chroma_client.get_collection(
                    name=self.COLLECTION_NAME,
                )
                logger.debug(f"Loaded existing collection: {self.COLLECTION_NAME}")
            except Exception:
                # Collection doesn't exist, create it
                self._collection = self.chroma_client.create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"description": "MTG card embeddings for semantic search"},
                )
                logger.info(f"Created new collection: {self.COLLECTION_NAME}")
        return self._collection

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
            existing = self.collection.get(ids=[card.id])
            if existing and existing["ids"]:
                logger.debug(f"Card already embedded: {card.name}")
                return True

            # Build text and embed
            card_text = self._build_card_text(card)
            embedding = self.embedding_model.encode(card_text).tolist()

            # Store in ChromaDB
            self.collection.add(
                ids=[card.id],
                embeddings=[embedding],
                metadatas=[self._build_metadata(card)],
                documents=[card_text],
            )

            logger.debug(f"Embedded card: {card.name}")
            return True

        except Exception as e:
            logger.error(f"Error embedding card {card.name}: {e}")
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

        logger.info(f"Embedding {len(cards)} cards in batches of {batch_size}")

        for i in range(0, len(cards), batch_size):
            batch = cards[i : i + batch_size]

            for card in batch:
                try:
                    # Check if already exists
                    existing = self.collection.get(ids=[card.id])
                    if existing and existing["ids"]:
                        stats["skipped"] += 1
                        continue

                    # Embed and store
                    if self.embed_card(card):
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Error in batch processing: {e}")
                    stats["failed"] += 1

            if (i + batch_size) % 100 == 0:
                logger.info(f"Processed {i + batch_size}/{len(cards)} cards")

        logger.info(
            f"Embedding complete: {stats['success']} success, {stats['skipped']} skipped, {stats['failed']} failed",
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
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            where_filter = filters if filters else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
            )

            # Parse results
            similar_cards = []
            if results and results["ids"] and results["ids"][0]:
                for i, card_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i]
                    # Convert distance to similarity (1 - distance)
                    similarity = 1 - distance
                    metadata = results["metadatas"][0][i]
                    similar_cards.append((card_id, similarity, metadata))

            logger.debug(f"Found {len(similar_cards)} similar cards for query: {query}")
            return similar_cards

        except Exception as e:
            logger.error(f"Error searching similar cards: {e}")
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
        try:
            result = self.collection.get(
                ids=[card_id],
                include=["embeddings"],
            )
            if result and result["embeddings"]:
                return result["embeddings"][0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving embedding: {e}")
            return None

    def remove_card(self, card_id: str) -> bool:
        """Remove a card's embedding.

        Args:
            card_id: Card ID to remove

        Returns:
            True if removed, False otherwise

        """
        try:
            self.collection.delete(ids=[card_id])
            logger.debug(f"Removed embedding for card: {card_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing embedding: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all embeddings from the collection.

        Returns:
            True if successful, False otherwise

        """
        try:
            self.chroma_client.delete_collection(name=self.COLLECTION_NAME)
            self._collection = None  # Force recreation
            logger.info("Cleared all embeddings")
            return True
        except Exception as e:
            logger.error(f"Error clearing embeddings: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system.

        Returns:
            Dictionary with statistics

        """
        try:
            count = self.collection.count()

            # Get disk usage
            chroma_size = sum(f.stat().st_size for f in self.chroma_dir.rglob("*") if f.is_file())

            return {
                "total_embeddings": count,
                "model_name": self.model_name,
                "collection_name": self.COLLECTION_NAME,
                "disk_usage_bytes": chroma_size,
                "disk_usage_mb": round(chroma_size / (1024 * 1024), 2),
                "chroma_dir": str(self.chroma_dir),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
