"""Unit tests for Interactor natural language query handling logic.

These are TRUE unit tests with mocked dependencies - testing OUR logic, not external services.
"""

from unittest.mock import Mock

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities import Card
from tests.mocks import MockLLMService


class TestQueryWorkflow:
    """Test the natural language query workflow with mocked dependencies."""

    def test_query_extracts_filters_when_enabled(self, mock_llm: MockLLMService) -> None:
        """Test that query extraction happens when use_filters=True."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_filters=True,
        )

        # Should call RAG with filters
        assert mock_rag.search_similar.called
        call_kwargs = mock_rag.search_similar.call_args.kwargs
        filters = call_kwargs.get("filters")

        # Filters should be applied (blue → color_identity: U)
        assert filters is not None
        assert "color_identity" in filters

    def test_query_skips_filters_when_disabled(self, mock_llm: MockLLMService) -> None:
        """Test that filter extraction is skipped when use_filters=False."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_filters=False,
        )

        # Should call RAG without filters
        call_kwargs = mock_rag.search_similar.call_args.kwargs
        filters = call_kwargs.get("filters")

        # Filters should be None
        assert filters is None

    def test_query_searches_rag_with_user_query(self, mock_llm: MockLLMService) -> None:
        """Test that user query is passed to RAG search."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.answer_natural_language_query("Find efficient removal spells")

        # Verify RAG search was called with user query
        assert mock_rag.search_similar.called
        call_kwargs = mock_rag.search_similar.call_args.kwargs
        assert call_kwargs.get("query") == "Find efficient removal spells"

    def test_query_requests_n_results_from_rag(self, mock_llm: MockLLMService) -> None:
        """Test that RAG search requests appropriate number of results."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.answer_natural_language_query("Show me powerful cards")

        # Should request 5 results by default
        call_kwargs = mock_rag.search_similar.call_args.kwargs
        assert call_kwargs.get("n_results") == 5

    def test_query_fetches_card_details(self, mock_llm: MockLLMService) -> None:
        """Test that full card details are fetched for search results."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("bolt", 0.95, {}),
            ("path", 0.88, {}),
        ]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="bolt",
            name="Lightning Bolt",
            type_line="Instant",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            cmc=1,
            colors=["R"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.answer_natural_language_query("efficient removal")

        # Should fetch card details for each result
        assert mock_card_manager.get_card_by_id.called
        assert mock_card_manager.get_card_by_id.call_count >= 1

    def test_query_provides_cards_to_llm(self, mock_llm: MockLLMService) -> None:
        """Test that LLM receives card details for formatting."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("bolt", 0.95, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="bolt",
            name="Lightning Bolt",
            type_line="Instant",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            cmc=1,
            colors=["R"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Find burn spells")

        # LLM should be called with card details
        assert mock_llm.generate_count == 2  # 1 for filter + 1 for format
        format_prompt = mock_llm.calls[1]  # Second call is format

        # Prompt should include card details
        assert "Lightning Bolt" in format_prompt
        assert "Instant" in format_prompt
        assert "3 damage" in format_prompt

    def test_query_returns_llm_formatted_response(self, mock_llm: MockLLMService) -> None:
        """Test that the function returns LLM's formatted response."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("card1", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Creature",
            oracle_text="Does things.",
            cmc=3,
            colors=["G"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Show me cards")

        # Should return string response
        assert isinstance(result, str)
        assert len(result) > 0


class TestQueryEdgeCases:
    """Test edge cases in query handling."""

    def test_query_handles_no_search_results(self, mock_llm: MockLLMService) -> None:
        """Test graceful handling when RAG returns no results."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Find unicorn cards")

        # Should return helpful message
        assert isinstance(result, str)
        assert "no cards found" in result.lower()

    def test_query_handles_no_results_with_filters(self, mock_llm: MockLLMService) -> None:
        """Test that no-results message mentions filters when applied."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_filters=True,
        )

        # Should suggest broadening search
        assert isinstance(result, str)
        assert "filter" in result.lower() or "broaden" in result.lower()

    def test_query_handles_cards_not_retrievable(self, mock_llm: MockLLMService) -> None:
        """Test handling when RAG returns IDs but cards can't be fetched."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("missing1", 0.9, {}),
            ("missing2", 0.8, {}),
        ]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = None  # Cards not found

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Show me cards")

        # Should return error message
        assert isinstance(result, str)
        assert "could not be retrieved" in result.lower()

    def test_query_handles_partial_card_retrieval(self, mock_llm: MockLLMService) -> None:
        """Test handling when some cards can be retrieved but others can't."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("good", 0.9, {}),
            ("missing", 0.8, {}),
            ("also_good", 0.7, {}),
        ]

        def get_card_side_effect(card_id, fetch_if_missing=False):
            if card_id == "missing":
                return None
            return Card(
                id=card_id,
                name=f"Card {card_id}",
                type_line="Test",
                oracle_text="Test card",
                cmc=2,
                colors=[],
            )

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.side_effect = get_card_side_effect

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Show me cards")

        # Should still process the retrievable cards
        assert isinstance(result, str)
        # Should have called LLM with partial results
        assert mock_llm.generate_count >= 1

    def test_query_includes_power_toughness_for_creatures(self, mock_llm: MockLLMService) -> None:
        """Test that creature cards include power/toughness in context."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("delver", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="delver",
            name="Delver of Secrets",
            type_line="Creature — Human Wizard",
            oracle_text="At the beginning of your upkeep...",
            cmc=1,
            colors=["U"],
            power="1",
            toughness="1",
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Find efficient creatures")

        # LLM prompt should include power/toughness
        format_prompt = mock_llm.calls[1]  # Second call is format
        assert "1/1" in format_prompt or ("power_toughness" in format_prompt and "1" in format_prompt)


class TestQueryCaching:
    """Test caching behavior in query handling."""

    def test_query_uses_cache_when_enabled(self, mock_llm: MockLLMService) -> None:
        """Test that query uses cache when enabled."""
        mock_cache = Mock()
        mock_cache.get.return_value = (True, "Cached response about blue cards")

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_cache=True,
            use_filters=False,  # Disable filters to avoid LLM call
        )

        # Should return cached result
        assert result == "Cached response about blue cards"

        # Should check cache
        assert mock_cache.get.called

        # Should NOT call LLM for formatting when cached (filters disabled)
        assert mock_llm.generate_count == 0

    def test_query_stores_in_cache(self, mock_llm: MockLLMService) -> None:
        """Test that query results are stored in cache."""
        mock_cache = Mock()
        mock_cache.get.return_value = (False, None)  # Cache miss

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("card1", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.answer_natural_language_query("Show me cards", use_cache=True)

        # Should store result in cache
        assert mock_cache.set.called

        # Verify cache key includes query
        cache_args = mock_cache.set.call_args[0]
        assert "Show me cards" in cache_args[0]

    def test_query_cache_includes_filters(self, mock_llm: MockLLMService) -> None:
        """Test that cache key includes filter information."""
        mock_cache = Mock()
        mock_cache.get.return_value = (False, None)

        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_cache=True,
            use_filters=True,
        )

        # Cache.get should be called with query and filters
        assert mock_cache.get.called
        get_args = mock_cache.get.call_args[0]
        # First arg is query, second should be filters dict
        assert len(get_args) >= 2

    def test_query_bypasses_cache_when_disabled(self, mock_llm: MockLLMService) -> None:
        """Test that cache is bypassed when use_cache=False."""
        mock_cache = Mock()

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("card1", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.answer_natural_language_query("Show me cards", use_cache=False)

        # Should NOT check or store in cache
        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()

    def test_query_caches_no_results_message(self, mock_llm: MockLLMService) -> None:
        """Test that 'no results' messages are also cached."""
        mock_cache = Mock()
        mock_cache.get.return_value = (False, None)

        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.answer_natural_language_query("Find unicorns", use_cache=True)

        # Should cache the no-results message
        assert mock_cache.set.called
        cached_value = mock_cache.set.call_args[0][1]
        assert "no cards found" in cached_value.lower()


class TestQueryContextBuilding:
    """Test the LLM context building for queries."""

    def test_query_includes_relevance_scores(self, mock_llm: MockLLMService) -> None:
        """Test that card context includes relevance scores."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("card1", 0.95, {}),
            ("card2", 0.82, {}),
        ]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Show me cards")

        # LLM format prompt should include relevance scores
        format_prompt = mock_llm.calls[1]
        assert "0.95" in format_prompt or "relevance" in format_prompt.lower()

    def test_query_prompt_includes_user_query(self, mock_llm: MockLLMService) -> None:
        """Test that LLM prompt includes the user's original query."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("card1", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query("Find efficient removal")

        # Format prompt should include user query
        format_prompt = mock_llm.calls[1]
        assert "Find efficient removal" in format_prompt

    def test_query_prompt_mentions_filters_when_applied(self, mock_llm: MockLLMService) -> None:
        """Test that LLM prompt mentions when filters were applied."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("card1", 0.9, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card_by_id.return_value = Card(
            id="card1",
            name="Counterspell",
            type_line="Instant",
            oracle_text="Counter target spell.",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.answer_natural_language_query(
            "Show me blue counterspells",
            use_filters=True,
        )

        # Format prompt should mention filters
        format_prompt = mock_llm.calls[1]
        assert "filter" in format_prompt.lower() or "color_identity" in format_prompt
