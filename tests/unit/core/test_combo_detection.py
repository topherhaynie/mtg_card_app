"""Tests for combo detection functionality in QueryOrchestrator."""

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


class TestComboDetection:
    """Test combo detection functionality."""

    def test_find_combos_isochron_scepter(self, orchestrator) -> None:
        """Test finding combos with Isochron Scepter.

        Expected: Should find synergistic cards and provide combo analysis.

        Note: This test is intentionally less strict because:
        1. Semantic search results can vary based on vector similarity scores
        2. LLM responses are non-deterministic (temperature, randomness)
        3. The exact combo pieces returned depend on the dataset
        We verify the response exists and is substantial, rather than
        expecting specific card names.
        """
        response = orchestrator.find_combos("Isochron Scepter")

        # Verify response exists and is substantial
        assert isinstance(response, str)
        assert len(response) > 100, "Combo explanation should be substantial"

        # Should mention combo-related concepts (relaxed check)
        response_lower = response.lower()
        combo_terms = ["synergy", "combo", "infinite", "scepter", "instant", "artifact", "mana"]
        assert any(term in response_lower for term in combo_terms), "Response should discuss combo concepts"

    def test_find_combos_dramatic_reversal(self, orchestrator) -> None:
        """Test finding combos with Dramatic Reversal.

        Expected: Should find Isochron Scepter and mana rocks/dorks.
        """
        response = orchestrator.find_combos("Dramatic Reversal")

        assert isinstance(response, str)
        assert len(response) > 100

        response_lower = response.lower()
        # Should mention artifacts or mana generation
        assert "artifact" in response_lower or "mana" in response_lower or "scepter" in response_lower

    def test_find_combos_thassas_oracle(self, orchestrator) -> None:
        """Test finding combos with Thassa's Oracle.

        Expected: Should find Demonic Consultation or cards that empty the library.
        """
        response = orchestrator.find_combos("Thassa's Oracle")

        assert isinstance(response, str)
        assert len(response) > 100

        response_lower = response.lower()
        # Should mention consultation or winning the game
        assert "consultation" in response_lower or "demonic" in response_lower or "win" in response_lower

    def test_find_combos_rhystic_study(self, orchestrator) -> None:
        """Test finding combos with Rhystic Study (card advantage engine).

        Expected: Should find other draw/advantage engines or taxing effects.
        """
        response = orchestrator.find_combos("Rhystic Study")

        assert isinstance(response, str)
        assert len(response) > 50

        # Should discuss card advantage or synergies
        response_lower = response.lower()
        assert "draw" in response_lower or "card" in response_lower or "advantage" in response_lower

    def test_find_combos_nonexistent_card(self, orchestrator) -> None:
        """Test combo detection with a card that doesn't exist."""
        response = orchestrator.find_combos("Nonexistent Card Name")

        assert isinstance(response, str)
        assert len(response) > 0

        # Should indicate card not found
        response_lower = response.lower()
        assert "not found" in response_lower or "check" in response_lower

    def test_combo_response_quality(self, orchestrator) -> None:
        """Test that combo responses are detailed and helpful."""
        response = orchestrator.find_combos("Isochron Scepter", n_results=3)

        # Response should be substantial
        assert len(response) > 200, "Combo explanation should be detailed"

        # Should mention key combo concepts
        response_lower = response.lower()
        combo_terms = ["combo", "synergy", "infinite", "win", "mana", "card"]
        assert any(term in response_lower for term in combo_terms), "Response should mention combo-related concepts"

    def test_combo_with_limit(self, orchestrator) -> None:
        """Test finding combos with a specific result limit."""
        response = orchestrator.find_combos("Counterspell", n_results=2)

        assert isinstance(response, str)
        assert len(response) > 50

        # Should still provide meaningful response even with limit
        response_lower = response.lower()
        assert "counterspell" in response_lower or "counter" in response_lower
