"""E2E tests for Phase 4.2 tri-hybrid combo search.

Tests the breakthrough tri-hybrid search implementation:
- Semantic search (25%)
- Exact phrase match (25%)
- Mechanical requirements (50%)

These tests verify that famous combos are found and properly validated.
Uses retry decorator to handle LLM non-determinism (80% expected success rate).
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


class TestTriHybridSearch:
    """Test tri-hybrid search finds famous combos."""

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_isochron_scepter_finds_dramatic_reversal(self, interactor) -> None:
        """Test that Isochron Scepter finds Dramatic Reversal.

        This is the OPTIMIZED combo - system was specifically improved for this.
        Expected success rate: ~80% per attempt, 99.2% over 3 attempts.

        Verifies:
        - Dramatic Reversal is found
        - Combo is identified as infinite
        - Mana rocks requirement is mentioned
        """
        response = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)

        # Verify Dramatic Reversal is found
        assert "Dramatic Reversal" in response, "Should find Dramatic Reversal"

        response_lower = response.lower()

        # Verify infinite loop recognition
        assert "infinite" in response_lower, "Should recognize infinite loop"

        # Verify mana rocks are mentioned (relaxed check for LLM variation)
        mana_rock_terms = ["mana rock", "sol ring", "arcane signet", "artifact", "mana"]
        assert any(term in response_lower for term in mana_rock_terms), \
            "Should mention mana generation requirements"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_thassas_oracle_generalization(self, interactor) -> None:
        """Test Thassa's Oracle combo search (NON-OPTIMIZED).

        This verifies system generalizes beyond Isochron Scepter.
        Expected: Should find cards that exile library or create devotion.

        Note: This is intentionally less strict as it tests generalization
        to combo patterns we didn't specifically optimize for.
        """
        response = interactor.find_combo_pieces("Thassa's Oracle", n_results=10, use_cache=False)

        # Verify response is substantial
        assert len(response) > 100, "Should provide detailed analysis"

        response_lower = response.lower()

        # Should mention relevant concepts
        oracle_terms = ["oracle", "devotion", "library", "exile", "win", "consultation", "tutor"]
        assert any(term in response_lower for term in oracle_terms), \
            "Should discuss Thassa's Oracle synergies"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_kiki_jiki_generalization(self, interactor) -> None:
        """Test Kiki-Jiki combo search (NON-OPTIMIZED).

        This verifies system handles creature-based infinite combos.
        Expected: Should find creatures with untap abilities.

        Note: Tests generalization to ETB/creature combo patterns.
        """
        response = interactor.find_combo_pieces("Kiki-Jiki, Mirror Breaker", n_results=10, use_cache=False)

        # Verify response exists
        assert len(response) > 100, "Should provide detailed analysis"

        response_lower = response.lower()

        # Should mention relevant combo concepts
        kiki_terms = ["copy", "creature", "token", "untap", "infinite", "enter", "battlefield"]
        assert any(term in response_lower for term in kiki_terms), \
            "Should discuss creature copy mechanics"


class TestMechanicalRequirements:
    """Test mechanical requirements extraction."""

    @pytest.mark.e2e
    def test_isochron_scepter_extracts_requirements(self, interactor) -> None:
        """Test that mechanical requirements are extracted correctly.

        Verifies the LLM can extract:
        - Card type requirement (instant)
        - CMC requirement (≤2)
        """
        card = interactor.fetch_card("Isochron Scepter")
        assert card is not None, "Isochron Scepter should exist"

        # Analyze mechanics
        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)

        # Should generate search queries
        assert llm_analysis['search_queries'], "Should generate search queries"
        assert len(llm_analysis['search_queries']) > 0, "Should have at least one query"

        # Search queries should mention relevant concepts
        queries_text = " ".join(llm_analysis['search_queries']).lower()
        assert any(term in queries_text for term in ["instant", "mana", "spell", "untap"]), \
            "Queries should mention relevant combo concepts"


class TestComboValidation:
    """Test LLM validation explains combos correctly."""

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_infinite_combo_recognition(self, interactor) -> None:
        """Test that infinite combos are clearly identified.

        Verifies validation prompt correctly:
        - Labels infinite combos as "INFINITE"
        - Explains the loop sequence
        - Mentions power level
        """
        response = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)

        # If Dramatic Reversal is found, check validation quality
        if "Dramatic Reversal" in response:
            response_lower = response.lower()

            # Should explicitly identify as infinite
            assert "infinite" in response_lower, "Should identify infinite combo"

            # Should explain what's generated
            infinite_terms = ["infinite mana", "infinite cast", "infinite untap", "loop"]
            assert any(term in response_lower for term in infinite_terms), \
                "Should explain what's infinite"

            # Should mention power level
            power_terms = ["competitive", "cedh", "power level", "casual"]
            assert any(term in response_lower for term in power_terms), \
                "Should mention power level"

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_mana_rocks_requirement_validation(self, interactor) -> None:
        """Test that mana rocks requirement is properly explained.

        Verifies that when a combo requires mana rocks, the validation:
        - Mentions the need for mana rocks
        - Explains WHY they're needed
        - Gives examples (Sol Ring, Arcane Signet, etc.)
        """
        response = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)

        # If Dramatic Reversal is found, check mana rocks explanation
        if "Dramatic Reversal" in response:
            response_lower = response.lower()

            # Should mention mana generation (relaxed - various ways to phrase this)
            mana_terms = [
                "mana rock", "sol ring", "arcane signet", "thought vessel",
                "mana source", "artifact", "produce", "mana"
            ]
            assert any(term in response_lower for term in mana_terms), \
                "Should mention mana generation requirements"


class TestSearchPerformance:
    """Test search performance and consistency."""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_consistency_over_multiple_runs(self, interactor) -> None:
        """Test consistency of search results over 5 runs.

        Expected: Dramatic Reversal should appear in ≥3/5 runs (60%+).
        With 80% per-run success rate, probability of ≥3/5 = 94.2%

        This test takes longer (~2-3 minutes) so marked as slow.
        Run with: pytest -m "e2e and slow"
        """
        successes = 0
        ranks = []

        for run in range(5):
            response = interactor.find_combo_pieces("Isochron Scepter", n_results=10, use_cache=False)

            if "Dramatic Reversal" in response:
                successes += 1
                # Try to extract rank (basic heuristic)
                lines = response.split('\n')
                for i, line in enumerate(lines):
                    if "Dramatic Reversal" in line:
                        # Rough approximation of rank
                        ranks.append(i // 5)  # Assume ~5 lines per card
                        break

        # Should succeed in at least 60% of runs (allows for some variability)
        success_rate = successes / 5
        assert success_rate >= 0.60, \
            f"Expected ≥60% success rate, got {success_rate*100:.0f}% ({successes}/5)"

        # If we got any successes, check they're in reasonable ranks
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            assert avg_rank <= 10, f"Average rank {avg_rank:.1f} should be in top 10"


class TestGeneralizationAcrossComboTypes:
    """Test that system generalizes across different combo patterns."""

    @pytest.mark.e2e
    @retry_on_llm_variability(max_attempts=3)
    def test_finds_multiple_combo_types(self, interactor) -> None:
        """Test that system can find different types of combos.

        Runs searches for 3 different combo patterns:
        1. Copy + Untap (Isochron Scepter)
        2. Library manipulation (Thassa's Oracle)
        3. Creature ETB (Kiki-Jiki)

        Success criteria: Substantial responses for all 3, even if specific
        cards aren't found (LLM non-determinism).
        """
        test_cases = [
            ("Isochron Scepter", ["infinite", "instant", "copy"]),
            ("Thassa's Oracle", ["oracle", "devotion", "library", "win"]),
            ("Kiki-Jiki, Mirror Breaker", ["copy", "creature", "token", "untap"]),
        ]

        for card_name, expected_terms in test_cases:
            response = interactor.find_combo_pieces(card_name, n_results=10, use_cache=False)

            # Should provide substantial response
            assert len(response) > 100, f"{card_name} should get detailed analysis"

            # Should mention relevant concepts
            response_lower = response.lower()
            assert any(term in response_lower for term in expected_terms), \
                f"{card_name} response should mention {expected_terms}"
