"""Tests for the stats command."""

from __future__ import annotations

from unittest.mock import Mock, patch

from mtg_card_app.ui.cli.commands.stats import show_stats


class TestStatsCommand:
    """Test suite for the stats command."""

    def test_stats_display(self, mock_interactor: Mock) -> None:
        """Test stats command displays system information.

        Args:
            mock_interactor: Mock Interactor instance

        """
        # Mock get_system_stats is already configured in conftest
        with patch(
            "mtg_card_app.ui.cli.commands.stats.Interactor",
            return_value=mock_interactor,
        ):
            # Should not raise exception
            show_stats()

    def test_stats_with_minimal_data(self, mock_interactor: Mock) -> None:
        """Test stats with minimal data.

        Args:
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.get_system_stats.return_value = {}

        with patch(
            "mtg_card_app.ui.cli.commands.stats.Interactor",
            return_value=mock_interactor,
        ):
            # Should handle empty stats gracefully
            show_stats()

    def test_stats_with_llm_info(self, mock_interactor: Mock) -> None:
        """Test stats displays LLM information.

        Args:
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.get_system_stats.return_value = {
            "llm": {
                "provider": "ollama",
                "model": "llama3",
                "status": "connected",
            },
        }

        with patch(
            "mtg_card_app.ui.cli.commands.stats.Interactor",
            return_value=mock_interactor,
        ):
            show_stats()

    def test_stats_with_card_data(self, mock_interactor: Mock) -> None:
        """Test stats displays card data information.

        Args:
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.get_system_stats.return_value = {
            "card_data": {
                "total_cards": 35402,
            },
        }

        with patch(
            "mtg_card_app.ui.cli.commands.stats.Interactor",
            return_value=mock_interactor,
        ):
            show_stats()

    def test_stats_calls_interactor(self, mock_interactor: Mock) -> None:
        """Test that stats calls get_system_stats.

        Args:
            mock_interactor: Mock Interactor instance

        """
        with patch(
            "mtg_card_app.ui.cli.commands.stats.Interactor",
            return_value=mock_interactor,
        ):
            show_stats()

        mock_interactor.get_system_stats.assert_called_once()
