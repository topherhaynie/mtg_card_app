"""Tests for the CLI setup command."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from mtg_card_app.ui.cli.commands.setup import run_setup_wizard


class TestSetupCommand:
    """Test suite for the setup wizard command."""

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_wizard_basic_flow(
        self, mock_print, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test the basic setup wizard flow."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
            "llm.ollama.base_url": "http://localhost:11434/api/generate",
            "llm.ollama.model": "llama3",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory_class.return_value = mock_factory

        # User declines LLM configuration and testing
        mock_confirm.side_effect = [False, False]

        # Run setup
        run_setup_wizard()

        # Verify config was accessed
        mock_get_config.assert_called()
        mock_factory_class.assert_called_once_with(mock_config)

        # Verify something was printed (basic flow completed)
        assert mock_print.called

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.Prompt.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_configures_ollama(
        self, mock_print, mock_prompt, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test configuring Ollama provider."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
            "llm.ollama.base_url": "http://localhost:11434/api/generate",
            "llm.ollama.model": "llama3",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory_class.return_value = mock_factory

        # User wants to configure LLM (True), keep defaults (True, True),
        # skip testing (False)
        mock_confirm.side_effect = [True, True, True, False]
        mock_prompt.side_effect = ["ollama", "llama3"]

        # Run setup
        run_setup_wizard()

        # Verify provider was set
        assert any(
            call[0] == ("llm.provider", "ollama")
            for call in mock_config.set.call_args_list
        )

        # Verify model was set
        assert any(
            call[0] == ("llm.ollama.model", "llama3")
            for call in mock_config.set.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.Prompt.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_configures_openai_with_env_var(
        self, mock_print, mock_prompt, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test configuring OpenAI with environment variable."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
            "llm.openai.api_key": "",
            "llm.openai.model": "gpt-4o-mini",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory_class.return_value = mock_factory

        # User wants to configure (True), provider available (continues),
        # update API key (True), use env var (1), keep model default (enter),
        # skip testing (False)
        mock_confirm.side_effect = [True, False]
        mock_prompt.side_effect = [
            "openai",  # Choose provider
            "1",  # Use env var
            "OPENAI_API_KEY",  # Env var name
            "gpt-4o-mini",  # Model
        ]

        # Run setup
        run_setup_wizard()

        # Verify provider was set
        assert any(
            call[0] == ("llm.provider", "openai")
            for call in mock_config.set.call_args_list
        )

        # Verify API key with env var syntax
        assert any(
            call[0] == ("llm.openai.api_key", "${OPENAI_API_KEY}")
            for call in mock_config.set.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.Prompt.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_warns_unavailable_provider(
        self, mock_print, mock_prompt, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test warning when choosing unavailable provider."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = False
        mock_factory_class.return_value = mock_factory

        # User wants to configure (True), chooses openai (unavailable),
        # declines to continue (False), skip testing (False)
        mock_confirm.side_effect = [True, False, False]
        mock_prompt.side_effect = ["openai"]

        # Run setup
        run_setup_wizard()

        # Verify warning was shown
        assert any(
            "not installed" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.Path")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_checks_data_files(
        self, mock_print, mock_path_class, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test that setup checks for data files."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory_class.return_value = mock_factory

        # Mock data directory and files
        mock_data_dir = MagicMock()
        mock_path_class.return_value = mock_data_dir

        # Simulate cards.db exists, chroma/ missing
        def exists_side_effect():
            # This is called for each file check
            return False

        mock_file = MagicMock()
        mock_file.exists.side_effect = [True, False]  # cards.db exists, chroma/ missing
        mock_data_dir.__truediv__.return_value = mock_file

        # User declines configuration (False) and testing (False)
        mock_confirm.side_effect = [False, False]

        # Run setup
        run_setup_wizard()

        # Verify data files were checked
        assert any(
            "data files" in str(call).lower() or "cards.db" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_tests_connection(
        self, mock_print, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test that setup can test LLM connection."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True

        # Mock successful service creation
        mock_service = MagicMock()
        mock_service.get_model_name.return_value = "llama3"
        mock_factory.create_provider.return_value = mock_service

        mock_factory_class.return_value = mock_factory

        # User declines configuration (False), wants to test (True),
        # declines sample query (False)
        mock_confirm.side_effect = [False, True, False]

        # Run setup
        run_setup_wizard()

        # Verify connection was tested
        mock_factory.create_provider.assert_called_once_with("ollama")
        mock_service.get_model_name.assert_called_once()

        # Verify success message
        assert any(
            "connected" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_tests_generation(
        self, mock_print, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test that setup can test LLM generation."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True

        # Mock successful service creation and generation
        mock_service = MagicMock()
        mock_service.get_model_name.return_value = "llama3"
        mock_service.generate.return_value = "A mana curve is the distribution of cards by mana cost."
        mock_factory.create_provider.return_value = mock_service

        mock_factory_class.return_value = mock_factory

        # User declines configuration (False), wants to test (True),
        # wants sample query (True)
        mock_confirm.side_effect = [False, True, True]

        # Run setup
        run_setup_wizard()

        # Verify generation was tested
        mock_service.generate.assert_called_once()
        assert "mana curve" in mock_service.generate.call_args[0][0].lower()

        # Verify success message
        assert any(
            "generation" in str(call).lower() or "successful" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_handles_connection_failure(
        self, mock_print, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test handling of connection test failure."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory.create_provider.side_effect = Exception("Connection refused")

        mock_factory_class.return_value = mock_factory

        # User declines configuration (False), wants to test (True)
        mock_confirm.side_effect = [False, True]

        # Run setup
        run_setup_wizard()

        # Verify error was shown
        assert any(
            "failed" in str(call).lower() or "connection refused" in str(call).lower()
            for call in mock_print.call_args_list
        )

        # Verify troubleshooting tips were shown
        assert any(
            "troubleshooting" in str(call).lower()
            for call in mock_print.call_args_list
        )

    @patch("mtg_card_app.ui.cli.commands.setup.get_config")
    @patch("mtg_card_app.ui.cli.commands.setup.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.setup.Confirm.ask")
    @patch("mtg_card_app.ui.cli.commands.setup.console.print")
    def test_setup_shows_completion_message(
        self, mock_print, mock_confirm, mock_factory_class, mock_get_config
    ):
        """Test that setup shows completion message."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "data.directory": "data",
        }.get(key, default)
        mock_config.config_path = Path("/tmp/config.yaml")
        mock_get_config.return_value = mock_config

        mock_factory = MagicMock()
        mock_factory.is_provider_available.return_value = True
        mock_factory_class.return_value = mock_factory

        # User declines everything
        mock_confirm.side_effect = [False, False]

        # Run setup
        run_setup_wizard()

        # Verify wizard completed and printed output
        assert mock_print.called
        # Verify multiple outputs (welcome, status, data files, completion)
        assert mock_print.call_count >= 4
