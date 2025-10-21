"""Manager registry for dependency injection."""

import logging
from typing import Optional

from mtg_card_app.managers.card_data import CardDataManager
from mtg_card_app.managers.card_data.services import CardDataService, ScryfallCardDataService
from mtg_card_app.managers.db.manager import DatabaseManager
from mtg_card_app.managers.llm.manager import LLMManager
from mtg_card_app.managers.llm.services import LLMService, OllamaLLMService
from mtg_card_app.managers.rag import RAGManager
from mtg_card_app.managers.rag.services import (
    ChromaVectorStoreService,
    EmbeddingService,
    SentenceTransformerEmbeddingService,
    VectorStoreService,
)
from mtg_card_app.utils.query_cache import QueryCache

logger = logging.getLogger(__name__)


class ManagerRegistry:
    """Central registry for all managers in the application.

    This class implements the Service Locator pattern, providing a single
    point of access to all managers and services in the application.
    It handles initialization and dependency injection.
    """

    _instance: Optional["ManagerRegistry"] = None

    def __init__(
        self,
        data_dir: str = "data",
        card_data_service: CardDataService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store_service: VectorStoreService | None = None,
        llm_service: LLMService | None = None,
        query_cache: QueryCache | None = None,
    ):
        """Initialize the manager registry.

        Args:
            data_dir: Directory for data storage
            card_data_service: Optional card data service (uses Scryfall if not provided)
            embedding_service: Optional embedding service (uses SentenceTransformers if not provided)
            vector_store_service: Optional vector store service (uses ChromaDB if not provided)
            llm_service: Optional LLM service (uses Ollama if not provided)
            query_cache: Optional query cache (creates new one if not provided)

        """
        self.data_dir = data_dir

        # Initialize services (use defaults if not provided)
        self._card_data_service = card_data_service or ScryfallCardDataService()
        self._embedding_service = embedding_service or SentenceTransformerEmbeddingService()
        self._vector_store_service = vector_store_service or ChromaVectorStoreService(
            data_dir=f"{data_dir}/chroma",
            collection_name="mtg_cards",
        )
        self._llm_service = llm_service or OllamaLLMService(model="llama3")
        self._query_cache = query_cache or QueryCache(maxsize=128)

        # Core managers (lazy-loaded via properties)
        self._db_manager: DatabaseManager | None = None
        self._card_data_manager: CardDataManager | None = None
        self._rag_manager: RAGManager | None = None
        self._llm_manager: LLMManager | None = None

        logger.info(f"Initialized ManagerRegistry with data_dir: {data_dir}")

    @classmethod
    def get_instance(cls, data_dir: str = "data") -> "ManagerRegistry":
        """Get or create the singleton instance of ManagerRegistry.

        Args:
            data_dir: Directory for data storage

        Returns:
            ManagerRegistry instance

        """
        if cls._instance is None:
            cls._instance = cls(data_dir=data_dir)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    @property
    def db_manager(self) -> DatabaseManager:
        """Get the database manager."""
        if self._db_manager is None:
            self._db_manager = DatabaseManager(data_dir=self.data_dir)
            logger.debug("Initialized DatabaseManager")
        return self._db_manager

    @property
    def card_data_service(self) -> CardDataService:
        """Get the card data service."""
        return self._card_data_service

    @property
    def embedding_service(self) -> EmbeddingService:
        """Get the embedding service."""
        return self._embedding_service

    @property
    def vector_store_service(self) -> VectorStoreService:
        """Get the vector store service."""
        return self._vector_store_service

    @property
    def card_data_manager(self) -> CardDataManager:
        """Get the card data manager."""
        if self._card_data_manager is None:
            self._card_data_manager = CardDataManager(
                card_service=self.db_manager.card_service,
                card_data_service=self._card_data_service,
            )
            logger.debug("Initialized CardDataManager")
        return self._card_data_manager

    @property
    def rag_manager(self) -> RAGManager:
        """Get the RAG manager."""
        if self._rag_manager is None:
            self._rag_manager = RAGManager(
                embedding_service=self._embedding_service,
                vector_store=self._vector_store_service,
            )
            logger.debug("Initialized RAGManager")
        return self._rag_manager

    @property
    def llm_manager(self) -> LLMManager:
        """Get the LLM manager."""
        if self._llm_manager is None:
            self._llm_manager = LLMManager(llm_service=self._llm_service)
            logger.debug("Initialized LLMManager")
        return self._llm_manager

    @property
    def query_cache(self) -> QueryCache:
        """Get the query cache."""
        return self._query_cache

    def get_all_stats(self) -> dict:
        """Get statistics from all managers.

        Returns:
            Dictionary with stats from all managers

        """
        return {
            "database": self.db_manager.get_stats(),
            "card_data": self.card_data_manager.get_stats(),
            "card_data_service": self.card_data_service.get_stats(),
            "rag": self.rag_manager.get_stats(),
            "embedding_service": self.embedding_service.get_stats(),
            "vector_store_service": self.vector_store_service.get_stats(),
            "llm": self.llm_manager.get_stats(),
            "query_cache": self.query_cache.get_stats(),
        }
