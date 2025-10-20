"""Manager registry for dependency injection."""

import logging
from typing import Optional

from mtg_card_app.interfaces.card_data import CardDataService, ScryfallCardDataService
from mtg_card_app.managers.card_data import CardDataManager
from mtg_card_app.managers.db.manager import DatabaseManager

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
        card_data_service: Optional[CardDataService] = None,
    ):
        """Initialize the manager registry.

        Args:
            data_dir: Directory for data storage
            card_data_service: Optional card data service (uses Scryfall if not provided)

        """
        self.data_dir = data_dir

        # Core managers
        self._db_manager: Optional[DatabaseManager] = None
        self._card_data_manager: Optional[CardDataManager] = None
        self._card_data_service = card_data_service or ScryfallCardDataService()

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
    def card_data_manager(self) -> CardDataManager:
        """Get the card data manager."""
        if self._card_data_manager is None:
            self._card_data_manager = CardDataManager(
                card_service=self.db_manager.card_service,
                card_data_service=self._card_data_service,
            )
            logger.debug("Initialized CardDataManager")
        return self._card_data_manager

    def get_all_stats(self) -> dict:
        """Get statistics from all managers.

        Returns:
            Dictionary with stats from all managers

        """
        return {
            "database": self.db_manager.get_stats(),
            "card_data": self.card_data_manager.get_stats(),
            "card_data_service": self.card_data_service.get_stats(),
        }
