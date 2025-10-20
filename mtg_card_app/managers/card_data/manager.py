"""Card data manager for fetching and caching card data."""

import logging
from typing import Any, Dict, List, Optional

from mtg_card_app.domain.entities import Card
from mtg_card_app.interfaces.scryfall import CardNotFoundError, ScryfallClient
from mtg_card_app.managers.db.services import CardService

logger = logging.getLogger(__name__)


class CardDataManager:
    """Manages card data fetching and caching.

    This manager coordinates between the Scryfall API and local storage,
    implementing a caching strategy to minimize API calls.
    """

    def __init__(self, card_service: CardService, scryfall_client: Optional[ScryfallClient] = None):
        """Initialize the card data manager.

        Args:
            card_service: Service for local card storage
            scryfall_client: Optional Scryfall client (creates one if not provided)

        """
        self.card_service = card_service
        self.scryfall_client = scryfall_client or ScryfallClient()

    def get_card(self, name: str, fetch_if_missing: bool = True) -> Optional[Card]:
        """Get a card by name, fetching from Scryfall if not in local storage.

        Args:
            name: Card name
            fetch_if_missing: Whether to fetch from Scryfall if not found locally

        Returns:
            Card entity or None

        """
        # Try local storage first
        card = self.card_service.get_by_name(name)

        if card:
            logger.debug(f"Found card '{name}' in local storage")
            return card

        # Fetch from Scryfall if not found locally
        if fetch_if_missing:
            logger.info(f"Fetching card '{name}' from Scryfall")
            try:
                card = self.fetch_and_store_card(name)
                return card
            except CardNotFoundError:
                logger.warning(f"Card '{name}' not found in Scryfall")
                return None

        return None

    def get_card_by_id(self, card_id: str, fetch_if_missing: bool = True) -> Optional[Card]:
        """Get a card by Scryfall ID.

        Args:
            card_id: Scryfall UUID
            fetch_if_missing: Whether to fetch from Scryfall if not found locally

        Returns:
            Card entity or None

        """
        # Try local storage first
        card = self.card_service.get_by_id(card_id)

        if card:
            return card

        # Fetch from Scryfall if not found
        if fetch_if_missing:
            try:
                scryfall_data = self.scryfall_client.get_card_by_id(card_id)
                card = Card.from_scryfall(scryfall_data)
                self.card_service.create(card)
                logger.info(f"Fetched and stored card: {card.name}")
                return card
            except CardNotFoundError:
                logger.warning(f"Card ID '{card_id}' not found in Scryfall")
                return None

        return None

    def fetch_and_store_card(self, name: str, fuzzy: bool = True) -> Card:
        """Fetch a card from Scryfall and store it locally.

        Args:
            name: Card name
            fuzzy: Use fuzzy matching

        Returns:
            Card entity

        Raises:
            CardNotFoundError: If card not found

        """
        scryfall_data = self.scryfall_client.get_card_by_name(name, fuzzy=fuzzy)
        card = Card.from_scryfall(scryfall_data)

        # Store in local database
        if self.card_service.exists(card.id):
            card = self.card_service.update(card)
        else:
            card = self.card_service.create(card)

        return card

    def search_cards(
        self,
        query: str,
        use_local: bool = True,
        use_scryfall: bool = False,
    ) -> List[Card]:
        """Search for cards using Scryfall syntax or local criteria.

        Args:
            query: Search query (Scryfall syntax or dict for local)
            use_local: Search local storage
            use_scryfall: Search Scryfall API

        Returns:
            List of matching cards

        """
        results = []

        if use_local:
            # Convert Scryfall query to local search (simplified)
            # In a real implementation, you'd parse the query properly
            local_results = self.card_service.get_all(limit=1000)
            results.extend(local_results)

        if use_scryfall:
            logger.info(f"Searching Scryfall: {query}")
            scryfall_results = self.scryfall_client.search_cards(query)

            # Convert and store results
            for scryfall_data in scryfall_results:
                card = Card.from_scryfall(scryfall_data)

                # Store if not exists
                if not self.card_service.exists(card.id):
                    self.card_service.create(card)

                results.append(card)

            logger.info(f"Found {len(scryfall_results)} cards from Scryfall")

        return results

    def bulk_import_cards(self, card_names: List[str], fuzzy: bool = True) -> Dict[str, Any]:
        """Import multiple cards from Scryfall.

        Args:
            card_names: List of card names to import
            fuzzy: Use fuzzy matching

        Returns:
            Import statistics

        """
        stats = {
            "total": len(card_names),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

        for name in card_names:
            try:
                # Check if already exists
                if self.card_service.get_by_name(name):
                    stats["skipped"] += 1
                    continue

                # Fetch and store
                self.fetch_and_store_card(name, fuzzy=fuzzy)
                stats["successful"] += 1

            except CardNotFoundError:
                stats["failed"] += 1
                stats["errors"].append(f"Card not found: {name}")
                logger.warning(f"Could not find card: {name}")
            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(f"Error importing {name}: {e!s}")
                logger.error(f"Error importing card {name}: {e}")

        logger.info(
            f"Bulk import complete: {stats['successful']} successful, "
            f"{stats['failed']} failed, {stats['skipped']} skipped"
        )

        return stats

    def get_budget_cards(self, max_price: float) -> List[Card]:
        """Get cards under a certain price."""
        return self.card_service.get_budget_cards(max_price)

    def refresh_card_prices(self, card_ids: Optional[List[str]] = None) -> int:
        """Refresh pricing data for cards by re-fetching from Scryfall.

        Args:
            card_ids: Specific card IDs to refresh (all if None)

        Returns:
            Number of cards refreshed

        """
        if card_ids is None:
            # Refresh all cards
            all_cards = self.card_service.get_all()
            card_ids = [card.id for card in all_cards]

        refreshed = 0
        for card_id in card_ids:
            try:
                scryfall_data = self.scryfall_client.get_card_by_id(card_id)
                card = Card.from_scryfall(scryfall_data)
                self.card_service.update(card)
                refreshed += 1
            except Exception as e:
                logger.error(f"Error refreshing card {card_id}: {e}")

        logger.info(f"Refreshed {refreshed} card prices")
        return refreshed

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about card data."""
        return {
            "total_cards": self.card_service.count(),
            "scryfall_requests": self.scryfall_client.get_request_stats(),
        }
