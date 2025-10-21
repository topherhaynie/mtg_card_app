"""Dependency manager for service instantiation and lifecycle management.

This class provides a centralized container for managing service dependencies,
allowing for easy configuration, testing, and swapping of implementations.
"""

from __future__ import annotations

import logging
from typing import Any

from mtg_card_app.managers.card_data.services import (
    CardDataService,
    ScryfallCardDataService,
)
from mtg_card_app.managers.llm.services import (
    LLMService,
    OllamaLLMService,
)
from mtg_card_app.managers.rag.services import (
    ChromaVectorStoreService,
    EmbeddingService,
    SentenceTransformerEmbeddingService,
    VectorStoreService,
)
from mtg_card_app.utils.query_cache import QueryCache

logger = logging.getLogger(__name__)


class DependencyManager:
    """Centralized dependency injection container.

    This class manages the lifecycle and configuration of all services in the application.
    It provides a single point for service instantiation, configuration, and retrieval.

    Usage:
        # Create with defaults
        deps = DependencyManager(data_dir="data")

        # Access services
        card_service = deps.get_card_data_service()
        embedding_service = deps.get_embedding_service()

        # Create with custom implementations
        deps = DependencyManager(
            data_dir="data",
            card_data_service=CustomCardDataService(),
        )
    """

    def __init__(
        self,
        data_dir: str = "data",
        card_data_service: CardDataService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store_service: VectorStoreService | None = None,
        llm_service: LLMService | None = None,
        query_cache: QueryCache | None = None,
    ) -> None:
        """Initialize the dependency manager.

        Args:
            data_dir: Base directory for data storage
            card_data_service: Optional custom card data service
            embedding_service: Optional custom embedding service
            vector_store_service: Optional custom vector store service
            llm_service: Optional custom LLM service
            query_cache: Optional custom query cache

        """
        self.data_dir = data_dir
        self._services: dict[str, Any] = {}

        # Initialize services
        self._card_data_service = card_data_service
        self._embedding_service = embedding_service
        self._vector_store_service = vector_store_service
        self._llm_service = llm_service
        self._query_cache = query_cache

        logger.info(
            "Initialized DependencyManager with data_dir: %s",
            data_dir,
        )

    def get_card_data_service(self) -> CardDataService:
        """Get or create the card data service.

        Returns:
            CardDataService instance

        """
        if self._card_data_service is None:
            logger.debug("Creating default ScryfallCardDataService")
            self._card_data_service = ScryfallCardDataService()
        return self._card_data_service

    def get_embedding_service(self) -> EmbeddingService:
        """Get or create the embedding service.

        Returns:
            EmbeddingService instance

        """
        if self._embedding_service is None:
            logger.debug("Creating default SentenceTransformerEmbeddingService")
            self._embedding_service = SentenceTransformerEmbeddingService()
        return self._embedding_service

    def get_vector_store_service(self) -> VectorStoreService:
        """Get or create the vector store service.

        Returns:
            VectorStoreService instance

        """
        if self._vector_store_service is None:
            logger.debug("Creating default ChromaVectorStoreService")
            self._vector_store_service = ChromaVectorStoreService(
                data_dir=f"{self.data_dir}/chroma",
                collection_name="mtg_cards",
            )
        return self._vector_store_service

    def get_llm_service(self) -> LLMService:
        """Get or create the LLM service.

        Returns:
            LLMService instance

        """
        if self._llm_service is None:
            logger.debug("Creating default OllamaLLMService")
            self._llm_service = OllamaLLMService(model="llama3")
        return self._llm_service

    def get_query_cache(self) -> QueryCache:
        """Get or create the query cache.

        Returns:
            QueryCache instance

        """
        if self._query_cache is None:
            logger.debug("Creating default QueryCache")
            self._query_cache = QueryCache(maxsize=128)
        return self._query_cache

    def set_card_data_service(self, service: CardDataService) -> None:
        """Set a custom card data service.

        Args:
            service: CardDataService implementation to use

        """
        self._card_data_service = service
        logger.debug(
            "Set custom card data service: %s",
            service.get_service_name(),
        )

    def set_embedding_service(self, service: EmbeddingService) -> None:
        """Set a custom embedding service.

        Args:
            service: EmbeddingService implementation to use

        """
        self._embedding_service = service
        logger.debug(
            "Set custom embedding service: %s",
            service.get_service_name(),
        )

    def set_vector_store_service(self, service: VectorStoreService) -> None:
        """Set a custom vector store service.

        Args:
            service: VectorStoreService implementation to use

        """
        self._vector_store_service = service
        logger.debug(
            "Set custom vector store service: %s",
            service.get_service_name(),
        )

    def set_llm_service(self, service: LLMService) -> None:
        """Set a custom LLM service.

        Args:
            service: LLMService implementation to use

        """
        self._llm_service = service
        logger.debug("Set custom LLM service: %s", service.get_service_name())

    def set_query_cache(self, cache: QueryCache) -> None:
        """Set a custom query cache.

        Args:
            cache: QueryCache instance to use

        """
        self._query_cache = cache
        logger.debug("Set custom query cache with maxsize: %d", cache.maxsize)

    def get_all_services(self) -> dict[str, Any]:
        """Get all initialized services.

        Returns:
            Dictionary mapping service names to instances

        """
        services = {}
        if self._card_data_service is not None:
            services["card_data"] = self._card_data_service
        if self._embedding_service is not None:
            services["embedding"] = self._embedding_service
        if self._vector_store_service is not None:
            services["vector_store"] = self._vector_store_service
        if self._llm_service is not None:
            services["llm"] = self._llm_service
        if self._query_cache is not None:
            services["query_cache"] = self._query_cache
        return services

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about all services.

        Returns:
            Dictionary with service statistics

        """
        stats = {
            "data_dir": self.data_dir,
            "services": {},
        }

        for name, service in self.get_all_services().items():
            if hasattr(service, "get_stats"):
                stats["services"][name] = service.get_stats()
            else:
                stats["services"][name] = {
                    "name": service.get_service_name() if hasattr(service, "get_service_name") else name,
                }

        return stats

    def shutdown(self) -> None:
        """Shutdown all services and cleanup resources.

        This should be called when the application is shutting down to ensure
        proper cleanup of resources.
        """
        logger.info("Shutting down DependencyManager")

        # Cleanup vector store (may have open connections)
        if self._vector_store_service is not None:
            logger.debug("Shutting down vector store service")
            # ChromaDB clients are automatically cleaned up, but we can call
            # any explicit cleanup methods if needed in the future

        # Clear query cache
        if self._query_cache is not None:
            logger.debug("Clearing query cache")
            self._query_cache.clear()

        # Clear references
        self._card_data_service = None
        self._embedding_service = None
        self._vector_store_service = None
        self._llm_service = None
        self._query_cache = None
        self._services.clear()

        logger.info("DependencyManager shutdown complete")
