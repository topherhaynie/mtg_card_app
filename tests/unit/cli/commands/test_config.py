"""Tests for the config CLI command."""

from unittest.mock import Mock, patch

from mtg_card_app.ui.cli.commands.config import config


class TestConfigShowCommand:
    """Test suite for the config show subcommand."""

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_show_displays_configuration(self, mock_get_config, cli_runner):
        """Test that config show displays all configuration settings."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.get.side_effect = lambda key, default=None: {
            "llm.provider": "openai",
            "cache.enabled": True,
            "cache.maxsize": 1000,
            "data.directory": "/path/to/data",
        }.get(key, default)
        mock_cfg.get_provider_config.return_value = {"model": "gpt-4"}
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["show"])

        # Verify
        assert result.exit_code == 0
        assert "Configuration" in result.output
        assert "LLM Provider" in result.output
        assert "openai" in result.output
        assert "gpt-4" in result.output
        assert "Cache Enabled" in result.output
        assert "True" in result.output
        assert "config.yaml" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_show_with_defaults(self, mock_get_config, cli_runner):
        """Test config show with default/missing values."""
        # Setup mock config with None values
        mock_cfg = Mock()
        mock_cfg.get.side_effect = lambda key, default=None: {
            "llm.provider": None,
            "cache.enabled": True,
            "cache.maxsize": 100,
            "data.directory": None,
        }.get(key, default)
        mock_cfg.get_provider_config.return_value = {}
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["show"])

        # Verify defaults are shown
        assert result.exit_code == 0
        assert "ollama" in result.output  # Default provider
        assert "data" in result.output  # Default data directory


class TestConfigSetCommand:
    """Test suite for the config set subcommand."""

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_set_string_value(self, mock_get_config, cli_runner):
        """Test setting a string configuration value."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["set", "llm.provider", "openai"])

        # Verify
        assert result.exit_code == 0
        mock_cfg.set.assert_called_once_with("llm.provider", "openai")
        assert "Set llm.provider = openai" in result.output
        assert "config.yaml" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_set_boolean_true(self, mock_get_config, cli_runner):
        """Test setting a boolean configuration value to true."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command with "true"
        result = cli_runner.invoke(config, ["set", "cache.enabled", "true"])

        # Verify boolean conversion
        assert result.exit_code == 0
        mock_cfg.set.assert_called_once_with("cache.enabled", True)
        assert "Set cache.enabled = True" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_set_boolean_false(self, mock_get_config, cli_runner):
        """Test setting a boolean configuration value to false."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command with "false"
        result = cli_runner.invoke(config, ["set", "cache.enabled", "false"])

        # Verify boolean conversion
        assert result.exit_code == 0
        mock_cfg.set.assert_called_once_with("cache.enabled", False)
        assert "Set cache.enabled = False" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_set_integer_value(self, mock_get_config, cli_runner):
        """Test setting an integer configuration value."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["set", "cache.maxsize", "2000"])

        # Verify integer conversion
        assert result.exit_code == 0
        mock_cfg.set.assert_called_once_with("cache.maxsize", 2000)
        assert "Set cache.maxsize = 2000" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_set_float_value(self, mock_get_config, cli_runner):
        """Test setting a float configuration value."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["set", "llm.temperature", "0.7"])

        # Verify float conversion
        assert result.exit_code == 0
        mock_cfg.set.assert_called_once_with("llm.temperature", 0.7)
        assert "Set llm.temperature = 0.7" in result.output


class TestConfigGetCommand:
    """Test suite for the config get subcommand."""

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_get_existing_key(self, mock_get_config, cli_runner):
        """Test getting an existing configuration value."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.get.return_value = "openai"
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["get", "llm.provider"])

        # Verify
        assert result.exit_code == 0
        mock_cfg.get.assert_called_once_with("llm.provider")
        assert "llm.provider = openai" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_get_nonexistent_key(self, mock_get_config, cli_runner):
        """Test getting a non-existent configuration key."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.get.return_value = None
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["get", "nonexistent.key"])

        # Verify
        assert result.exit_code == 0
        assert "Key 'nonexistent.key' not found" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_get_boolean_value(self, mock_get_config, cli_runner):
        """Test getting a boolean configuration value."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.get.return_value = True
        mock_get_config.return_value = mock_cfg

        # Run command
        result = cli_runner.invoke(config, ["get", "cache.enabled"])

        # Verify
        assert result.exit_code == 0
        assert "cache.enabled = True" in result.output


class TestConfigResetCommand:
    """Test suite for the config reset subcommand."""

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_reset_with_confirmation(self, mock_get_config, cli_runner):
        """Test resetting configuration with user confirmation."""
        # Setup mock config
        mock_cfg = Mock()
        mock_cfg.config_path = "/home/user/.config/mtg_card_app/config.yaml"
        mock_get_config.return_value = mock_cfg

        # Run command with confirmation
        result = cli_runner.invoke(config, ["reset"], input="y\n")

        # Verify
        assert result.exit_code == 0
        mock_cfg.reset_to_defaults.assert_called_once()
        assert "Configuration reset to defaults" in result.output
        assert "config.yaml" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_reset_abort(self, mock_get_config, cli_runner):
        """Test aborting configuration reset."""
        # Setup mock config
        mock_cfg = Mock()
        mock_get_config.return_value = mock_cfg

        # Run command with abort
        result = cli_runner.invoke(config, ["reset"], input="n\n")

        # Verify command was aborted
        assert result.exit_code != 0  # Click abort raises exception
        mock_cfg.reset_to_defaults.assert_not_called()


class TestConfigProvidersCommand:
    """Test suite for the config providers subcommand."""

    @patch("mtg_card_app.ui.cli.commands.config.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_providers_lists_all(
        self,
        mock_get_config,
        mock_factory_class,
        cli_runner,
    ):
        """Test listing all available LLM providers."""
        # Setup mocks
        mock_cfg = Mock()
        mock_cfg.get.return_value = "ollama"
        mock_get_config.return_value = mock_cfg

        mock_factory = Mock()
        mock_factory.get_available_providers.return_value = ["ollama", "openai"]
        mock_factory_class.return_value = mock_factory

        # Run command
        result = cli_runner.invoke(config, ["providers"])

        # Verify
        assert result.exit_code == 0
        assert "Available LLM Providers" in result.output
        assert "Ollama" in result.output
        assert "Openai" in result.output
        assert "Anthropic" in result.output
        assert "Gemini" in result.output
        assert "Groq" in result.output
        assert "Current provider: ollama" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_providers_shows_availability(
        self,
        mock_get_config,
        mock_factory_class,
        cli_runner,
    ):
        """Test that providers command shows availability status."""
        # Setup mocks
        mock_cfg = Mock()
        mock_cfg.get.return_value = "openai"
        mock_get_config.return_value = mock_cfg

        mock_factory = Mock()
        mock_factory.get_available_providers.return_value = ["ollama", "openai", "anthropic"]
        mock_factory_class.return_value = mock_factory

        # Run command
        result = cli_runner.invoke(config, ["providers"])

        # Verify availability markers
        assert result.exit_code == 0
        assert "✓ Available" in result.output
        assert "✗ Not Installed" in result.output
        assert "pip install mtg-card-app" in result.output
        assert "Current provider: openai" in result.output

    @patch("mtg_card_app.ui.cli.commands.config.ProviderFactory")
    @patch("mtg_card_app.ui.cli.commands.config.get_config")
    def test_config_providers_with_no_optional_installed(
        self,
        mock_get_config,
        mock_factory_class,
        cli_runner,
    ):
        """Test providers command when only ollama is available."""
        # Setup mocks
        mock_cfg = Mock()
        mock_cfg.get.return_value = "ollama"
        mock_get_config.return_value = mock_cfg

        mock_factory = Mock()
        mock_factory.get_available_providers.return_value = ["ollama"]
        mock_factory_class.return_value = mock_factory

        # Run command
        result = cli_runner.invoke(config, ["providers"])

        # Verify
        assert result.exit_code == 0
        assert "Available LLM Providers" in result.output
        # Should show install commands for missing providers
        # Note: The actual command shows "pip install mtg-card-app" without [provider] suffix
        assert "pip install mtg-card-app" in result.output
        assert "✗ Not Installed" in result.output
