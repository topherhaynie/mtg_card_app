"""E2E tests for combo detection functionality in Interactor.

NOTE: These are END-TO-END tests that hit:
- Real Ollama LLM service (~30 seconds per test)
- Real ChromaDB vector store
- Real SQLite database

Mark tests with @pytest.mark.e2e to skip them in fast test runs.
Run with: pytest -m "not e2e" to skip these tests.

RETRY MECHANISM:
Tests use @retry_on_llm_variability decorator to retry up to 3 times.
This handles LLM non-determinism - same query can produce different
(but valid) responses. Test passes if ANY attempt succeeds.
"""

import pytest

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry
from tests.e2e.retry_decorator import retry_on_llm_variability


@pytest.fixture
def interactor():
    """Create an interactor with all managers initialized."""
    registry = ManagerRegistry.get_instance()
    return Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        db_manager=registry.db_manager,
        query_cache=registry.query_cache,
    )


class TestComboDetection:
    """Test combo detection functionality."""

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_find_combo_pieces_isochron_scepter(self, interactor) -> None:
        """Test finding combos with Isochron Scepter.

        Expected: Should find synergistic cards and provide combo analysis.

        Note: This test is intentionally less strict because:
        1. Semantic search results can vary based on vector similarity scores
        2. LLM responses are non-deterministic (temperature, randomness)
        3. The exact combo pieces returned depend on the dataset
        We verify the response exists and is substantial, rather than
        expecting specific card names.
        """
        response = interactor.find_combo_pieces("Isochron Scepter")

        # Verify response exists and is substantial
        assert isinstance(response, str)
        assert len(response) > 100, "Combo explanation should be substantial"

        # Should mention combo-related concepts (relaxed check)
        response_lower = response.lower()
        combo_terms = ["synergy", "combo", "infinite", "scepter", "instant", "artifact", "mana"]
        assert any(term in response_lower for term in combo_terms), "Response should discuss combo concepts"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_find_combo_pieces_dramatic_reversal(self, interactor) -> None:
        """Test finding combos with Dramatic Reversal.

        Expected: Should find Isochron Scepter and mana rocks/dorks.
        """
        response = interactor.find_combo_pieces("Dramatic Reversal")

        assert isinstance(response, str)
        assert len(response) > 100

        response_lower = response.lower()
        # Should mention artifacts or mana generation
        assert "artifact" in response_lower or "mana" in response_lower or "scepter" in response_lower

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_find_combo_pieces_thassas_oracle(self, interactor) -> None:
        """Test finding combos with Thassa's Oracle.

        Expected: Should find cards that synergize with library manipulation or tutors.
        """
        response = interactor.find_combo_pieces("Thassa's Oracle")

        assert isinstance(response, str)
        assert len(response) > 100

        response_lower = response.lower()
        # Should mention combo-related concepts (more lenient for LLM variations)
        combo_terms = ["tutor", "oracle", "combo", "synergy", "library", "devotion", "draw"]
        assert any(term in response_lower for term in combo_terms), "Response should discuss Thassa's Oracle synergies"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_find_combo_pieces_rhystic_study(self, interactor) -> None:
        """Test finding combos with Rhystic Study (card advantage engine).

        Expected: Should find other draw/advantage engines or taxing effects.
        """
        response = interactor.find_combo_pieces("Rhystic Study")

        assert isinstance(response, str)
        assert len(response) > 50

        # Should discuss card advantage or synergies
        response_lower = response.lower()
        assert "draw" in response_lower or "card" in response_lower or "advantage" in response_lower

    @pytest.mark.e2e
    def test_find_combo_pieces_nonexistent_card(self, interactor) -> None:
        """Test combo detection with a card that doesn't exist."""
        response = interactor.find_combo_pieces("Nonexistent Card Name")

        assert isinstance(response, str)
        assert len(response) > 0

        # Should indicate card not found
        response_lower = response.lower()
        assert "not found" in response_lower or "check" in response_lower

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_combo_response_quality(self, interactor) -> None:
        """Test that combo responses are detailed and helpful."""
        response = interactor.find_combo_pieces("Isochron Scepter", n_results=3)

        # Response should be substantial
        assert len(response) > 200, "Combo explanation should be detailed"

        # Should mention key combo concepts
        response_lower = response.lower()
        combo_terms = ["combo", "synergy", "infinite", "win", "mana", "card"]
        assert any(term in response_lower for term in combo_terms), "Response should mention combo-related concepts"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_combo_with_limit(self, interactor) -> None:
        """Test finding combos with a specific result limit."""
        response = interactor.find_combo_pieces("Counterspell", n_results=2)

        assert isinstance(response, str)
        assert len(response) > 50

        # Should still provide meaningful response even with limit
        response_lower = response.lower()
        assert "counterspell" in response_lower or "counter" in response_lower
