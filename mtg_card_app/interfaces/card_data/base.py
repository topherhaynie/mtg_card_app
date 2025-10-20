"""Base protocol for card data services.

This module defines the interface that all card data providers must implement,
allowing for easy swapping between different data sources (Scryfall, MTGJSON, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CardDataService(ABC):
    """Abstract base class for card data services.

    This defines the interface that all card data providers must implement.
    Implementations could fetch from Scryfall, MTGJSON, local databases, etc.
    """

    @abstractmethod
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        """Get card data by name.

        Args:
            name: Card name to search for
            exact: Whether to do exact matching (True) or fuzzy matching (False)

        Returns:
            Card data as dictionary, or None if not found

        Raises:
            Exception: On service-specific errors

        """

    @abstractmethod
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card data by unique identifier.

        Args:
            card_id: Unique identifier for the card (format depends on service)

        Returns:
            Card data as dictionary, or None if not found

        Raises:
            Exception: On service-specific errors

        """

    @abstractmethod
    def search_cards(
        self,
        query: str,
        order: str = "name",
        direction: str = "auto",
        include_extras: bool = False,
        unique: str = "cards",
    ) -> List[Dict[str, Any]]:
        """Search for cards matching a query.

        Args:
            query: Search query (format depends on service)
            order: Field to order results by
            direction: Sort direction ('asc', 'desc', or 'auto')
            include_extras: Whether to include extras/tokens
            unique: How to handle duplicate cards ('cards', 'art', 'prints')

        Returns:
            List of card data dictionaries

        Raises:
            Exception: On service-specific errors

        """

    @abstractmethod
    def autocomplete(self, query: str, include_extras: bool = False) -> List[str]:
        """Get autocomplete suggestions for a card name.

        Args:
            query: Partial card name
            include_extras: Whether to include extras/tokens

        Returns:
            List of suggested card names

        Raises:
            Exception: On service-specific errors

        """

    @abstractmethod
    def get_random_card(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get a random card.

        Args:
            query: Optional query to filter random selection

        Returns:
            Card data as dictionary

        Raises:
            Exception: On service-specific errors

        """

    @abstractmethod
    def build_search_query(
        self,
        colors: Optional[List[str]] = None,
        color_identity: Optional[List[str]] = None,
        type_line: Optional[str] = None,
        oracle_text: Optional[str] = None,
        mana_cost: Optional[str] = None,
        cmc: Optional[int] = None,
        power: Optional[str] = None,
        toughness: Optional[str] = None,
        rarity: Optional[str] = None,
        set_code: Optional[str] = None,
        is_commander: bool = False,
        format_legal: Optional[str] = None,
    ) -> str:
        """Build a search query from structured parameters.

        Args:
            colors: List of color codes (e.g., ['W', 'U'])
            color_identity: List of color identity codes
            type_line: Type line to search for
            oracle_text: Oracle text to search for
            mana_cost: Mana cost pattern
            cmc: Converted mana cost
            power: Power value
            toughness: Toughness value
            rarity: Rarity (common, uncommon, rare, mythic)
            set_code: Set code
            is_commander: Whether card can be a commander
            format_legal: Format legality (standard, modern, commander, etc.)

        Returns:
            Formatted search query string

        """

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the name of this service.

        Returns:
            Service name (e.g., 'Scryfall', 'MTGJSON')

        """

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about this service's usage.

        Returns:
            Dictionary with service statistics

        """

    def supports_bulk_data(self) -> bool:
        """Check if this service supports bulk data downloads.

        Returns:
            True if bulk data is supported

        """
        return False

    def get_bulk_data_url(self) -> Optional[str]:
        """Get URL for bulk data download if supported.

        Returns:
            URL string or None if not supported

        """
        return None
