"""Main interactor for orchestrating application workflows."""

import logging
from typing import Any

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities import Card, Combo

logger = logging.getLogger(__name__)


class Interactor:
    """Main application interactor.

    This class orchestrates high-level workflows by coordinating
    between different managers. It implements use cases and business logic.
    """

    def __init__(self, registry: ManagerRegistry | None = None):
        """Initialize the interactor.

        Args:
            registry: Optional manager registry (creates one if not provided)

        """
        self.registry = registry or ManagerRegistry.get_instance()
        logger.info("Initialized Interactor")

    # ===== Card Operations =====

    def fetch_card(self, name: str) -> Card | None:
        """Fetch a card by name.

        Args:
            name: Card name

        Returns:
            Card entity or None

        """
        logger.info(f"Fetching card: {name}")
        return self.registry.card_data_manager.get_card(name)

    def search_cards(self, query: str, use_scryfall: bool = False) -> list[Card]:
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

    def import_cards(self, card_names: list[str]) -> dict[str, Any]:
        """Import multiple cards from Scryfall.

        Args:
            card_names: List of card names to import

        Returns:
            Import statistics

        """
        logger.info(f"Importing {len(card_names)} cards")
        return self.registry.card_data_manager.bulk_import_cards(card_names)

    def get_budget_cards(self, max_price: float) -> list[Card]:
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
        card_names: list[str],
        name: str | None = None,
        description: str | None = None,
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

    def find_combos_by_card(self, card_name: str) -> list[Combo]:
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

    def get_budget_combos(self, max_price: float) -> list[Combo]:
        """Get combos under a certain total price.

        Args:
            max_price: Maximum total price in USD

        Returns:
            List of budget combos

        """
        logger.info(f"Finding budget combos under ${max_price}")
        return self.registry.db_manager.combo_service.get_budget_combos(max_price)

    # ===== System Operations =====

    def get_system_stats(self) -> dict[str, Any]:
        """Get overall system statistics.

        Returns:
            Dictionary with system stats

        """
        return self.registry.get_all_stats()

    # ===== Query Operations =====

    def answer_natural_language_query(self, query: str, use_cache: bool = True) -> str:
        """Answer a natural language query about MTG cards using RAG + LLM.

        Args:
            query: Natural language query (e.g., "Find me blue counterspells under $5")
            use_cache: Whether to use query cache (default: True)

        Returns:
            Generated answer from the LLM

        """
        logger.info(f"Processing natural language query: {query}")

        # Check cache first if enabled
        if use_cache:
            cached_result = self.registry.query_cache.get(query)
            if cached_result is not None:
                logger.info("Query cache hit")
                return cached_result

        # Get relevant cards using RAG
        rag_results = self.registry.rag_manager.query(query, n_results=5)

        # Format context for the LLM
        context = "\n\n".join(
            [
                f"Card: {result['name']}\n"
                f"Type: {result['type_line']}\n"
                f"Mana Cost: {result['mana_cost']}\n"
                f"Text: {result['oracle_text']}\n"
                f"Distance: {result['distance']:.4f}"
                for result in rag_results
            ]
        )

        # Generate answer using LLM
        prompt = f"""Based on the following Magic: The Gathering cards, please answer this query:

Query: {query}

Available Cards:
{context}

Please provide a helpful answer based on these cards. If none of the cards match the query well, say so."""

        answer = self.registry.llm_manager.generate(prompt)

        # Cache the result if enabled
        if use_cache:
            self.registry.query_cache.set(query, answer)

        return answer

    def find_combo_pieces(
        self,
        card_name: str,
        n_results: int = 5,
        use_cache: bool = True,
    ) -> str:
        """Find potential combo pieces for a given card using semantic similarity.

        Args:
            card_name: Name of the card to find combos for
            n_results: Number of similar cards to return
            use_cache: Whether to use query cache (default: True)

        Returns:
            LLM-generated analysis of potential combo pieces

        """
        logger.info(f"Finding combo pieces for: {card_name}")

        # Create cache key
        cache_key = f"combo_pieces:{card_name}:{n_results}"

        # Check cache first if enabled
        if use_cache:
            cached_result = self.registry.query_cache.get(cache_key)
            if cached_result is not None:
                logger.info("Query cache hit")
                return cached_result

        # Fetch the card to get its details
        card = self.fetch_card(card_name)
        if not card:
            return f"Card '{card_name}' not found in database."

        # Query for similar cards
        query = f"cards that combo well with {card.name} {card.oracle_text}"
        rag_results = self.registry.rag_manager.query(query, n_results=n_results)

        # Format context for the LLM
        card_context = f"""Target Card: {card.name}
Type: {card.type_line}
Mana Cost: {card.mana_cost}
Oracle Text: {card.oracle_text}"""

        similar_cards = "\n\n".join(
            [
                f"Card: {result['name']}\n"
                f"Type: {result['type_line']}\n"
                f"Mana Cost: {result['mana_cost']}\n"
                f"Text: {result['oracle_text']}"
                for result in rag_results
            ]
        )

        # Generate analysis using LLM
        prompt = f"""Analyze potential combo synergies for this Magic: The Gathering card:

{card_context}

Similar/Synergistic Cards:
{similar_cards}

Please analyze which of these cards would work well in a combo with {card.name} and explain why. 
Consider mana costs, color requirements, and mechanical synergies."""

        answer = self.registry.llm_manager.generate(prompt)

        # Cache the result if enabled
        if use_cache:
            self.registry.query_cache.set(cache_key, answer)

        return answer

    def initialize_with_sample_data(self) -> dict[str, Any]:
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
