"""Main interactor for orchestrating application workflows."""

import json
import logging
from typing import Any

from mtg_card_app.domain.entities import Card, Combo

logger = logging.getLogger(__name__)


class Interactor:
    # ===== Deck Builder Operations =====

    def build_deck(
        self,
        deck_format: str,
        card_pool: list[str],
        commander: str = None,
        constraints: dict = None,
        metadata: dict = None,
    ):
        """Build a deck using the DeckBuilderManager."""
        from mtg_card_app.core.manager_registry import ManagerRegistry

        deck_builder = ManagerRegistry.get_instance().deck_builder_manager
        return deck_builder.build_deck(deck_format, card_pool, commander, constraints, metadata)

    def validate_deck(self, deck):
        """Validate a deck using the DeckBuilderManager."""
        from mtg_card_app.core.manager_registry import ManagerRegistry

        deck_builder = ManagerRegistry.get_instance().deck_builder_manager
        return deck_builder.validate_deck(deck)

    def analyze_deck(self, deck):
        """Analyze a deck using the DeckBuilderManager."""
        from mtg_card_app.core.manager_registry import ManagerRegistry

        deck_builder = ManagerRegistry.get_instance().deck_builder_manager
        return deck_builder.analyze_deck(deck)

    def suggest_cards(self, deck, constraints: dict | None = None):
        """Suggest cards for a deck using the DeckBuilderManager."""
        from mtg_card_app.core.manager_registry import ManagerRegistry

        deck_builder = ManagerRegistry.get_instance().deck_builder_manager
        return deck_builder.suggest_cards(deck, constraints)

    def export_deck(self, deck, export_format: str = "text"):
        """Export a deck to various formats using the DeckBuilderManager."""
        from mtg_card_app.core.manager_registry import ManagerRegistry

        deck_builder = ManagerRegistry.get_instance().deck_builder_manager
        return deck_builder.export_deck(deck, export_format)

    """Main application interactor.

    Orchestrates high-level workflows by coordinating between managers.
    All dependencies must be passed explicitly.
    """

    def __init__(
        self,
        card_data_manager,
        rag_manager,
        llm_manager,
        db_manager=None,
        query_cache=None,
        # Add other managers/services as needed
    ):
        """Initialize the interactor with all dependencies explicitly.

        Args:
            card_data_manager: CardDataManager instance
            rag_manager: RAGManager instance
            llm_manager: LLMManager instance
            db_manager: DatabaseManager instance (optional)
            query_cache: QueryCache instance (optional)

        """
        self.card_data_manager = card_data_manager
        self.rag_manager = rag_manager
        self.llm_manager = llm_manager
        self.db_manager = db_manager
        self.query_cache = query_cache
        logger.info("Initialized Interactor with explicit dependencies")

    # ===== Card Operations =====

    def fetch_card(self, name: str) -> Card | None:
        """Fetch a card by name.

        Args:
            name: Card name

        Returns:
            Card entity or None

        """
        logger.info(f"Fetching card: {name}")
        return self.card_data_manager.get_card(name)

    def search_cards(self, query: str, use_scryfall: bool = False) -> list[Card]:
        """Search for cards.

        Args:
            query: Search query
            use_scryfall: Whether to search Scryfall API

        Returns:
            List of matching cards

        """
        logger.info(f"Searching cards: {query} (scryfall={use_scryfall})")
        return self.card_data_manager.search_cards(
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
        return self.card_data_manager.bulk_import_cards(card_names)

    def get_budget_cards(self, max_price: float) -> list[Card]:
        """Get cards under a certain price.

        Args:
            max_price: Maximum price in USD

        Returns:
            List of budget-friendly cards

        """
        logger.info(f"Finding budget cards under ${max_price}")
        return self.card_data_manager.get_budget_cards(max_price)

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
        combo = self.db_manager.combo_service.create(combo)
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

        return self.db_manager.combo_service.get_by_card_id(card.id)

    def get_budget_combos(self, max_price: float) -> list[Combo]:
        """Get combos under a certain total price.

        Args:
            max_price: Maximum total price in USD

        Returns:
            List of budget combos

        """
        logger.info(f"Finding budget combos under ${max_price}")
        return self.db_manager.combo_service.get_budget_combos(max_price)

    # ===== System Operations =====

    def get_system_stats(self) -> dict[str, Any]:
        """Get overall system statistics.

        Returns:
            Dictionary with system stats

        """
        return {
            "card_data": self.card_data_manager.get_stats() if hasattr(self.card_data_manager, "get_stats") else None,
            "rag": self.rag_manager.get_stats() if hasattr(self.rag_manager, "get_stats") else None,
            "llm": self.llm_manager.get_stats() if hasattr(self.llm_manager, "get_stats") else None,
            "db": self.db_manager.get_stats() if self.db_manager and hasattr(self.db_manager, "get_stats") else None,
        }

    # ===== Query Operations =====

    def _extract_filters(self, user_query: str) -> dict[str, Any]:
        """Extract search filters from natural language query using LLM.

        Parses queries for:
        - Colors (e.g., "blue", "mono-red", "Grixis")
        - CMC constraints (e.g., "under 3 mana", "CMC 5 or less")
        - Card types (e.g., "creatures", "instants", "artifacts")

        Args:
            user_query: Natural language query

        Returns:
            Dictionary of ChromaDB-compatible filters

        """
        extraction_prompt = f"""You are a filter extraction system. Extract ONLY explicitly stated color and mana cost filters from MTG queries.

Examples:
Query: "Show me blue counterspells"
Response: {{"colors": "U"}}

Query: "Find red creatures under 3 mana"
Response: {{"colors": "R", "max_cmc": 2}}

Query: "What are some infinite mana combos?"
Response: {{}}

Query: "Recommend green ramp spells"
Response: {{"colors": "G"}}

Query: "Show me Grixis control cards under 4 mana"
Response: {{"colors": "U,B,R", "max_cmc": 3}}

Query: "Find efficient removal spells under 2 mana"
Response: {{"max_cmc": 1}}

Rules:
- colors: ONLY if explicitly mentioned (blue, red, mono-black, Grixis, etc.)
  W=white, U=blue, B=black, R=red, G=green
- max_cmc: Integer only. "under X" means X-1. "X or less" means X.
- If not explicitly stated: omit from JSON
- Do NOT infer colors from card types (removal can be any color)
- Return ONLY JSON, no explanation, no markdown, no ```json blocks

Query: "{user_query}"
Response:"""

        try:
            response = self.llm_manager.generate(extraction_prompt)
            # Try to parse JSON from response - handle various formats
            clean_response = response.strip()

            # Remove markdown code blocks if present
            if clean_response.startswith("```"):
                lines = clean_response.split("\n")
                # Find the actual JSON content between ``` markers
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not line.startswith("```")):
                        json_lines.append(line)
                clean_response = "\n".join(json_lines).strip()

            # Try to extract JSON if there's extra text
            # Look for {...} pattern
            if not clean_response.startswith("{"):
                start = clean_response.find("{")
                end = clean_response.rfind("}") + 1
                if start != -1 and end > start:
                    clean_response = clean_response[start:end]

            filters = json.loads(clean_response)
            logger.debug("Extracted filters: %s", filters)

            # Convert to ChromaDB filter format
            # ChromaDB requires $and/$or operators when multiple filters are present
            filter_conditions = []

            # Handle colors - ChromaDB uses exact match, so we check color_identity field
            if filters.get("colors"):
                filter_conditions.append({"color_identity": filters["colors"]})

            # Handle CMC - use $lte operator for "less than or equal"
            # Skip if None/null value
            if "max_cmc" in filters and filters["max_cmc"] is not None:
                filter_conditions.append({"cmc": {"$lte": filters["max_cmc"]}})

            # Combine conditions with $and if multiple filters
            if len(filter_conditions) == 0:
                return {}
            if len(filter_conditions) == 1:
                return filter_conditions[0]
            return {"$and": filter_conditions}

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Failed to extract filters from query: %s", e)
            return {}

    def answer_natural_language_query(
        self,
        query: str,
        *,
        use_cache: bool = True,
        use_filters: bool = True,
    ) -> str:
        """Answer a natural language query about MTG cards using RAG + LLM.

        Args:
            query: Natural language query (e.g., "Find me blue counterspells under $5")
            use_cache: Whether to use query cache (default: True)
            use_filters: Whether to extract and apply filters (default: True)

        Returns:
            Generated answer from the LLM

        """
        logger.info("Processing natural language query: %s", query)

        # Extract filters if enabled
        filters = self._extract_filters(query) if use_filters else {}

        # Check cache first if enabled (include filters in cache key)
        if use_cache:
            is_cached, cached_result = self.query_cache.get(query, filters) if self.query_cache else (False, None)
            if is_cached:
                logger.info("Query cache hit")
                return cached_result
            cache_key = (query, filters)
        else:
            cache_key = None

        # Use RAG semantic search to find relevant cards with filters
        search_results = self.rag_manager.search_similar(
            query=query,
            n_results=5,
            filters=filters if filters else None,
        )

        if not search_results:
            result = self._handle_no_results(query, filters)
            if cache_key:
                if self.query_cache:
                    self.query_cache.set(cache_key[0], result, cache_key[1])
            return result

        # Fetch full card details for the top results
        cards = []
        for card_id, score, _metadata in search_results:
            card = self.card_data_manager.get_card_by_id(
                card_id,
                fetch_if_missing=False,
            )
            if card:
                cards.append((card, score))

        if not cards:
            result = "Cards were found but could not be retrieved. Please try again."
            if cache_key:
                if self.query_cache:
                    self.query_cache.set(cache_key[0], result, cache_key[1])
            return result

        # Build rich context for LLM formatting
        card_details = []
        for card, score in cards:
            details = {
                "name": card.name,
                "type": card.type_line,
                "cmc": card.cmc,
                "colors": card.colors or [],
                "text": card.oracle_text or "",
                "relevance_score": round(score, 3),
            }
            if card.power and card.toughness:
                details["power_toughness"] = f"{card.power}/{card.toughness}"
            card_details.append(details)

        # LLM formats the response with context
        filters_applied = f" (filters applied: {filters})" if filters else ""
        format_prompt = f"""User query: "{query}"{filters_applied}

Relevant MTG cards found (in order of relevance):
{card_details}

Please provide a helpful, natural response answering the user's query using these cards.
Include card names, relevant details, and explain why they match the query."""

        result = self.llm_manager.generate(format_prompt)
        # Cache the result
        if cache_key:
            if self.query_cache:
                self.query_cache.set(cache_key[0], result, cache_key[1])
        return result

    def _handle_no_results(self, user_query: str, filters: dict[str, Any]) -> str:
        """Handle empty search results with suggestions.

        Args:
            user_query: Original user query
            filters: Filters that were applied

        Returns:
            Helpful message with suggestions

        """
        if filters:
            return (
                f"No cards found matching '{user_query}' with the specified filters. "
                "Try broadening your search by removing color, mana cost, or type constraints."
            )
        return f"No cards found matching '{user_query}'. Try rephrasing your query or using different keywords."

    def find_combo_pieces(
        self,
        card_name: str,
        n_results: int = 5,
        *,
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
        logger.info("Finding combo pieces for: %s", card_name)

        # Check cache first if enabled
        if use_cache:
            cache_query = f"combo_pieces:{card_name}:{n_results}"
            is_cached, cached_result = self.query_cache.get(cache_query) if self.query_cache else (False, None)
            if is_cached:
                logger.info("Query cache hit")
                return cached_result
            cache_key = cache_query
        else:
            cache_key = None

        # Fetch the card to get its details
        card = self.fetch_card(card_name)
        if not card:
            return f"Card '{card_name}' not found in database."

        # Build a combo-focused search query
        combo_query = self._build_combo_query(card)
        logger.debug("Combo query: %s", combo_query)

        # Find synergistic cards using semantic search
        search_results = self.rag_manager.search_similar(
            query=combo_query,
            n_results=n_results + 1,  # +1 to account for the base card itself
        )

        # Filter out the base card from results
        combo_cards = []
        for card_id, score, _metadata in search_results:
            if card_id == card.id:
                continue
            combo_card = self.card_data_manager.get_card_by_id(
                card_id,
                fetch_if_missing=False,
            )
            if combo_card:
                combo_cards.append((combo_card, score))

        if not combo_cards:
            return f"No combo pieces found for {card_name}. This card may work well on its own."

        # Build context for LLM analysis
        base_card_info = {
            "name": card.name,
            "type": card.type_line,
            "cmc": card.cmc,
            "colors": card.colors or [],
            "text": card.oracle_text or "",
        }

        combo_details = []
        for combo_card, score in combo_cards[:n_results]:
            details = {
                "name": combo_card.name,
                "type": combo_card.type_line,
                "cmc": combo_card.cmc,
                "colors": combo_card.colors or [],
                "text": combo_card.oracle_text or "",
                "synergy_score": round(score, 3),
            }
            combo_details.append(details)

        # Ask LLM to analyze and explain the combos
        combo_prompt = f"""You are an expert Magic: The Gathering player analyzing card combos.

Base Card:
{base_card_info}

Potential Combo Pieces (ordered by synergy):
{combo_details}

For each combo piece, explain:
1. How it synergizes with {card.name}
2. What the combo accomplishes (infinite mana, infinite damage, card advantage, etc.)
3. Any additional pieces needed to complete the combo
4. Power level assessment (casual, competitive, cEDH-viable)

Provide a clear, organized response that helps players understand these combos."""

        answer = self.llm_manager.generate(combo_prompt)
        # Cache the result if enabled
        if cache_key:
            if self.query_cache:
                self.query_cache.set(cache_key, answer)
        return answer

    def _build_combo_query(self, card: Card) -> str:
        """Build a semantic search query to find combo pieces.

        Args:
            card: Card entity to find combos for

        Returns:
            Search query string optimized for finding synergies

        """
        # Extract key mechanics from oracle text
        oracle_text = card.oracle_text or ""
        card_type = card.type_line.lower()

        # Build a query that emphasizes synergistic mechanics
        query_parts = [f"Cards that synergize with {card.name}"]

        # Add type-specific synergies
        if "artifact" in card_type:
            query_parts.append("artifact synergies")
        if "enchantment" in card_type:
            query_parts.append("enchantment synergies")
        if "instant" in card_type or "sorcery" in card_type:
            query_parts.append("spell synergies")

        # Look for key combo keywords in oracle text
        combo_keywords = [
            "untap",
            "copy",
            "cast",
            "enters",
            "exile",
            "sacrifice",
            "draw",
            "tap",
            "activated ability",
            "storm",
            "flashback",
        ]

        for keyword in combo_keywords:
            if keyword in oracle_text.lower():
                query_parts.append(f"{keyword} effects")

        # Include the oracle text for semantic matching
        query_parts.append(oracle_text[:200])  # Limit length

        return " ".join(query_parts)

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
