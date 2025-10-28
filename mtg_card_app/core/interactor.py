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
        combo_validator=None,
        # Add other managers/services as needed
    ):
        """Initialize the interactor with all dependencies explicitly.

        Args:
            card_data_manager: CardDataManager instance
            rag_manager: RAGManager instance
            llm_manager: LLMManager instance
            db_manager: DatabaseManager instance (optional)
            query_cache: QueryCache instance (optional)
            combo_validator: ComboValidator instance (optional)

        """
        self.card_data_manager = card_data_manager
        self.rag_manager = rag_manager
        self.llm_manager = llm_manager
        self.db_manager = db_manager
        self.query_cache = query_cache
        self.combo_validator = combo_validator
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
        combo.colors_required = sorted(all_colors)

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
        cards_with_scores, response = self.answer_query_with_cards(
            query, use_cache=use_cache, use_filters=use_filters
        )
        return response

    def answer_query_with_cards(
        self,
        query: str,
        *,
        use_cache: bool = True,
        use_filters: bool = True,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[list[tuple[Card, float]], str]:
        """Answer a natural language query and return both cards and response.

        This method is useful when you want to display the cards alongside
        the LLM response (e.g., in a UI).

        Args:
            query: Natural language query (e.g., "Find me blue counterspells under $5")
            use_cache: Whether to use query cache (default: True)
            use_filters: Whether to extract and apply filters (default: True)
            conversation_history: Optional list of previous messages for context

        Returns:
            Tuple of (cards_with_scores, response_text)
            - cards_with_scores: List of (Card, relevance_score) tuples
            - response_text: Generated answer from the LLM

        """
        logger.info("Processing natural language query: %s", query)

        # Extract filters if enabled
        filters = self._extract_filters(query) if use_filters else {}

        # Check cache first if enabled (include filters in cache key)
        if use_cache:
            is_cached, cached_result = self.query_cache.get(query, filters) if self.query_cache else (False, None)
            if is_cached:
                logger.info("Query cache hit")
                # Cache stores only response text, reconstruct with empty cards
                return ([], cached_result)
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
            return ([], result)

        # Fetch full card details for the top results
        cards_with_scores = []
        for card_id, score, _metadata in search_results:
            card = self.card_data_manager.get_card_by_id(
                card_id,
                fetch_if_missing=False,
            )
            if card:
                cards_with_scores.append((card, score))

        if not cards_with_scores:
            result = "Cards were found but could not be retrieved. Please try again."
            if cache_key:
                if self.query_cache:
                    self.query_cache.set(cache_key[0], result, cache_key[1])
            return ([], result)

        # Build improved prompt with strict constraints
        filters_applied = f" (filters applied: {filters})" if filters else ""
        
        # Validate combo if combo validator is available and query seems combo-related
        combo_validation = None
        is_combo_query = any(keyword in query.lower() for keyword in [
            "combo", "infinite", "synergy", "work with", "interact", "together"
        ])
        
        if self.combo_validator and is_combo_query and len(cards_with_scores) >= 2:
            # Validate the top cards as a potential combo
            cards_to_validate = [card for card, _ in cards_with_scores[:3]]  # Check top 3
            combo_validation = self.combo_validator.validate_combo(cards_to_validate)
            logger.info(f"Combo validation: {combo_validation['confidence']:.2%} confidence")
        
        # Format cards for LLM with numbered references
        card_list = []
        for idx, (card, score) in enumerate(cards_with_scores, 1):
            card_text = f"[{idx}] {card.name}"
            if card.mana_cost:
                card_text += f" - {card.mana_cost}"
            if card.type_line:
                card_text += f" - {card.type_line}"
            if card.oracle_text:
                card_text += f'\n    "{card.oracle_text}"'
            card_list.append(card_text)
        
        cards_formatted = "\n\n".join(card_list)
        
        # Add combo validation context if available
        validation_context = ""
        if combo_validation:
            if combo_validation["is_known_combo"]:
                validation_context = f"\n\nNOTE: These cards form a known combo: '{combo_validation['known_combo_name']}' (High confidence)\n"
            elif combo_validation["valid"]:
                confidence_pct = combo_validation["confidence"] * 100
                validation_context = f"\n\nNOTE: Combo feasibility analysis shows {confidence_pct:.0f}% confidence. "
                if combo_validation["warnings"]:
                    validation_context += f"Considerations: {'; '.join(combo_validation['warnings'][:2])}\n"
            else:
                validation_context = f"\n\nNOTE: These cards show limited synergy (confidence: {combo_validation['confidence']:.0%}). "
                validation_context += "Consider explaining what additional pieces or conditions are needed.\n"
        
        # Build conversation context if available
        context_section = ""
        if conversation_history and len(conversation_history) > 0:
            context_lines = ["\nPrevious Conversation:"]
            for msg in conversation_history[:-1]:  # Exclude current query
                role = "User" if msg["role"] == "user" else "You"
                content = msg["content"][:150]  # Truncate long messages
                if len(msg["content"]) > 150:
                    content += "..."
                context_lines.append(f"{role}: {content}")
            context_section = "\n".join(context_lines) + "\n"
        
        format_prompt = f"""You are a Magic: The Gathering expert assistant.
{context_section}
User Query: "{query}"{filters_applied}

Available Cards (in order of relevance):
{cards_formatted}{validation_context}

IMPORTANT RULES:
1. Answer ONLY using the cards listed above
2. DO NOT mention or invent cards not in this list
3. Reference cards by their [number] (e.g., [1], [2])
4. Quote actual card text from the descriptions provided
5. If the query cannot be answered with these cards, say so clearly
6. Use conversation context for follow-up questions (e.g., "that card" refers to previously mentioned cards)
7. If combo validation notes are provided above, incorporate that analysis into your response

Provide a helpful response using ONLY these cards."""

        result = self.llm_manager.generate(format_prompt)
        
        # Cache the result
        if cache_key:
            if self.query_cache:
                self.query_cache.set(cache_key[0], result, cache_key[1])
        
        return (cards_with_scores, result)

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
        """Find potential combo pieces for a given card using LLM-powered analysis.
        
        NEW APPROACH: Use LLM to understand mechanics, then search with multiple
        targeted queries. This leverages the LLM's understanding of Magic's nuanced
        wording to find synergies that pure semantic search would miss.

        Args:
            card_name: Name of the card to find combos for
            n_results: Number of similar cards to return
            use_cache: Whether to use query cache (default: True)

        Returns:
            LLM-generated analysis of potential combo pieces

        """
        logger.info("Finding combo pieces for: %s (LLM-powered analysis)", card_name)

        # Check cache first if enabled
        if use_cache:
            cache_query = f"combo_pieces_v2:{card_name}:{n_results}"  # v2 to invalidate old cache
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

        # STEP 1: Use LLM to analyze card mechanics
        logger.info("Step 1: LLM analyzing card mechanics...")
        llm_analysis = self._analyze_card_mechanics_with_llm(card)
        logger.debug(f"LLM identified mechanics: {llm_analysis['mechanics']}")
        logger.debug(f"LLM search queries: {llm_analysis['search_queries']}")

        # STEP 2: Execute multiple targeted searches based on LLM's understanding
        all_candidates = {}  # card_id -> (card, best_score, query_that_found_it)
        
        # Search with each LLM-generated query
        for search_query in llm_analysis['search_queries'][:6]:  # Top 6 queries
            if not search_query or len(search_query) < 3:
                continue
            logger.debug(f"Searching with query: {search_query}")
            results = self.rag_manager.search_similar(
                query=search_query,
                n_results=5,
            )
            for card_id, score, _metadata in results:
                if card_id == card.id:
                    continue
                if card_id not in all_candidates or score > all_candidates[card_id][1]:
                    combo_card = self.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                    if combo_card:
                        all_candidates[card_id] = (combo_card, score, search_query)

        if not all_candidates:
            return f"No combo pieces found for {card_name}. This card may work well on its own."

        # STEP 3: Sort by score and take top N
        sorted_candidates = sorted(all_candidates.values(), key=lambda x: x[1], reverse=True)
        top_candidates = sorted_candidates[:n_results]

        # Build context for LLM analysis
        base_card_info = {
            "name": card.name,
            "type": card.type_line,
            "cmc": card.cmc,
            "colors": card.colors or [],
            "text": card.oracle_text or "",
        }

        combo_details = []
        for combo_card, score, query_used in top_candidates:
            details = {
                "name": combo_card.name,
                "type": combo_card.type_line,
                "cmc": combo_card.cmc,
                "colors": combo_card.colors or [],
                "text": combo_card.oracle_text or "",
                "synergy_score": round(score, 3),
                "found_via": query_used,
            }
            combo_details.append(details)

        # STEP 4: Ask LLM to validate and explain the mechanical synergies
        # This is where the LLM shines - understanding WHY cards combo
        combo_prompt = f"""You are an expert Magic: The Gathering player analyzing card combos.

Base Card:
{base_card_info}

Your Earlier Analysis:
Mechanics: {', '.join(llm_analysis['mechanics'][:3])}
Synergies: {', '.join(llm_analysis['synergies'][:3])}

Potential Combo Pieces (ordered by synergy):
{combo_details}

For each combo piece, explain the ACTUAL MECHANICAL INTERACTION:
1. How does it synergize with {card.name}? (Be specific about game rules and timing)
2. What does the combo accomplish? (infinite mana, infinite damage, card advantage, etc.)
3. Are there any additional pieces needed?
4. Power level: casual, competitive, or cEDH-viable

IMPORTANT: Only describe real mechanical synergies. If a card doesn't actually combo well, say so.
Be honest about which combos work and which don't."""

        answer = self.llm_manager.generate(combo_prompt)
        # Cache the result if enabled
        if cache_key:
            if self.query_cache:
                self.query_cache.set(cache_key, answer)
        return answer

    def _analyze_card_mechanics_with_llm(self, card: Card) -> dict[str, Any]:
        """Use LLM to deeply analyze a card's combo potential.
        
        This is the KEY to finding novel combos - the LLM understands Magic's
        nuanced wording and can identify mechanical synergies that semantic
        search alone cannot find.
        
        Args:
            card: Card to analyze
            
        Returns:
            Dictionary with mechanics, search_queries, and combo_patterns
        """
        analysis_prompt = f"""You are an expert Magic: The Gathering combo analyst. Analyze this card for combo potential.

Card: {card.name}
Type: {card.type_line}
Mana Cost: {card.mana_cost}
Oracle Text: {card.oracle_text}

CRITICAL: Your goal is to find cards that CREATE COMBOS with this card, not cards that do similar things.

Step 1: Understand what THIS card does
{card.name} does: [analyze the oracle text]

Step 2: Identify what would CREATE AN INFINITE LOOP or POWERFUL SYNERGY
- If this has a TAP ability, you need UNTAP effects for infinite loops
- If this COPIES spells, you need cheap/powerful spells to copy repeatedly  
- If this has ETB triggers, you need FLICKER/BLINK to trigger repeatedly
- If this UNTAPS things, you need tap abilities that generate value
- If this SACRIFICES, you need recursion/death triggers

Step 3: Generate search queries for ORACLE TEXT of combo pieces
Think: "What exact words appear on cards that would combo with this?"

EXAMPLE for a card with tap abilities:
- "untap target artifact" (exact phrase)
- "untap all permanents" (exact phrase)
- "untap each artifact" (exact phrase)

EXAMPLE for a card that copies instants:
- "instant" and "mana value 1" (to find cheap instants)
- "untap all" (to untap this card for infinite copies)
- "target instant" (instants that interact with instants)

Your queries should be 3-8 words of ACTUAL ORACLE TEXT that would appear on combo pieces.

SEARCH_QUERIES:
- [oracle text pattern 1]
- [oracle text pattern 2]
- [oracle text pattern 3]
- [oracle text pattern 4]
- [oracle text pattern 5]
- [oracle text pattern 6]"""

        try:
            response = self.llm_manager.generate(analysis_prompt)
            
            # Parse search queries from response
            # The LLM might output them in various formats, so be flexible
            search_queries = []
            
            for line in response.split('\n'):
                line = line.strip()
                # Look for lines starting with "-" (list items)
                if line.startswith('-'):
                    query = line.lstrip('- ').strip()
                    # Remove quotes and extra formatting
                    query = query.strip('"').strip("'").strip()
                    if query and len(query) > 3:
                        search_queries.append(query)
                # Also look for numbered lists like "1." or "2."
                elif len(line) > 3 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                    # Extract everything after the number
                    query = line[2:].strip() if line[1] == '.' else line[3:].strip()
                    # Remove quotes and anything in parentheses (explanations)
                    query = query.strip('"').strip("'").strip()
                    # Remove parenthetical explanations
                    if '(' in query:
                        query = query[:query.index('(')].strip()
                    if query and len(query) > 3:
                        search_queries.append(query)
            
            return {
                'mechanics': [],
                'synergies': [],
                'search_queries': search_queries,
                'raw_response': response,
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to simple query
            return {
                'mechanics': [],
                'synergies': [],
                'search_queries': [card.oracle_text[:100] if card.oracle_text else card.name],
                'known_combos': [],
                'raw_response': '',
            }

    def _build_combo_query(self, card: Card) -> str:
        """Build a targeted search query for finding combo pieces.

        This method analyzes the card's mechanics and builds a search query
        that will help find synergistic cards using semantic search.

        Args:
            card: Card entity to find combos for

        Returns:
            Search query string optimized for finding synergies

        """
        # Extract key mechanics from oracle text
        oracle_text = (card.oracle_text or "").lower()
        card_type = (card.type_line or "").lower()
        card_name = card.name.lower()

        # Start with explicit combo synergy focus
        query_parts = []
        
        # Analyze the card's key mechanics deeply
        mechanics_found = []
        
        # UNTAP EFFECTS - Extremely valuable for combo potential
        if any(word in oracle_text for word in ["untap", "untaps"]):
            mechanics_found.append("untap")
            # Untap effects want tap abilities, mana, or activated abilities
            query_parts.append("tap abilities activated abilities mana rocks mana dorks")
            query_parts.append("untap all permanents artifacts creatures lands")
        
        # TAP ABILITIES - Want untap effects
        if ": " in oracle_text and ("tap" in oracle_text or "{t}" in oracle_text):
            mechanics_found.append("tap_ability")
            query_parts.append("untap permanents artifacts creatures")
            query_parts.append("ways to untap repeatedly infinite activations")
        
        # COPY EFFECTS - Want spells to copy
        if any(word in oracle_text for word in ["copy", "copies"]):
            mechanics_found.append("copy")
            query_parts.append("instants sorceries spells cast triggers")
            query_parts.append("storm cascade copy spell effects")
        
        # IMPRINT/EXILE - Cards like Isochron Scepter
        if any(word in oracle_text for word in ["imprint", "exile", "exiled"]):
            if "instant" in oracle_text or "sorcery" in oracle_text:
                mechanics_found.append("imprint_spell")
                query_parts.append("cheap instants low mana cost instant spells")
                query_parts.append("untap effects dramatic reversal reset")
        
        # ENTERS THE BATTLEFIELD - Want flicker/blink/recursion
        if any(word in oracle_text for word in ["enters the battlefield", "etb", "when ~ enters"]):
            mechanics_found.append("etb")
            query_parts.append("flicker blink bounce return to hand")
            query_parts.append("recurring nightmare cloudstone curio")
        
        # SACRIFICE OUTLETS - Want recursion/death triggers
        if any(word in oracle_text for word in ["sacrifice", "sacrifices"]):
            mechanics_found.append("sacrifice")
            query_parts.append("death triggers dies creature dies")
            query_parts.append("reanimate return from graveyard persist undying")
        
        # DRAW EFFECTS - Want discard or deck manipulation
        if "draw" in oracle_text and "card" in oracle_text:
            mechanics_found.append("draw")
            query_parts.append("discard effects wheel effects library manipulation")
            query_parts.append("laboratory maniac thassa's oracle jace win condition")
        
        # MILL - Want graveyard synergies
        if any(word in oracle_text for word in ["mill", "put", "top"]) and "library" in oracle_text:
            mechanics_found.append("mill")
            query_parts.append("graveyard matters reanimation flashback dredge")
            query_parts.append("self-mill fill graveyard")
        
        # STORM - Want cheap spells
        if "storm" in oracle_text:
            mechanics_found.append("storm")
            query_parts.append("zero mana spells cheap cantrips rituals")
            query_parts.append("cost reduction spell cost reducers")
        
        # TOKENS - Want sacrifice outlets or token doublers
        if "token" in oracle_text or "create" in oracle_text:
            mechanics_found.append("tokens")
            query_parts.append("sacrifice outlets altar ashnod's altar")
            query_parts.append("token doublers parallel lives doubling season")
        
        # MANA PRODUCTION - Want infinite mana sinks
        if any(word in oracle_text for word in ["add", "mana"]) and any(c in oracle_text for c in ["{", "}"]):
            mechanics_found.append("mana")
            query_parts.append("mana sinks infinite mana outlets")
            query_parts.append("untap lands mana rocks mana dorks")
        
        # LIFE GAIN - Want life payment or damage conversion
        if "gain" in oracle_text and "life" in oracle_text:
            mechanics_found.append("lifegain")
            query_parts.append("pay life aetherflux reservoir lifegain payoffs")
        
        # COUNTER/REMOVAL - Want spell recursion
        if "counter target" in oracle_text:
            mechanics_found.append("counterspell")
            query_parts.append("spell recursion isochron scepter fork copy instant")
        
        # If we found specific mechanics, add targeted searches
        if mechanics_found:
            # Add the specific mechanic combinations
            if "untap" in mechanics_found and "tap_ability" in mechanics_found:
                query_parts.append("infinite combo untap loop")
            if "copy" in mechanics_found:
                query_parts.append("infinite copies fork effect")
            if "etb" in mechanics_found and "sacrifice" in mechanics_found:
                query_parts.append("sacrifice loop recursive combo")
        
        # Add card type synergies
        if "artifact" in card_type:
            query_parts.append("artifact synergies untap artifacts artifact combo")
        if "enchantment" in card_type:
            query_parts.append("enchantment synergies enchantress effects")
        if "creature" in card_type:
            query_parts.append("creature synergies blink effects flicker")
        if "instant" in card_type or "sorcery" in card_type:
            query_parts.append("spell copy effects storm spell recursion")
        
        # Add specific combo patterns for well-known cards
        # These are PRIORITIZED - for known combos, use ONLY the card names
        # because adding mechanics dilutes the semantic search
        known_combos = {
            "isochron scepter": "dramatic reversal",
            "thassa's oracle": "demonic consultation tainted pact",
            "kiki-jiki": "deceiver exarch pestermite zealous conscripts",
            "splinter twin": "deceiver exarch pestermite",
            "food chain": "misthollow griffin eternal scourge",
            "worldgorger dragon": "animate dead dance of the dead necromancy",
        }
        
        known_combo_found = False
        for known_card, combo_query in known_combos.items():
            if known_card in card_name:
                # For known combos, ONLY search for the specific card names
                # Don't dilute with mechanics - semantic search works better with names alone
                query_parts = [combo_query]
                known_combo_found = True
                break
        
        # Only add oracle text if no specific mechanics found (fallback)
        if not mechanics_found and not known_combo_found:
            query_parts.append(oracle_text[:150])
        
        # Build final query emphasizing combo potential
        final_query = " ".join(query_parts)
        
        # Add explicit combo framing (but keep it short for known combos)
        if known_combo_found:
            final_query = f"{final_query}"  # No prefix for known combos - keep it focused
        else:
            final_query = f"combo pieces that work with {card.name}: {final_query}"
        
        logger.debug(f"Built combo query for {card.name}: mechanics={mechanics_found}")
        
        return final_query

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
