"""Unit tests for Interactor card operation methods.

These are TRUE unit tests with mocked dependencies - testing OUR logic, not external services.
"""

from unittest.mock import Mock

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities import Card


class TestFetchCard:
    """Test the fetch_card method."""

    def test_fetch_card_calls_card_manager(self) -> None:
        """Test that fetch_card delegates to card_data_manager."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="bolt",
            name="Lightning Bolt",
            type_line="Instant",
            oracle_text="Deal 3 damage",
            cmc=1,
            colors=["R"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.fetch_card("Lightning Bolt")

        # Should call card manager with name
        mock_card_manager.get_card.assert_called_once_with("Lightning Bolt")

        # Should return the card
        assert result is not None
        assert result.name == "Lightning Bolt"

    def test_fetch_card_returns_none_when_not_found(self) -> None:
        """Test that fetch_card returns None when card doesn't exist."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = None

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.fetch_card("Nonexistent Card")

        # Should return None
        assert result is None


class TestSearchCards:
    """Test the search_cards method."""

    def test_search_cards_uses_local_by_default(self) -> None:
        """Test that search uses local DB by default."""
        mock_card_manager = Mock()
        mock_card_manager.search_cards.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        interactor.search_cards("bolt")

        # Should call with use_local=True, use_scryfall=False
        mock_card_manager.search_cards.assert_called_once_with(
            "bolt",
            use_local=True,
            use_scryfall=False,
        )

    def test_search_cards_can_use_scryfall(self) -> None:
        """Test that search can use Scryfall when requested."""
        mock_card_manager = Mock()
        mock_card_manager.search_cards.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        interactor.search_cards("bolt", use_scryfall=True)

        # Should call with use_scryfall=True
        call_kwargs = mock_card_manager.search_cards.call_args.kwargs
        assert call_kwargs["use_scryfall"] is True

    def test_search_cards_returns_results(self) -> None:
        """Test that search returns card list."""
        mock_card_manager = Mock()
        mock_card_manager.search_cards.return_value = [
            Card(
                id="bolt",
                name="Lightning Bolt",
                type_line="Instant",
                oracle_text="Deal 3",
                cmc=1,
                colors=["R"],
            ),
            Card(
                id="bolt2",
                name="Chain Lightning",
                type_line="Sorcery",
                oracle_text="Deal 3",
                cmc=1,
                colors=["R"],
            ),
        ]

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        results = interactor.search_cards("lightning")

        # Should return list of cards
        assert len(results) == 2
        assert all(isinstance(card, Card) for card in results)

    def test_search_cards_handles_empty_results(self) -> None:
        """Test that search handles no results gracefully."""
        mock_card_manager = Mock()
        mock_card_manager.search_cards.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        results = interactor.search_cards("nonexistent")

        # Should return empty list
        assert results == []


class TestImportCards:
    """Test the import_cards method."""

    def test_import_cards_calls_bulk_import(self) -> None:
        """Test that import delegates to bulk_import_cards."""
        mock_card_manager = Mock()
        mock_card_manager.bulk_import_cards.return_value = {
            "imported": 3,
            "skipped": 0,
            "failed": 0,
        }

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        card_names = ["Sol Ring", "Mana Crypt", "Mana Vault"]
        result = interactor.import_cards(card_names)

        # Should call bulk_import_cards with list
        mock_card_manager.bulk_import_cards.assert_called_once_with(card_names)

        # Should return stats
        assert result["imported"] == 3

    def test_import_cards_returns_statistics(self) -> None:
        """Test that import returns detailed statistics."""
        mock_card_manager = Mock()
        mock_card_manager.bulk_import_cards.return_value = {
            "imported": 2,
            "skipped": 1,
            "failed": 1,
            "total": 4,
        }

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.import_cards(["Card1", "Card2", "Card3", "Card4"])

        # Should return dict with stats
        assert isinstance(result, dict)
        assert "imported" in result
        assert "skipped" in result
        assert "failed" in result

    def test_import_cards_handles_empty_list(self) -> None:
        """Test that import handles empty card list."""
        mock_card_manager = Mock()
        mock_card_manager.bulk_import_cards.return_value = {
            "imported": 0,
            "skipped": 0,
            "failed": 0,
        }

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.import_cards([])

        # Should handle empty list gracefully
        mock_card_manager.bulk_import_cards.assert_called_once_with([])
        assert result["imported"] == 0


class TestGetBudgetCards:
    """Test the get_budget_cards method."""

    def test_get_budget_cards_calls_manager(self) -> None:
        """Test that get_budget_cards delegates to card manager."""
        mock_card_manager = Mock()
        mock_card_manager.get_budget_cards.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        interactor.get_budget_cards(5.0)

        # Should call with max_price
        mock_card_manager.get_budget_cards.assert_called_once_with(5.0)

    def test_get_budget_cards_returns_filtered_list(self) -> None:
        """Test that budget cards are returned."""
        mock_card_manager = Mock()
        mock_card_manager.get_budget_cards.return_value = [
            Card(
                id="bolt",
                name="Lightning Bolt",
                type_line="Instant",
                oracle_text="Deal 3",
                cmc=1,
                colors=["R"],
            ),
        ]

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        results = interactor.get_budget_cards(10.0)

        # Should return list of cards
        assert len(results) == 1
        assert isinstance(results[0], Card)

    def test_get_budget_cards_handles_no_results(self) -> None:
        """Test that no budget cards returns empty list."""
        mock_card_manager = Mock()
        mock_card_manager.get_budget_cards.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        results = interactor.get_budget_cards(0.01)

        # Should return empty list
        assert results == []


class TestGetSystemStats:
    """Test the get_system_stats method."""

    def test_get_system_stats_collects_all_stats(self) -> None:
        """Test that system stats are collected from all managers."""
        mock_card_manager = Mock()
        mock_card_manager.get_stats.return_value = {"cards": 100}

        mock_rag_manager = Mock()
        mock_rag_manager.get_stats.return_value = {"embeddings": 100}

        mock_llm_manager = Mock()
        mock_llm_manager.get_stats.return_value = {"model": "llama3"}

        mock_db_manager = Mock()
        mock_db_manager.get_stats.return_value = {"size": "10MB"}

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag_manager,
            llm_manager=mock_llm_manager,
            db_manager=mock_db_manager,
        )

        result = interactor.get_system_stats()

        # Should collect from all managers
        assert "card_data" in result
        assert "rag" in result
        assert "llm" in result
        assert "db" in result
        assert result["card_data"]["cards"] == 100

    def test_get_system_stats_handles_missing_stats_method(self) -> None:
        """Test that stats handles managers without get_stats method."""
        mock_card_manager = Mock(spec=[])  # No get_stats method

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.get_system_stats()

        # Should handle missing method gracefully
        assert "card_data" in result
        assert result["card_data"] is None

    def test_get_system_stats_handles_none_db_manager(self) -> None:
        """Test that stats handles None db_manager."""
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=None,
        )

        result = interactor.get_system_stats()

        # Should handle None db_manager
        assert "db" in result
        assert result["db"] is None
