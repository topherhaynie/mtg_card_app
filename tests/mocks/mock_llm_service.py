"""Mock LLM service for fast, predictable testing."""

import json
from typing import Any


class MockLLMService:
    """Mock LLM that returns canned responses based on prompt analysis.

    This allows us to test our code logic without hitting the real Ollama service,
    making tests fast, deterministic, and independent of external services.

    Usage:
        # Default behavior (smart responses based on prompt)
        mock_llm = MockLLMService()

        # Custom responses for specific keywords
        mock_llm = MockLLMService(responses={
            "combo": "These cards synergize well...",
            "filter": '{"colors": "U"}',
        })
    """

    def __init__(self, responses: dict[str, str] | None = None):
        """Initialize with optional response mapping.

        Args:
            responses: Dict mapping prompt keywords to responses.
                      If a keyword is found in the prompt, return that response.

        """
        self.responses = responses or {}
        self.calls: list[str] = []
        self.generate_count = 0

    def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate a mock response based on prompt keywords.

        Args:
            prompt: The prompt to respond to
            max_tokens: Maximum tokens (ignored in mock, kept for API compatibility)

        Returns:
            Mock response string

        """
        self.calls.append(prompt)
        self.generate_count += 1

        # Check for custom responses first
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response

        # Default responses based on prompt type
        if "extract filter" in prompt.lower() or "filter extraction" in prompt.lower():
            return self._mock_filter_extraction(prompt)

        if "combo" in prompt.lower() or "synergy" in prompt.lower():
            return self._mock_combo_response(prompt)

        if "format" in prompt.lower() or "relevant mtg cards" in prompt.lower():
            return self._mock_format_response(prompt)

        return "Mock LLM response for testing purposes."

    def _mock_filter_extraction(self, prompt: str) -> str:
        """Mock filter extraction - returns simple format that will be converted.

        The Interactor's _extract_filters method converts these simple filters
        into ChromaDB format (e.g., {"colors": "U"} → {"color_identity": "U"}).

        Extract the actual user query from the prompt (after LAST "Query: ").
        """
        # Extract the actual user query from the prompt template
        # Use rfind to get the LAST occurrence (the actual user query, not examples)
        query_marker = 'query: "'
        prompt_lower = prompt.lower()

        if query_marker in prompt_lower:
            # Find the LAST occurrence of 'Query: "'
            start_idx = prompt_lower.rfind(query_marker) + len(query_marker)
            end_idx = prompt.find('"', start_idx)
            if end_idx > start_idx:
                user_query = prompt[start_idx:end_idx].strip()
                # If extracted query is empty, return no filters immediately
                if not user_query:
                    return json.dumps({})
                user_query = user_query.lower()
            else:
                user_query = prompt_lower
        else:
            user_query = prompt_lower

        # Simple pattern matching for common filter patterns
        filters = {}

        # Color detection
        if "blue" in user_query:
            filters["colors"] = "U"
        elif "red" in user_query:
            filters["colors"] = "R"
        elif "green" in user_query:
            filters["colors"] = "G"
        elif "white" in user_query:
            filters["colors"] = "W"
        elif "black" in user_query:
            filters["colors"] = "B"
        elif "grixis" in user_query:
            filters["colors"] = "U,B,R"

        # CMC detection - check user query only
        if "under 4" in user_query:
            filters["max_cmc"] = 3
        elif "under 3" in user_query:
            filters["max_cmc"] = 2
        elif "under 2" in user_query:
            filters["max_cmc"] = 1
        elif "3 or less" in user_query:
            filters["max_cmc"] = 3
        elif "2 or less" in user_query:
            filters["max_cmc"] = 1

        # Return simple format - Interactor will convert to ChromaDB format
        return json.dumps(filters)

    def _mock_combo_response(self, prompt: str) -> str:
        """Mock combo analysis response.

        Args:
            prompt: Prompt containing combo analysis request

        Returns:
            Mock combo analysis text

        """
        prompt_lower = prompt.lower()

        if "isochron scepter" in prompt_lower:
            return (
                "Isochron Scepter creates powerful synergies with instant-speed spells. "
                "Dramatic Reversal is the most famous combo piece, generating infinite mana "
                "when you have mana-producing artifacts that generate at least 3 total mana. "
                "Other excellent options include counterspells like Counterspell or "
                "Swan Song for repeatable interaction, and cantrips like Brainstorm for "
                "card advantage. The key is finding instants with CMC 2 or less that "
                "provide repeatable value."
            )

        if "dramatic reversal" in prompt_lower:
            return (
                "Dramatic Reversal combos with Isochron Scepter and mana rocks to generate "
                "infinite mana. You need artifacts that produce at least 3 total mana to go "
                "infinite. Common enablers include Sol Ring, Mana Crypt, Mana Vault, and "
                "mana-producing creatures. Once you have infinite mana, you can win with "
                "any mana sink or storm payoff."
            )

        if "thassa's oracle" in prompt_lower or "thassas oracle" in prompt_lower:
            return (
                "Thassa's Oracle creates a powerful win condition with cards that empty your "
                "library. Demonic Consultation and Tainted Pact are the most efficient options, "
                "instantly winning the game when Oracle enters. Other synergies include "
                "Paradigm Shift, Leveler, and self-mill strategies."
            )

        if "rhystic study" in prompt_lower:
            return (
                "Rhystic Study is a powerful card advantage engine that synergizes with other "
                "taxing effects. Pair it with Mystic Remora for doubled draw triggers, "
                "Smothering Tithe for mana generation, and Grand Arbiter Augustin IV to "
                "make the tax harder to pay. It's also excellent with wheel effects that "
                "force opponents to recast their hands."
            )

        return (
            "These cards have strong synergies when played together in combo-focused decks. "
            "Consider the mana costs, colors, and timing to maximize their effectiveness."
        )

    def _mock_format_response(self, prompt: str) -> str:
        """Mock formatted card response.

        Args:
            prompt: Prompt containing card formatting request

        Returns:
            Mock formatted response

        """
        return (
            "Here are some relevant cards for your query:\n\n"
            "1. **Counterspell** - The classic 2-mana hard counter that stops any spell\n"
            "2. **Lightning Bolt** - Efficient 1-mana removal dealing 3 damage\n"
            "3. **Sol Ring** - The most powerful mana rock, generating 2 colorless mana\n"
            "4. **Swords to Plowshares** - Premium 1-mana removal for any creature\n\n"
            "These cards offer excellent value and are staples in their respective archetypes. "
            "They demonstrate efficient mana usage and provide answers to common threats."
        )

    def get_model_name(self) -> str:
        """Return mock model name.

        Returns:
            Model name string

        """
        return "mock-llm-v1"

    def get_stats(self) -> dict[str, Any]:
        """Return mock stats.

        Returns:
            Dictionary with mock statistics

        """
        return {
            "model": "mock-llm-v1",
            "total_calls": self.generate_count,
            "api_url": "mock://localhost",
            "status": "mocked",
        }

    def reset(self) -> None:
        """Reset call tracking for test isolation."""
        self.calls = []
        self.generate_count = 0
