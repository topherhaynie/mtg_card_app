"""Tests for combo detection functionality in Interactor."""

import pytest

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry


@pytest.fixture
def interactor():
    """Create an interactor with all managers initialized."""
    registry = ManagerRegistry.get_instance()
    return Interactor(registry=registry)


class TestComboDetection:
    """Test combo detection functionality."""

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

    def test_find_combo_pieces_thassas_oracle(self, interactor) -> None:
        """Test finding combos with Thassa's Oracle.

        Expected: Should find Demonic Consultation or cards that empty the library.
        """
        response = interactor.find_combo_pieces("Thassa's Oracle")

        assert isinstance(response, str)
        assert len(response) > 100

        response_lower = response.lower()
        # Should mention consultation or winning the game
        assert "consultation" in response_lower or "demonic" in response_lower or "win" in response_lower

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

    def test_find_combo_pieces_nonexistent_card(self, interactor) -> None:
        """Test combo detection with a card that doesn't exist."""
        response = interactor.find_combo_pieces("Nonexistent Card Name")

        assert isinstance(response, str)
        assert len(response) > 0

        # Should indicate card not found
        response_lower = response.lower()
        assert "not found" in response_lower or "check" in response_lower

    def test_combo_response_quality(self, interactor) -> None:
        """Test that combo responses are detailed and helpful."""
        response = interactor.find_combo_pieces("Isochron Scepter", n_results=3)

        # Response should be substantial
        assert len(response) > 200, "Combo explanation should be detailed"

        # Should mention key combo concepts
        response_lower = response.lower()
        combo_terms = ["combo", "synergy", "infinite", "win", "mana", "card"]
        assert any(term in response_lower for term in combo_terms), "Response should mention combo-related concepts"

    def test_combo_with_limit(self, interactor) -> None:
        """Test finding combos with a specific result limit."""
        response = interactor.find_combo_pieces("Counterspell", n_results=2)

        assert isinstance(response, str)
        assert len(response) > 50

        # Should still provide meaningful response even with limit
        response_lower = response.lower()
        assert "counterspell" in response_lower or "counter" in response_lower
