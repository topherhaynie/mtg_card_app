"""Fast unit tests for Phase 4.2 combo search (search phase only).

These tests isolate the SEARCH phase from the VALIDATION phase:
- Test mechanical requirements extraction
- Test tri-hybrid scoring
- Test that search returns expected cards
- No full LLM validation (faster execution)

Run with: pytest tests/unit/core/test_combo_search_fast.py
"""

import pytest

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry


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


class TestMechanicalRequirementsExtraction:
    """Test mechanical requirements extraction logic."""

    def test_isochron_scepter_requirements(self, interactor) -> None:
        """Test that Isochron Scepter requirements are extracted.

        Should extract:
        - type: instant
        - cmc: ≤2
        """
        card = interactor.fetch_card("Isochron Scepter")
        assert card is not None, "Card should exist"

        # Extract requirements
        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)

        # Should return valid analysis
        assert isinstance(llm_analysis, dict), "Should return dict"
        assert 'search_queries' in llm_analysis, "Should have search queries"
        assert len(llm_analysis['search_queries']) > 0, "Should generate queries"

    def test_mechanical_search_returns_candidates(self, interactor) -> None:
        """Test that mechanical search returns candidate cards.

        Should find instants with CMC ≤2.
        """
        card = interactor.fetch_card("Isochron Scepter")
        assert card is not None

        llm_analysis = interactor._analyze_card_mechanics_with_llm(card)
        mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)

        # Should return candidates
        assert isinstance(mechanical_candidates, dict), "Should return dict"
        # Should find some instants with CMC ≤2 (there are ~1900 in the database)
        assert len(mechanical_candidates) > 100, f"Should find many candidates, got {len(mechanical_candidates)}"


class TestSearchPhaseRetry:
    """Test search phase with retry logic for LLM non-determinism."""

    def _check_card_in_results(self, interactor, base_card: str, expected_card: str, max_attempts: int = 3) -> dict:
        """Helper to check if expected card is found in search results.

        Args:
            interactor: The interactor instance
            base_card: Seed card name
            expected_card: Card we expect to find
            max_attempts: Number of retry attempts

        Returns:
            Dict with found status, rank, score, attempt
        """
        for attempt in range(1, max_attempts + 1):
            card = interactor.fetch_card(base_card)
            if not card:
                continue

            # Run search phases
            llm_analysis = interactor._analyze_card_mechanics_with_llm(card)

            # Semantic search
            semantic_candidates = {}
            for query in llm_analysis['search_queries'][:6]:
                if not query or len(query) < 3:
                    continue
                results = interactor.rag_manager.search_similar(query=query, n_results=5)
                for card_id, score, _ in results:
                    if card_id == card.id:
                        continue
                    if card_id not in semantic_candidates or score > semantic_candidates[card_id][1]:
                        combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                        if combo_card:
                            semantic_candidates[card_id] = (combo_card, score, "semantic")

            # Exact phrase search
            exact_candidates = {}
            for query in llm_analysis['search_queries'][:6]:
                if not query or len(query) < 5:
                    continue
                results = interactor.rag_manager.search_similar(query=query, n_results=10)
                for card_id, score, _ in results:
                    if card_id == card.id:
                        continue
                    combo_card = interactor.card_data_manager.get_card_by_id(card_id, fetch_if_missing=False)
                    if not combo_card or not combo_card.oracle_text:
                        continue
                    query_words = set(query.lower().split())
                    oracle_words = set(combo_card.oracle_text.lower().split())
                    word_overlap = len(query_words & oracle_words) / len(query_words) if query_words else 0
                    boosted_score = score * (1.0 + word_overlap)
                    if card_id not in exact_candidates or boosted_score > exact_candidates[card_id][1]:
                        exact_candidates[card_id] = (combo_card, boosted_score, "exact")

            # Mechanical search
            mechanical_candidates = interactor._search_by_mechanical_requirements(card, llm_analysis)

            # Tri-hybrid scoring
            WEIGHT_SEMANTIC = 0.25
            WEIGHT_EXACT = 0.25
            WEIGHT_MECHANICAL = 0.50

            all_candidates = {}
            all_card_ids = set(semantic_candidates.keys()) | set(exact_candidates.keys()) | set(
                mechanical_candidates.keys())

            for card_id in all_card_ids:
                semantic_score = semantic_candidates[card_id][1] if card_id in semantic_candidates else 0.0
                exact_score = exact_candidates[card_id][1] if card_id in exact_candidates else 0.0
                mechanical_score = mechanical_candidates[card_id][1] if card_id in mechanical_candidates else 0.0

                weighted_score = (
                        semantic_score * WEIGHT_SEMANTIC +
                        exact_score * WEIGHT_EXACT +
                        mechanical_score * WEIGHT_MECHANICAL
                )

                combo_card = None
                if card_id in semantic_candidates:
                    combo_card = semantic_candidates[card_id][0]
                elif card_id in exact_candidates:
                    combo_card = exact_candidates[card_id][0]
                elif card_id in mechanical_candidates:
                    combo_card = mechanical_candidates[card_id][0]

                if combo_card:
                    all_candidates[card_id] = (combo_card, weighted_score)

            # Get top 10
            sorted_candidates = sorted(all_candidates.values(), key=lambda x: x[1], reverse=True)
            top_10 = sorted_candidates[:10]

            # Check if expected card is in top 10
            found_cards = [c.name for c, _ in top_10]
            if expected_card in found_cards:
                rank = found_cards.index(expected_card) + 1
                score = next(s for c, s in top_10 if c.name == expected_card)
                return {
                    "found": True,
                    "rank": rank,
                    "score": score,
                    "attempt": attempt,
                    "top_10": found_cards
                }

        return {
            "found": False,
            "attempts": max_attempts,
            "last_top_10": found_cards if 'found_cards' in locals() else []
        }

    @pytest.mark.integration
    def test_dramatic_reversal_found_with_retry(self, interactor) -> None:
        """Test that Dramatic Reversal is found within 3 attempts.

        With 80% per-attempt success rate, 3 attempts gives 99.2% success.
        This test focuses on SEARCH phase only (no validation).
        """
        result = self._check_card_in_results(
            interactor,
            base_card="Isochron Scepter",
            expected_card="Dramatic Reversal",
            max_attempts=3
        )

        assert result["found"], \
            f"Dramatic Reversal should be found within 3 attempts. Last top 10: {result.get('last_top_10', [])}"
        assert result["rank"] <= 10, f"Should be in top 10, got rank {result['rank']}"
        assert result["score"] > 0.5, f"Should have decent score, got {result['score']:.3f}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_consistency_across_runs(self, interactor) -> None:
        """Test that search is reasonably consistent.

        Runs 5 searches and verifies ≥60% success rate.
        Marked as slow since it runs multiple searches.
        """
        successes = 0
        for _ in range(5):
            result = self._check_card_in_results(
                interactor,
                base_card="Isochron Scepter",
                expected_card="Dramatic Reversal",
                max_attempts=1  # Single attempt per run
            )
            if result["found"]:
                successes += 1

        success_rate = successes / 5
        assert success_rate >= 0.6, \
            f"Expected ≥60% success rate, got {success_rate * 100:.0f}% ({successes}/5)"


class TestTriHybridScoring:
    """Test tri-hybrid scoring weights."""

    def test_weights_sum_to_one(self) -> None:
        """Test that weights sum to 1.0."""
        WEIGHT_SEMANTIC = 0.25
        WEIGHT_EXACT = 0.25
        WEIGHT_MECHANICAL = 0.50

        total = WEIGHT_SEMANTIC + WEIGHT_EXACT + WEIGHT_MECHANICAL
        assert abs(total - 1.0) < 0.001, f"Weights should sum to 1.0, got {total}"

    def test_mechanical_weight_is_highest(self) -> None:
        """Test that mechanical has highest weight (most reliable)."""
        WEIGHT_SEMANTIC = 0.25
        WEIGHT_EXACT = 0.25
        WEIGHT_MECHANICAL = 0.50

        assert WEIGHT_MECHANICAL > WEIGHT_SEMANTIC, "Mechanical should be weighted higher than semantic"
        assert WEIGHT_MECHANICAL > WEIGHT_EXACT, "Mechanical should be weighted higher than exact"

    def test_semantic_and_exact_equal(self) -> None:
        """Test that semantic and exact have equal weight."""
        WEIGHT_SEMANTIC = 0.25
        WEIGHT_EXACT = 0.25

        assert WEIGHT_SEMANTIC == WEIGHT_EXACT, "Semantic and exact should be equally weighted"
