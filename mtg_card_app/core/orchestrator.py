"""QueryOrchestrator: Coordinates LLM, CardData, Embedding, and VectorStore managers for intelligent MTG queries."""

import json
import logging
from typing import Any

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.managers.llm.manager import LLMManager
from mtg_card_app.utils.query_cache import QueryCache

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """Orchestrates multi-manager workflows for natural language MTG queries."""

    def __init__(self, registry: ManagerRegistry = None, llm_manager: LLMManager = None):
        self.registry = registry or ManagerRegistry.get_instance()
        self.llm = llm_manager or LLMManager()
        self.cache = QueryCache(maxsize=128)  # Cache up to 128 queries

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
            response = self.llm.generate(extraction_prompt)
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
            logger.debug(f"Extracted filters: {filters}")

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
            logger.warning(f"Failed to extract filters from query: {e}")
            return {}

    def answer_query(self, user_query: str) -> str:
        """Answer a user query using semantic search and filtering.

        Workflow:
        1. Check cache for previously answered query
        2. Extract filters from natural language query (colors, CMC, type)
        3. Use RAGManager for semantic search with filters
        4. Fetch full card details from CardDataManager
        5. Use LLM to format the final response
        6. Cache the result

        Args:
            user_query: Natural language query about MTG cards

        Returns:
            Natural language response with relevant card information

        """
        # Step 0: Check cache first
        filters = self._extract_filters(user_query)
        is_cached, cached_result = self.cache.get(user_query, filters)
        if is_cached:
            logger.info("Returning cached result for query: %s", user_query[:50])
            return cached_result

        # Step 1: Extract filters from query (already done above for cache key)
        logger.debug("Applying filters: %s", filters)

        # Step 2: Use RAG semantic search to find relevant cards with filters
        search_results = self.registry.rag_manager.search_similar(
            user_query,
            n_results=5,
            filters=filters if filters else None,
        )

        if not search_results:
            result = self._handle_no_results(user_query, filters)
            self.cache.set(user_query, result, filters)
            return result

        # Step 3: Fetch full card details for the top results
        cards = []
        for card_id, score, _metadata in search_results:
            card = self.registry.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if card:
                cards.append((card, score))

        if not cards:
            result = "Cards were found but could not be retrieved. Please try again."
            self.cache.set(user_query, result, filters)
            return result

        # Step 4: Build a rich context for LLM formatting
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

        # Step 5: LLM formats the response with context
        filters_applied = f" (filters applied: {filters})" if filters else ""
        format_prompt = f"""User query: "{user_query}"{filters_applied}

Relevant MTG cards found (in order of relevance):
{card_details}

Please provide a helpful, natural response answering the user's query using these cards.
Include card names, relevant details, and explain why they match the query."""

        result = self.llm.generate(format_prompt)

        # Step 6: Cache the result
        self.cache.set(user_query, result, filters)

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
                f"Try broadening your search by removing color, mana cost, or type constraints."
            )
        return f"No cards found matching '{user_query}'. Try rephrasing your query or using different keywords."

    def find_combos(self, card_name: str, n_results: int = 5) -> str:
        """Find cards that combo with a specific card.

        Uses semantic search to find synergistic cards and LLM to explain the combos.

        Args:
            card_name: Name of the card to find combos for
            n_results: Number of combo pieces to find

        Returns:
            Natural language explanation of combos

        """
        # Step 1: Get the base card
        base_card = self.registry.card_data_manager.get_card(card_name)

        if not base_card:
            return f"Card '{card_name}' not found in the database. Please check the spelling."

        # Step 2: Build a combo-focused search query
        combo_query = self._build_combo_query(base_card)
        logger.debug("Combo query: %s", combo_query)

        # Step 3: Find synergistic cards using semantic search
        search_results = self.registry.rag_manager.search_similar(
            combo_query,
            n_results=n_results + 1,  # +1 to account for the base card itself
        )

        # Filter out the base card from results
        combo_cards = []
        for card_id, score, _metadata in search_results:
            if card_id == base_card.id:
                continue
            card = self.registry.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
            if card:
                combo_cards.append((card, score))

        if not combo_cards:
            return f"No combo pieces found for {card_name}. This card may work well on its own."

        # Step 4: Build context for LLM analysis
        base_card_info = {
            "name": base_card.name,
            "type": base_card.type_line,
            "cmc": base_card.cmc,
            "colors": base_card.colors or [],
            "text": base_card.oracle_text or "",
        }

        combo_details = []
        for card, score in combo_cards[:n_results]:
            details = {
                "name": card.name,
                "type": card.type_line,
                "cmc": card.cmc,
                "colors": card.colors or [],
                "text": card.oracle_text or "",
                "synergy_score": round(score, 3),
            }
            combo_details.append(details)

        # Step 5: Ask LLM to analyze and explain the combos
        combo_prompt = f"""You are an expert Magic: The Gathering player analyzing card combos.

Base Card:
{base_card_info}

Potential Combo Pieces (ordered by synergy):
{combo_details}

For each combo piece, explain:
1. How it synergizes with {base_card.name}
2. What the combo accomplishes (infinite mana, infinite damage, card advantage, etc.)
3. Any additional pieces needed to complete the combo
4. Power level assessment (casual, competitive, cEDH-viable)

Provide a clear, organized response that helps players understand these combos."""

        return self.llm.generate(combo_prompt)

    def _build_combo_query(self, card) -> str:
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

    def get_cache_stats(self) -> dict[str, Any]:
        """Get query cache statistics.

        Returns:
            Dictionary with cache hit rate, size, and other metrics

        """
        return self.cache.get_stats()
