"""Tests for the card command."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from mtg_card_app.ui.cli.commands.card import card

if TYPE_CHECKING:
    from click.testing import CliRunner


class TestCardCommand:
    """Test suite for the card command."""

    def test_card_default_format(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with default (rich) format.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt"])

        assert result.exit_code == 0
        assert "Lightning Bolt" in result.output
        assert "{R}" in result.output
        mock_interactor.fetch_card.assert_called_once_with("Lightning Bolt")

    def test_card_text_format(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with text format.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt", "--format", "text"])

        assert result.exit_code == 0
        assert "Lightning Bolt" in result.output
        # Text format should have no ANSI codes
        assert "\x1b[" not in result.output

    def test_card_json_format(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with JSON format.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt", "--format", "json"])

        assert result.exit_code == 0
        # JSON output should be parseable
        assert "{" in result.output
        assert '"name"' in result.output or "'name'" in result.output

    def test_card_not_found(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with non-existent card.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.fetch_card.return_value = None

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Nonexistent Card"])

        # Should handle gracefully - either error or message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_card_missing_argument(self, cli_runner: CliRunner) -> None:
        """Test card command without card name argument.

        Args:
            cli_runner: Click CLI test runner

        """
        result = cli_runner.invoke(card, [])

        assert result.exit_code != 0
        # Click should show usage/error
        assert "Usage:" in result.output or "Error:" in result.output

    def test_card_interactor_called_correctly(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test that Interactor is called with correct arguments.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        card_name = "Sol Ring"

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, [card_name])

        assert result.exit_code == 0
        mock_interactor.fetch_card.assert_called_once_with(card_name)

    def test_card_multi_word_name(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with multi-word card name.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        # Create a mock card object
        mock_card = Mock()
        mock_card.name = "Thassa's Oracle"
        mock_card.mana_cost = "{U}{U}"
        mock_card.type_line = "Legendary Creature — Merfolk Wizard"
        mock_card.oracle_text = "When Thassa's Oracle enters the battlefield..."
        mock_card.power = "1"
        mock_card.toughness = "3"
        mock_card.price_usd = "15.00"
        
        mock_interactor.fetch_card.return_value = mock_card

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Thassa's Oracle"])

        assert result.exit_code == 0
        assert "Thassa's Oracle" in result.output
        mock_interactor.fetch_card.assert_called_once_with("Thassa's Oracle")

    def test_card_special_characters(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with special characters in name.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        card_name = "Jötun Grunt"
        
        # Create a mock card object
        mock_card = Mock()
        mock_card.name = card_name
        mock_card.mana_cost = "{1}{W}"
        mock_card.type_line = "Creature — Giant Soldier"
        mock_card.oracle_text = "Cumulative upkeep—Put two cards from a single graveyard on the bottom of their owner's library."
        mock_card.power = "4"
        mock_card.toughness = "4"
        mock_card.price_usd = "0.50"
        
        mock_interactor.fetch_card.return_value = mock_card

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, [card_name])

        assert result.exit_code == 0
        mock_interactor.fetch_card.assert_called_once_with(card_name)


class TestCardCommandOutputFormats:
    """Test suite for card command output formats."""

    @pytest.fixture
    def rich_card_data(self) -> dict:
        """Sample rich card data with all fields.

        Returns:
            Complete card data dictionary

        """
        return {
            "name": "Lightning Bolt",
            "mana_cost": "{R}",
            "cmc": 1.0,
            "type_line": "Instant",
            "oracle_text": "Lightning Bolt deals 3 damage to any target.",
            "colors": ["R"],
            "color_identity": ["R"],
            "power": None,
            "toughness": None,
            "keywords": [],
            "legalities": {
                "standard": "not_legal",
                "modern": "legal",
                "legacy": "legal",
                "vintage": "legal",
                "commander": "legal",
            },
            "set_name": "Alpha",
            "set_code": "lea",
            "rarity": "common",
            "artist": "Christopher Rush",
            "price_usd": "2.50",
            "price_usd_foil": "15.00",
            "edhrec_rank": 42,
        }

    def test_rich_format_shows_all_fields(
        self, cli_runner: CliRunner, mock_interactor: Mock, rich_card_data: dict
    ) -> None:
        """Test that rich format displays all card fields.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance
            rich_card_data: Complete card data

        """
        # Create a mock card object from the data
        mock_card = Mock()
        for key, value in rich_card_data.items():
            setattr(mock_card, key, value)
        
        mock_interactor.fetch_card.return_value = mock_card

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt"])

        assert result.exit_code == 0
        output = result.output

        # Check key fields are present
        assert "Lightning Bolt" in output
        assert "{R}" in output
        assert "Instant" in output
        assert "3 damage" in output
        assert "common" in output.lower()
        assert "Alpha" in output or "lea" in output

    def test_text_format_machine_readable(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test that text format is machine-readable (no ANSI).

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt", "--format", "text"])

        assert result.exit_code == 0
        # No ANSI escape codes
        assert "\x1b[" not in result.output
        # Still has content
        assert len(result.output) > 0
        assert "Lightning Bolt" in result.output

    def test_json_format_parseable(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test that JSON format is valid and parseable.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        import json

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt", "--format", "json"])

        assert result.exit_code == 0

        # Should be valid JSON
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
            assert "name" in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestCardCommandEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_empty_card_name(self, cli_runner: CliRunner) -> None:
        """Test card command with empty string as name.

        Args:
            cli_runner: Click CLI test runner

        """
        result = cli_runner.invoke(card, [""])

        # Should handle gracefully
        assert "Error:" in result.output or "not found" in result.output.lower()

    def test_very_long_card_name(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command with extremely long card name.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        long_name = "A" * 500
        mock_interactor.fetch_card.return_value = None

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, [long_name])

        # Should handle without crashing
        assert result.exit_code in [0, 1, 2]  # Success or handled error

    def test_invalid_format_option(self, cli_runner: CliRunner) -> None:
        """Test card command with invalid format option.

        Args:
            cli_runner: Click CLI test runner

        """
        result = cli_runner.invoke(
            card, ["Lightning Bolt", "--format", "invalid"]
        )

        # Click should reject invalid choice
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "choice" in result.output.lower()

    def test_interactor_exception(
        self, cli_runner: CliRunner, mock_interactor: Mock
    ) -> None:
        """Test card command when Interactor raises exception.

        Args:
            cli_runner: Click CLI test runner
            mock_interactor: Mock Interactor instance

        """
        mock_interactor.fetch_card.side_effect = Exception("Database error")

        with patch(
            "mtg_card_app.ui.cli.commands.card.Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke(card, ["Lightning Bolt"])

        # Should handle exception gracefully
        assert "error" in result.output.lower()
