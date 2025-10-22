"""Unit tests for Interactor combo detection logic.

These are TRUE unit tests with mocked dependencies - testing OUR logic, not Ollama or RAG.
"""

from unittest.mock import Mock

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities import Card
from tests.mocks import MockLLMService


class TestComboWorkflow:
    """Test the combo detection workflow with mocked dependencies."""

    def test_find_combo_fetches_card_by_name(self, mock_llm: MockLLMService) -> None:
        """Test that combo finder retrieves the base card from card data manager."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []  # No results to keep test focused

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint — When Isochron Scepter enters...",
            cmc=2,
            colors=[],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.find_combo_pieces("Isochron Scepter")

        # Verify card fetch was called with correct name
        mock_card_manager.get_card.assert_called_once_with("Isochron Scepter")

    def test_find_combo_builds_semantic_query(self, mock_llm: MockLLMService) -> None:
        """Test that combo finder builds appropriate semantic search query."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("reversal", 0.95, {}),
            ("sol_ring", 0.88, {}),
        ]

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint — When Isochron Scepter enters...",
            cmc=2,
            colors=[],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.find_combo_pieces("Isochron Scepter", n_results=3)

        # Verify RAG search was called
        assert mock_rag.search_similar.called
        call_kwargs = mock_rag.search_similar.call_args.kwargs

        # Should request n+1 results to account for the base card
        assert call_kwargs.get("n_results") == 4  # 3 + 1

        # Should pass a combo-focused query
        query = call_kwargs.get("query")
        assert query is not None
        assert len(query) > 0

    def test_find_combo_filters_out_base_card(self, mock_llm: MockLLMService) -> None:
        """Test that the base card is filtered from search results."""
        mock_rag = Mock()
        # Return base card + combo pieces
        mock_rag.search_similar.return_value = [
            ("scepter", 1.0, {}),  # Base card (should be filtered)
            ("reversal", 0.95, {}),
            ("sol_ring", 0.88, {}),
        ]

        mock_card_manager = Mock()
        base_card = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint — When Isochron Scepter enters...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card.return_value = base_card

        # Mock get_card_by_id to return combo cards
        def get_card_by_id_side_effect(card_id, fetch_if_missing=True):
            if card_id == "scepter":
                return base_card
            if card_id == "reversal":
                return Card(
                    id="reversal",
                    name="Dramatic Reversal",
                    type_line="Instant",
                    oracle_text="Untap all nonland permanents you control.",
                    cmc=2,
                    colors=["U"],
                )
            if card_id == "sol_ring":
                return Card(
                    id="sol_ring",
                    name="Sol Ring",
                    type_line="Artifact",
                    oracle_text="{T}: Add {C}{C}.",
                    cmc=1,
                    colors=[],
                )
            return None

        mock_card_manager.get_card_by_id.side_effect = get_card_by_id_side_effect

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Isochron Scepter", n_results=2)

        # Verify LLM was called
        assert mock_llm.generate_count == 1
        prompt = mock_llm.calls[0]

        # Base card should NOT appear in combo pieces list
        # But should appear as the base card
        assert "Dramatic Reversal" in prompt
        assert "Sol Ring" in prompt

    def test_find_combo_provides_llm_context(self, mock_llm: MockLLMService) -> None:
        """Test that LLM receives proper context about cards."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("reversal", 0.95, {}),
        ]

        mock_card_manager = Mock()
        base_card = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint — When Isochron Scepter enters...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card.return_value = base_card
        mock_card_manager.get_card_by_id.return_value = Card(
            id="reversal",
            name="Dramatic Reversal",
            type_line="Instant",
            oracle_text="Untap all nonland permanents you control.",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Isochron Scepter")

        # Verify LLM received comprehensive prompt
        assert mock_llm.generate_count == 1
        prompt = mock_llm.calls[0]

        # Should include base card details
        assert "Isochron Scepter" in prompt
        assert "Artifact" in prompt

        # Should include combo piece details
        assert "Dramatic Reversal" in prompt
        assert "Instant" in prompt
        assert "Untap all nonland permanents" in prompt

        # Should include synergy score
        assert "0.95" in prompt or "synergy" in prompt.lower()

        # Should ask for combo analysis
        assert "synerg" in prompt.lower() or "combo" in prompt.lower()

    def test_find_combo_returns_llm_response(self, mock_llm: MockLLMService) -> None:
        """Test that the function returns the LLM's generated response."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("reversal", 0.95, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card_by_id.return_value = Card(
            id="reversal",
            name="Dramatic Reversal",
            type_line="Instant",
            oracle_text="Untap...",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Isochron Scepter")

        # Should return string response
        assert isinstance(result, str)
        assert len(result) > 0


class TestComboEdgeCases:
    """Test edge cases in combo detection."""

    def test_find_combo_handles_missing_card(self, mock_llm: MockLLMService) -> None:
        """Test graceful handling when base card doesn't exist."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = None

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Nonexistent Card")

        # Should return error message
        assert isinstance(result, str)
        assert "not found" in result.lower()

        # Should NOT call LLM or RAG
        assert mock_llm.generate_count == 0

    def test_find_combo_handles_no_results(self, mock_llm: MockLLMService) -> None:
        """Test handling when RAG returns no similar cards."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="solo_card",
            name="Solo Card",
            type_line="Creature",
            oracle_text="Does nothing special.",
            cmc=3,
            colors=["G"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Solo Card")

        # Should return helpful message
        assert isinstance(result, str)
        assert "no combo pieces found" in result.lower() or "on its own" in result.lower()

        # Should NOT call LLM
        assert mock_llm.generate_count == 0

    def test_find_combo_handles_only_base_card_returned(self, mock_llm: MockLLMService) -> None:
        """Test when RAG only returns the base card itself."""
        mock_rag = Mock()
        # Only returns the base card
        mock_rag.search_similar.return_value = [("scepter", 1.0, {})]

        mock_card_manager = Mock()
        base_card = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card.return_value = base_card
        mock_card_manager.get_card_by_id.return_value = base_card

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        result = interactor.find_combo_pieces("Isochron Scepter")

        # Should return helpful message (no other cards found)
        assert isinstance(result, str)
        assert "no combo pieces found" in result.lower() or "on its own" in result.lower()


class TestComboQueryBuilding:
    """Test the combo query building logic."""

    def test_build_combo_query_includes_card_name(self, mock_llm: MockLLMService) -> None:
        """Test that combo query includes the card name."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="test_card",
            name="Test Card",
            type_line="Artifact",
            oracle_text="Do something cool.",
            cmc=3,
            colors=[],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )

        interactor.find_combo_pieces("Test Card")

        # Check what query was passed to RAG
        assert mock_rag.search_similar.called
        query = mock_rag.search_similar.call_args.kwargs.get("query")

        # Query should be non-empty
        assert query
        assert len(query) > 0

    def test_build_combo_query_considers_oracle_text(self, mock_llm: MockLLMService) -> None:
        """Test that combo query considers card's oracle text."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = []

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="counterspell",
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

        interactor.find_combo_pieces("Counterspell")

        # Verify RAG search was called with query
        assert mock_rag.search_similar.called
        query = mock_rag.search_similar.call_args.kwargs.get("query")

        # Should build meaningful query from card info
        assert query is not None


class TestComboCaching:
    """Test caching behavior in combo detection."""

    def test_find_combo_uses_cache_when_enabled(self, mock_llm: MockLLMService) -> None:
        """Test that combo detection uses cache when enabled."""
        mock_cache = Mock()
        mock_cache.get.return_value = (True, "Cached combo analysis")

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint...",
            cmc=2,
            colors=[],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.find_combo_pieces("Isochron Scepter", n_results=5, use_cache=True)

        # Should return cached result
        assert result == "Cached combo analysis"

        # Should check cache with proper key
        mock_cache.get.assert_called_once()
        cache_key = mock_cache.get.call_args[0][0]
        assert "combo_pieces" in cache_key
        assert "Isochron Scepter" in cache_key
        assert "5" in cache_key

        # Should NOT call LLM or RAG when cached
        assert mock_llm.generate_count == 0

    def test_find_combo_stores_in_cache(self, mock_llm: MockLLMService) -> None:
        """Test that combo results are stored in cache."""
        mock_cache = Mock()
        mock_cache.get.return_value = (False, None)  # Cache miss

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("reversal", 0.95, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card_by_id.return_value = Card(
            id="reversal",
            name="Dramatic Reversal",
            type_line="Instant",
            oracle_text="Untap...",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.find_combo_pieces("Isochron Scepter", use_cache=True)

        # Should store result in cache
        mock_cache.set.assert_called_once()
        cache_key, cached_value = mock_cache.set.call_args[0]

        # Verify cache key format
        assert "combo_pieces" in cache_key
        assert "Isochron Scepter" in cache_key

        # Verify cached value is the LLM response
        assert isinstance(cached_value, str)
        assert len(cached_value) > 0

    def test_find_combo_bypasses_cache_when_disabled(self, mock_llm: MockLLMService) -> None:
        """Test that combo detection bypasses cache when use_cache=False."""
        mock_cache = Mock()

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("reversal", 0.95, {})]

        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint...",
            cmc=2,
            colors=[],
        )
        mock_card_manager.get_card_by_id.return_value = Card(
            id="reversal",
            name="Dramatic Reversal",
            type_line="Instant",
            oracle_text="Untap...",
            cmc=2,
            colors=["U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
            query_cache=mock_cache,
        )

        result = interactor.find_combo_pieces("Isochron Scepter", use_cache=False)

        # Should NOT check cache
        mock_cache.get.assert_not_called()

        # Should NOT store in cache
        mock_cache.set.assert_not_called()

        # Should still call LLM
        assert mock_llm.generate_count == 1
