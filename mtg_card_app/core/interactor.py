"""Main interactor for orchestrating application workflows."""

import logging
from typing import Any, Dict, List, Optional

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities import Card, Combo

logger = logging.getLogger(__name__)


class Interactor:
    """Main application interactor.

    This class orchestrates high-level workflows by coordinating
    between different managers. It implements use cases and business logic.
    """

    def __init__(self, registry: Optional[ManagerRegistry] = None):
        """Initialize the interactor.

        Args:
            registry: Optional manager registry (creates one if not provided)

        """
        self.registry = registry or ManagerRegistry.get_instance()
        logger.info("Initialized Interactor")

    # ===== Card Operations =====

    def fetch_card(self, name: str) -> Optional[Card]:
        """Fetch a card by name.

        Args:
            name: Card name

        Returns:
            Card entity or None

        """
        logger.info(f"Fetching card: {name}")
        return self.registry.card_data_manager.get_card(name)

    def search_cards(self, query: str, use_scryfall: bool = False) -> List[Card]:
        """Search for cards.

        Args:
            query: Search query
            use_scryfall: Whether to search Scryfall API

        Returns:
            List of matching cards

        """
        logger.info(f"Searching cards: {query} (scryfall={use_scryfall})")
        return self.registry.card_data_manager.search_cards(
            query,
            use_local=True,
            use_scryfall=use_scryfall,
        )

    def import_cards(self, card_names: List[str]) -> Dict[str, Any]:
        """Import multiple cards from Scryfall.

        Args:
            card_names: List of card names to import

        Returns:
            Import statistics

        """
        logger.info(f"Importing {len(card_names)} cards")
        return self.registry.card_data_manager.bulk_import_cards(card_names)

    def get_budget_cards(self, max_price: float) -> List[Card]:
        """Get cards under a certain price.

        Args:
            max_price: Maximum price in USD

        Returns:
            List of budget-friendly cards

        """
        logger.info(f"Finding budget cards under ${max_price}")
        return self.registry.card_data_manager.get_budget_cards(max_price)

    # ===== Combo Operations =====

    def create_combo(
        self,
        card_names: List[str],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Combo:
        """Create a new combo from card names.

        Args:
            card_names: List of card names in the combo
            name: Optional name for the combo
            description: Optional description

        Returns:
            Created Combo entity

        """
        logger.info(f"Creating combo with {len(card_names)} cards")

        # Fetch all cards
        cards = []
        for card_name in card_names:
            card = self.fetch_card(card_name)
            if card:
                cards.append(card)
            else:
                logger.warning(f"Card '{card_name}' not found, skipping")

        if not cards:
            raise ValueError("No valid cards found for combo")

        # Create combo entity
        combo = Combo(
            name=name or f"{' + '.join([c.name for c in cards])}",
            description=description or "",
            card_ids=[c.id for c in cards],
            card_names=[c.name for c in cards],
        )

        # Calculate pricing
        card_prices = {c.id: c.get_primary_price() or 0.0 for c in cards}
        combo.calculate_total_price(card_prices)

        # Determine color identity
        all_colors = set()
        for card in cards:
            all_colors.update(card.color_identity)
        combo.colors_required = sorted(list(all_colors))

        # Store combo
        combo = self.registry.db_manager.combo_service.create(combo)
        logger.info(f"Created combo: {combo}")

        return combo

    def find_combos_by_card(self, card_name: str) -> List[Combo]:
        """Find all combos containing a specific card.

        Args:
            card_name: Name of the card

        Returns:
            List of combos

        """
        card = self.fetch_card(card_name)
        if not card:
            logger.warning(f"Card '{card_name}' not found")
            return []

        return self.registry.db_manager.combo_service.get_by_card_id(card.id)

    def get_budget_combos(self, max_price: float) -> List[Combo]:
        """Get combos under a certain total price.

        Args:
            max_price: Maximum total price in USD

        Returns:
            List of budget combos

        """
        logger.info(f"Finding budget combos under ${max_price}")
        return self.registry.db_manager.combo_service.get_budget_combos(max_price)

    # ===== System Operations =====

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics.

        Returns:
            Dictionary with system stats

        """
        return self.registry.get_all_stats()

    def initialize_with_sample_data(self) -> Dict[str, Any]:
        """Initialize the system with some sample MTG cards for testing.

        Returns:
            Import statistics

        """
        logger.info("Initializing with sample data")

        # Sample popular combo pieces and useful cards
        sample_cards = [
            # Classic infinite mana combos
            "Isochron Scepter",
            "Dramatic Reversal",
            # Thassa's Oracle win con
            "Thassa's Oracle",
            "Demonic Consultation",
            # Value engines
            "Sol Ring",
            "Rhystic Study",
            "Mystic Remora",
            # Common combo pieces
            "Lightning Bolt",
            "Counterspell",
            "Swords to Plowshares",
        ]

        return self.import_cards(sample_cards)
