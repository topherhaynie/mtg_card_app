"""Tests for the update command."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch, MagicMock

from mtg_card_app.ui.cli.commands.update import update

if TYPE_CHECKING:
    from click.testing import CliRunner


class TestUpdateCommand:
    """Test suite for the update command."""

    def test_update_basic(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test basic update command.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards") as mock_cards, \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings") as mock_embeddings:
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, [])

        assert result.exit_code == 0
        assert "Data Update" in result.output or "Update" in result.output
        mock_cards.assert_called_once()
        mock_embeddings.assert_called_once()

    def test_update_force_flag(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update with force flag.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards") as mock_cards, \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings") as mock_embeddings:
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, ["--force"])

        assert result.exit_code == 0
        # Verify force flag was passed
        mock_cards.assert_called_once()
        call_args = mock_cards.call_args
        assert call_args[0][1] is True  # force=True

    def test_update_cards_only(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update with cards-only flag.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards") as mock_cards, \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings") as mock_embeddings:
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, ["--cards-only"])

        assert result.exit_code == 0
        mock_cards.assert_called_once()
        # Should not call embeddings when cards-only
        mock_embeddings.assert_not_called()

    def test_update_embeddings_only(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update with embeddings-only flag.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards") as mock_cards, \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings") as mock_embeddings:
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, ["--embeddings-only"])

        assert result.exit_code == 0
        # Should not call cards when embeddings-only
        mock_cards.assert_not_called()
        mock_embeddings.assert_called_once()

    def test_update_conflicting_flags(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update with conflicting flags (cards-only and embeddings-only).

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards") as mock_cards, \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings") as mock_embeddings:
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, ["--cards-only", "--embeddings-only"])

        # Should show error about conflicting flags
        assert "Error:" in result.output or "Cannot use" in result.output
        # Should not call either update function
        mock_cards.assert_not_called()
        mock_embeddings.assert_not_called()

    def test_update_success_message(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update shows success message.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards"), \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings"):
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, [])

        assert result.exit_code == 0
        assert "complete" in result.output.lower() or "success" in result.output.lower()

    def test_update_data_directory_creation(
        self, cli_runner: CliRunner, tmp_path,
    ) -> None:
        """Test update creates data directory if it doesn't exist.

        Args:
            cli_runner: Click CLI test runner
            tmp_path: Pytest temporary directory

        """
        data_dir = tmp_path / "test_data"
        
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards"), \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings"), \
             patch("mtg_card_app.ui.cli.commands.update.Path") as mock_path:
            
            mock_config.return_value.get.return_value = str(data_dir)
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            
            result = cli_runner.invoke(update, [])

        assert result.exit_code == 0
        # Verify mkdir was called to create directory
        mock_path_instance.mkdir.assert_called_once_with(exist_ok=True, parents=True)

    def test_update_shows_next_steps(
        self, cli_runner: CliRunner,
    ) -> None:
        """Test update shows helpful next steps.

        Args:
            cli_runner: Click CLI test runner

        """
        with patch("mtg_card_app.ui.cli.commands.update.get_config") as mock_config, \
             patch("mtg_card_app.ui.cli.commands.update._update_cards"), \
             patch("mtg_card_app.ui.cli.commands.update._update_embeddings"):
            
            mock_config.return_value.get.return_value = "data"
            
            result = cli_runner.invoke(update, [])

        assert result.exit_code == 0
        # Should show helpful next steps
        assert "stats" in result.output.lower() or "search" in result.output.lower()
