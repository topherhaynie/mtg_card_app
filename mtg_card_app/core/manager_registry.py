"""Manager registry for dependency injection."""

import logging
from typing import Optional

from mtg_card_app.interfaces.scryfall import ScryfallClient
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

    def __init__(self, data_dir: str = "data"):
        """Initialize the manager registry.

        Args:
            data_dir: Directory for data storage

        """
        self.data_dir = data_dir

        # Core managers
        self._db_manager: Optional[DatabaseManager] = None
        self._card_data_manager: Optional[CardDataManager] = None
        self._scryfall_client: Optional[ScryfallClient] = None

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
    def scryfall_client(self) -> ScryfallClient:
        """Get the Scryfall API client."""
        if self._scryfall_client is None:
            self._scryfall_client = ScryfallClient()
            logger.debug("Initialized ScryfallClient")
        return self._scryfall_client

    @property
    def card_data_manager(self) -> CardDataManager:
        """Get the card data manager."""
        if self._card_data_manager is None:
            self._card_data_manager = CardDataManager(
                card_service=self.db_manager.card_service,
                scryfall_client=self.scryfall_client,
            )
            logger.debug("Initialized CardDataManager")
        return self._card_data_manager

    def get_all_stats(self) -> dict:
        """Get statistics from all managers.

        Returns:
            Dictionary with stats from all managers

        """
        stats = {
            "database": self.db_manager.get_stats(),
            "card_data": self.card_data_manager.get_stats(),
        }
        return stats
