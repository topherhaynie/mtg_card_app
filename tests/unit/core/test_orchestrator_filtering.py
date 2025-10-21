"""Enhanced protocol-based tests for QueryOrchestrator with filtering and validation."""

import pytest

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.orchestrator import QueryOrchestrator
from mtg_card_app.managers.llm.manager import LLMManager
from mtg_card_app.managers.llm.services.ollama_service import OllamaLLMService


@pytest.fixture
def orchestrator():
    """Create an orchestrator with all managers initialized."""
    registry = ManagerRegistry.get_instance()
    llm_manager = LLMManager(service=OllamaLLMService(model="llama3"))
    return QueryOrchestrator(registry=registry, llm_manager=llm_manager)


class TestOrchestratorFiltering:
    """Test orchestrator with filtering and result validation."""

    def test_color_filtering_blue(self, orchestrator) -> None:
        """Test that blue card queries return blue cards."""
        user_query = "Show me blue counterspells"
        response = orchestrator.answer_query(user_query)

        # Verify response exists and is meaningful
        assert isinstance(response, str)
        assert len(response) > 0

        # Should mention blue or counterspell-related cards
        response_lower = response.lower()
        assert "counterspell" in response_lower or "blue" in response_lower

    def test_semantic_relevance_card_draw(self, orchestrator) -> None:
        """Test semantic search returns relevant card draw effects."""
        user_query = "Cards that let me draw extra cards"
        response = orchestrator.answer_query(user_query)

        assert isinstance(response, str)
        assert len(response) > 0

        # Should mention known card draw effects from our test data
        response_lower = response.lower()
        # Rhystic Study and Mystic Remora are card draw enchantments in test data
        assert "rhystic" in response_lower or "remora" in response_lower or "draw" in response_lower

    def test_type_filtering_instant(self, orchestrator) -> None:
        """Test filtering by card type returns correct results."""
        user_query = "Show me instant speed interaction"
        response = orchestrator.answer_query(user_query)

        assert isinstance(response, str)
        assert len(response) > 0

        # Should mention instants from test data
        response_lower = response.lower()
        assert "instant" in response_lower or "swords" in response_lower or "counterspell" in response_lower

    def test_no_results_handling(self, orchestrator) -> None:
        """Test graceful handling when no results are found."""
        # Query for something very specific that doesn't exist
        user_query = "Show me 10 mana planeswalkers with hexproof"
        response = orchestrator.answer_query(user_query)

        assert isinstance(response, str)
        assert len(response) > 0

        # Should provide helpful feedback, not just empty response
        response_lower = response.lower()
        assert "no" in response_lower or "not found" in response_lower or "try" in response_lower

    def test_creature_removal(self, orchestrator) -> None:
        """Test semantic search for creature removal."""
        user_query = "What's the best creature removal?"
        response = orchestrator.answer_query(user_query)

        assert isinstance(response, str)
        assert len(response) > 0

        # Should mention Swords to Plowshares which is premium removal
        response_lower = response.lower()
        assert "swords" in response_lower or "removal" in response_lower or "plowshares" in response_lower

    def test_combo_pieces(self, orchestrator) -> None:
        """Test finding combo pieces."""
        user_query = "Cards that work with Isochron Scepter"
        response = orchestrator.answer_query(user_query)

        assert isinstance(response, str)
        assert len(response) > 0

        # Should mention Dramatic Reversal or other instants
        response_lower = response.lower()
        assert (
            "dramatic" in response_lower
            or "reversal" in response_lower
            or "instant" in response_lower
            or "scepter" in response_lower
        )

    def test_response_quality(self, orchestrator) -> None:
        """Test that responses are detailed and helpful."""
        user_query = "Explain blue counterspells"
        response = orchestrator.answer_query(user_query)

        # Response should be substantial
        assert len(response) > 50, "Response should be more than a few words"

        # Should contain card names (capitalized or lowercase)
        assert any(word in response.lower() for word in ["counterspell", "card", "mana", "spell"]), (
            "Response should mention relevant game terms"
        )
