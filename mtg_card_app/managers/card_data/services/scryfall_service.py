"""Scryfall implementation of the CardDataService."""

from typing import Any, Dict, List, Optional

from mtg_card_app.interfaces.scryfall.client import ScryfallClient
from mtg_card_app.managers.card_data.services.base import CardDataService


class ScryfallCardDataService(CardDataService):
    """Scryfall implementation of the card data service.

    This service wraps the ScryfallClient and provides the standard
    CardDataService interface, making it swappable with other implementations.
    """

    def __init__(self, client: Optional[ScryfallClient] = None):
        """Initialize the Scryfall card data service.

        Args:
            client: Optional ScryfallClient instance (creates one if not provided)

        """
        self._client = client or ScryfallClient()

    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        """Get card data by name.

        Args:
            name: Card name to search for
            exact: Whether to do exact matching (True) or fuzzy matching (False)

        Returns:
            Card data as dictionary, or None if not found

        Raises:
            Exception: On API or network errors (not for card not found)

        """
        from mtg_card_app.interfaces.scryfall.exceptions import CardNotFoundError

        try:
            return self._client.get_card_by_name(name, fuzzy=not exact)
        except CardNotFoundError:
            # Card not found is expected, return None
            return None
        except Exception:
            # Other errors should propagate
            raise

    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card data by Scryfall ID.

        Args:
            card_id: Scryfall UUID

        Returns:
            Card data as dictionary, or None if not found

        Raises:
            Exception: On API or network errors (not for card not found)

        """
        from mtg_card_app.interfaces.scryfall.exceptions import CardNotFoundError

        try:
            return self._client.get_card_by_id(card_id)
        except CardNotFoundError:
            # Card not found is expected, return None
            return None
        except Exception:
            # Other errors should propagate
            raise

    def search_cards(
        self,
        query: str,
        order: str = "name",
        direction: str = "auto",
        include_extras: bool = False,
        unique: str = "cards",
    ) -> List[Dict[str, Any]]:
        """Search for cards using Scryfall search syntax.

        Args:
            query: Scryfall search query (e.g., "t:creature c:green")
            order: Field to order by ("name", "set", "released", "rarity", "cmc", etc.)
            direction: Sort direction (Scryfall doesn't use this directly)
            include_extras: Whether to include tokens/emblems
            unique: How to handle duplicates ("cards", "art", "prints")

        Returns:
            List of card data dictionaries

        """
        try:
            return self._client.search_cards(
                query=query,
                order=order,
                include_extras=include_extras,
                unique=unique,
            )
        except Exception:
            return []

    def autocomplete(self, query: str, include_extras: bool = False) -> List[str]:
        """Get autocomplete suggestions for a card name.

        Args:
            query: Partial card name
            include_extras: Whether to include tokens/emblems

        Returns:
            List of suggested card names

        """
        try:
            return self._client.autocomplete(query, include_extras=include_extras)
        except Exception:
            return []

    def get_random_card(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get a random card.

        Args:
            query: Optional Scryfall query to filter random selection

        Returns:
            Card data as dictionary

        Raises:
            Exception: On API errors

        """
        return self._client.get_random_card(query=query)

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
        """Build a Scryfall search query from structured parameters.

        Args:
            colors: List of color codes (e.g., ['W', 'U'])
            color_identity: List of color identity codes
            type_line: Type line to search for (e.g., "creature", "instant")
            oracle_text: Oracle text to search for
            mana_cost: Mana cost pattern (e.g., "{2}{U}{U}")
            cmc: Converted mana cost
            power: Power value (e.g., "3", ">=3", "*")
            toughness: Toughness value
            rarity: Rarity (common, uncommon, rare, mythic)
            set_code: Set code (e.g., "khm", "znr")
            is_commander: Whether card can be a commander
            format_legal: Format legality (standard, modern, commander, etc.)

        Returns:
            Scryfall search query string

        Example:
            >>> service.build_search_query(colors=['U', 'R'], cmc=3, type_line='instant')
            "c:ur cmc=3 t:instant"

        """
        parts = []

        if colors:
            color_str = "".join(colors).lower()
            parts.append(f"c:{color_str}")

        if color_identity:
            ci_str = "".join(color_identity).lower()
            parts.append(f"id:{ci_str}")

        if type_line:
            parts.append(f"t:{type_line}")

        if oracle_text:
            parts.append(f"o:{oracle_text}")

        if mana_cost:
            parts.append(f"m:{mana_cost}")

        if cmc is not None:
            parts.append(f"cmc={cmc}")

        if power:
            parts.append(f"pow={power}")

        if toughness:
            parts.append(f"tou={toughness}")

        if rarity:
            parts.append(f"r:{rarity}")

        if set_code:
            parts.append(f"s:{set_code}")

        if is_commander:
            parts.append("is:commander")

        if format_legal:
            parts.append(f"f:{format_legal}")

        return " ".join(parts)

    def get_service_name(self) -> str:
        """Get the name of this service.

        Returns:
            'Scryfall'

        """
        return "Scryfall"

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about Scryfall API usage.

        Returns:
            Dictionary with request statistics

        """
        stats = self._client.get_request_stats()
        stats["service"] = "Scryfall"
        return stats

    def supports_bulk_data(self) -> bool:
        """Check if Scryfall supports bulk data downloads.

        Returns:
            True (Scryfall supports bulk data)

        """
        return True

    def get_bulk_data_url(self, bulk_type: str = "default_cards") -> Optional[str]:
        """Get URL for Scryfall bulk data download.

        Args:
            bulk_type: Type of bulk data
                - "oracle_cards": Unique cards
                - "default_cards": All printings (recommended)
                - "all_cards": Everything including tokens

        Returns:
            Download URL string

        """
        try:
            return self._client.get_bulk_data(bulk_type=bulk_type)
        except Exception:
            return None
