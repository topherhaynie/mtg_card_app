"""Unit tests for Interactor filter extraction logic.

These are TRUE unit tests with mocked LLM - testing OUR logic, not Ollama's intelligence.
Tests verify that our code correctly converts LLM output to ChromaDB filter format.
"""

import json
from unittest.mock import Mock

from mtg_card_app.core.interactor import Interactor
from tests.mocks import MockLLMService


class TestFilterExtraction:
    """Test filter extraction with mocked LLM - fast and deterministic.

    These tests verify that _extract_filters() correctly:
    1. Calls the LLM with proper prompts
    2. Parses the LLM's JSON response
    3. Converts simple filters to ChromaDB format
    """

    def test_extract_blue_color_filter(self, mock_llm: MockLLMService) -> None:
        """Test extraction of blue color filter from user query.

        MockLLM returns: {"colors": "U"}
        Interactor converts to: {"color_identity": "U"}
        """
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Show me blue counterspells")

        # Verify ChromaDB format conversion
        assert filters == {"color_identity": "U"}
        assert mock_llm.generate_count == 1

    def test_extract_red_color_filter(self, mock_llm: MockLLMService) -> None:
        """Test extraction of red color filter from user query."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Find red burn spells")

        assert filters == {"color_identity": "R"}

    def test_extract_cmc_filter_under_3(self, mock_llm: MockLLMService) -> None:
        """Test extraction of CMC filter ('under 3' means 2 or less)."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Find creatures under 3 mana")

        assert filters == {"cmc": {"$lte": 2}}

    def test_extract_cmc_filter_3_or_less(self, mock_llm: MockLLMService) -> None:
        """Test extraction of CMC filter ('3 or less' means 3)."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Show spells 3 or less")

        assert filters == {"cmc": {"$lte": 3}}

    def test_extract_combined_color_and_cmc_filters(self, mock_llm: MockLLMService) -> None:
        """Test extraction of multiple filters from single query."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Show me blue spells under 4 mana")

        # Multiple filters are wrapped in $and
        assert filters == {"$and": [{"color_identity": "U"}, {"cmc": {"$lte": 3}}]}

    def test_no_filters_extracted_from_general_query(self, mock_llm: MockLLMService) -> None:
        """Test query with no explicit filters returns empty dict."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("What are some infinite combos?")

        assert filters == {}

    def test_extract_grixis_multicolor_filter(self, mock_llm: MockLLMService) -> None:
        """Test extraction of multicolor (Grixis = UBR) filter."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Show me Grixis control cards")

        assert filters == {"color_identity": "U,B,R"}

    def test_llm_called_with_extraction_prompt(self, mock_llm: MockLLMService) -> None:
        """Test that LLM receives proper filter extraction prompt."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        interactor._extract_filters("blue counterspells")

        # Verify LLM was called
        assert len(mock_llm.calls) == 1
        prompt = mock_llm.calls[0]

        # Verify prompt contains key elements
        assert "filter extraction" in prompt.lower()
        assert "blue counterspells" in prompt

    def test_extract_handles_invalid_json_from_llm(self) -> None:
        """Test graceful handling when LLM returns invalid JSON."""
        # Create mock LLM that returns invalid JSON
        mock_llm = MockLLMService(responses={"extract": "not valid json"})

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        # Should return empty dict on JSON parse error
        filters = interactor._extract_filters("blue cards")

        assert filters == {}

    def test_custom_response_override(self, mock_llm_with_responses) -> None:
        """Test that custom responses can override default behavior."""
        custom_mock = mock_llm_with_responses(
            {
                "blue": json.dumps({"colors": "U", "custom": "override"}),
            }
        )

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=custom_mock,
        )

        filters = interactor._extract_filters("blue cards")

        # Should use custom response and convert to ChromaDB format
        assert filters == {"color_identity": "U"}


class TestFilterExtractionEdgeCases:
    """Test edge cases in filter extraction."""

    def test_empty_query_string(self, mock_llm: MockLLMService) -> None:
        """Test handling of empty query string.

        Note: The mock still receives a valid prompt with examples, so it may
        return filters. In production, the real LLM would likely return {}.
        This test verifies the code doesn't crash with empty input.
        """
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        # Should not crash - result doesn't matter for this edge case
        filters = interactor._extract_filters("")

        # Verify it returns a dict (doesn't crash)
        assert isinstance(filters, dict)

    def test_query_with_special_characters(self, mock_llm: MockLLMService) -> None:
        """Test handling of queries with special characters."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        filters = interactor._extract_filters("Find cards with {T}: ability")

        # Should not crash, should handle gracefully
        assert isinstance(filters, dict)

    def test_multiple_color_mentions_uses_first(self, mock_llm: MockLLMService) -> None:
        """Test that when multiple colors mentioned, mock picks first one."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )

        # Mock LLM will pick first color mentioned (blue)
        filters = interactor._extract_filters("blue or red spells")

        # Should extract blue (first mentioned) and convert to ChromaDB format
        assert filters == {"color_identity": "U"}
