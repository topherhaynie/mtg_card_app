"""Tests for the search command."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from mtg_card_app.ui.cli.commands.search import search

if TYPE_CHECKING:
    from click.testing import CliRunner


class TestSearchCommand:
    """Test suite for the search command."""

    def test_search_basic(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test basic search command.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = (
            "Found cards:\n- Lightning Bolt\n- Shock"
        )

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["Lightning Bolt"])

        assert result.exit_code == 0
        assert "Lightning Bolt" in result.output or "Searching" in result.output

    def test_search_multi_word(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search with multi-word query.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = (
            "Found cards:\n- Counterspell\n- Mana Drain"
        )

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["blue", "counterspells"])

        assert result.exit_code == 0
        mock_interactor.answer_natural_language_query.assert_called_once()

    def test_search_with_limit(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search with limit option.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = "Found 5 cards"

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["creatures", "--limit", "5"])

        assert result.exit_code == 0
        # Check that limit was passed to query
        call_args = mock_interactor.answer_natural_language_query.call_args[0][0]
        assert "5" in call_args

    def test_search_with_budget(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search with budget filter.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = "Budget cards found"

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["removal", "--budget", "1.0"])

        assert result.exit_code == 0

    def test_search_json_format(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search with JSON output format.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = "Card list"

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["cards", "--format", "json"])

        assert result.exit_code == 0

    def test_search_text_format(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search with text output format.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.return_value = "Plain text results"

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["dragons", "--format", "text"])

        assert result.exit_code == 0
        assert "Plain text results" in result.output

    def test_search_missing_query(self, cli_runner: CliRunner) -> None:
        """Test search without query argument.

        Args:
            cli_runner: Click CLI test runner

        """
        result = cli_runner.invoke(search, [])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_search_exception_handling(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test search command error handling.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.answer_natural_language_query.side_effect = Exception(
            "Search failed"
        )

        with patch(
            "mtg_card_app.ui.cli.commands.search.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(search, ["test"])

        assert "Error:" in result.output or "error" in result.output.lower()
