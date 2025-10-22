"""Unit tests for Config manager.

These are true unit tests:
- No external dependencies (files are mocked or use temp directories)
- Fast execution
- Test individual methods in isolation
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from mtg_card_app.config.manager import Config

pytestmark = [pytest.mark.config, pytest.mark.config_manager]  # Mark all tests in this module


class TestConfigCreation:
    """Test configuration file creation and initialization."""

    def test_config_creates_default_file_if_not_exists(self, tmp_path):
        """Test that Config creates default config file if it doesn't exist."""
        config_path = tmp_path / ".mtg" / "config.toml"

        # Config file doesn't exist yet
        assert not config_path.exists()

        # Create config
        config = Config(config_path)

        # File should now exist with defaults
        assert config_path.exists()
        assert config.get("llm.provider") == "ollama"

    def test_config_loads_existing_file(self, tmp_path):
        """Test that Config loads existing configuration file."""
        config_path = tmp_path / "config.toml"

        # Write a custom config
        config_path.write_text("""
[llm]
provider = "openai"

[llm.openai]
model = "gpt-4o"
""")

        # Load config
        config = Config(config_path)

        # Should load custom values
        assert config.get("llm.provider") == "openai"
        assert config.get("llm.openai.model") == "gpt-4o"

    def test_config_creates_parent_directories(self, tmp_path):
        """Test that Config creates nested parent directories."""
        config_path = tmp_path / "nested" / "deep" / "config.toml"

        # Parent directories don't exist
        assert not config_path.parent.exists()

        # Create config
        Config(config_path)

        # Parent directories should be created
        assert config_path.parent.exists()
        assert config_path.exists()


class TestConfigGet:
    """Test config.get() method."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test config instance."""
        return Config(tmp_path / "test_config.toml")

    def test_get_nested_value_with_dotted_key(self, config):
        """Test getting nested values using dotted key notation."""
        value = config.get("llm.ollama.model")
        assert value == "llama3"

    def test_get_top_level_value(self, config):
        """Test getting top-level values."""
        value = config.get("llm.provider")
        assert value == "ollama"

    def test_get_nonexistent_key_returns_default(self, config):
        """Test that getting non-existent key returns default value."""
        value = config.get("nonexistent.key", "default_value")
        assert value == "default_value"

    def test_get_nonexistent_key_returns_none_by_default(self, config):
        """Test that getting non-existent key returns None if no default."""
        value = config.get("nonexistent.key")
        assert value is None

    def test_get_deeply_nested_value(self, config):
        """Test getting deeply nested values."""
        config.set("level1.level2.level3.value", "deep_value")
        value = config.get("level1.level2.level3.value")
        assert value == "deep_value"


class TestConfigSet:
    """Test config.set() method."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test config instance."""
        return Config(tmp_path / "test_config.toml")

    def test_set_updates_existing_value(self, config):
        """Test that set() updates existing values."""
        config.set("llm.provider", "openai")
        assert config.get("llm.provider") == "openai"

    def test_set_creates_new_value(self, config):
        """Test that set() creates new values."""
        config.set("new.config.value", 42)
        assert config.get("new.config.value") == 42

    def test_set_creates_nested_structure(self, config):
        """Test that set() creates nested structure if it doesn't exist."""
        config.set("deeply.nested.new.value", "test")
        assert config.get("deeply.nested.new.value") == "test"

    def test_set_persists_to_file(self, tmp_path):
        """Test that set() persists changes to file."""
        config_path = tmp_path / "config.toml"
        config = Config(config_path)

        config.set("test.value", "persisted")

        # Create new config instance (reload from file)
        config2 = Config(config_path)
        assert config2.get("test.value") == "persisted"


class TestEnvironmentVariableResolution:
    """Test environment variable resolution in config values."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test config instance."""
        return Config(tmp_path / "test_config.toml")

    def test_resolve_environment_variable(self, config):
        """Test that ${VAR_NAME} syntax resolves to env var."""
        # Set an environment variable
        with patch.dict(os.environ, {"TEST_API_KEY": "secret_key_123"}):
            config.set("api.key", "${TEST_API_KEY}")
            value = config.get("api.key")
            assert value == "secret_key_123"

    def test_resolve_missing_environment_variable_returns_none(self, config):
        """Test that missing env var returns None."""
        with patch.dict(os.environ, {}, clear=True):
            config.set("api.key", "${MISSING_VAR}")
            value = config.get("api.key")
            assert value is None

    def test_resolve_env_var_in_nested_dict(self, config):
        """Test that env vars are resolved in nested dictionaries."""
        with patch.dict(os.environ, {"OPENAI_KEY": "sk-123"}):
            provider_config = config.get_provider_config("openai")
            # Default config has ${OPENAI_API_KEY}, but we set OPENAI_KEY for testing
            # So it should be None (var doesn't exist)
            assert provider_config.get("api_key") is None

    def test_non_env_var_string_not_resolved(self, config):
        """Test that normal strings are not treated as env vars."""
        config.set("normal.string", "not_an_env_var")
        value = config.get("normal.string")
        assert value == "not_an_env_var"


class TestGetProviderConfig:
    """Test get_provider_config() method."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test config instance."""
        return Config(tmp_path / "test_config.toml")

    def test_get_provider_config_returns_provider_settings(self, config):
        """Test getting provider-specific configuration."""
        ollama_config = config.get_provider_config("ollama")

        assert ollama_config["model"] == "llama3"
        assert "base_url" in ollama_config

    def test_get_provider_config_with_none_uses_default_provider(self, config):
        """Test that passing None uses the configured default provider."""
        # Default provider is ollama
        default_config = config.get_provider_config(None)
        assert default_config["model"] == "llama3"

        # Change default provider
        config.set("llm.provider", "openai")
        default_config = config.get_provider_config(None)
        assert default_config["model"] == "gpt-4o-mini"

    def test_get_provider_config_resolves_env_vars(self, config):
        """Test that provider config resolves environment variables."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-123"}):
            openai_config = config.get_provider_config("openai")
            assert openai_config["api_key"] == "sk-test-123"


class TestResetToDefaults:
    """Test reset_to_defaults() method."""

    def test_reset_to_defaults_restores_original_config(self, tmp_path):
        """Test that reset restores the original default configuration."""
        config_path = tmp_path / "config.toml"
        config = Config(config_path)

        # Modify config
        config.set("llm.provider", "openai")
        config.set("custom.value", "test")

        # Reset
        config.reset_to_defaults()

        # Should be back to defaults
        assert config.get("llm.provider") == "ollama"
        assert config.get("custom.value") is None

    def test_reset_to_defaults_persists_to_file(self, tmp_path):
        """Test that reset persists to file."""
        config_path = tmp_path / "config.toml"
        config = Config(config_path)

        # Modify and reset
        config.set("llm.provider", "openai")
        config.reset_to_defaults()

        # Reload from file
        config2 = Config(config_path)
        assert config2.get("llm.provider") == "ollama"


class TestGetAll:
    """Test get_all() method."""

    def test_get_all_returns_full_config(self, tmp_path):
        """Test that get_all returns complete configuration."""
        config = Config(tmp_path / "config.toml")

        all_config = config.get_all()

        assert "llm" in all_config
        assert "cache" in all_config
        assert "data" in all_config

    def test_get_all_returns_copy(self, tmp_path):
        """Test that get_all returns a copy, not the original."""
        config = Config(tmp_path / "config.toml")

        all_config = config.get_all()
        all_config["llm"]["provider"] = "modified"

        # Original should not be modified
        assert config.get("llm.provider") == "ollama"


class TestConfigRepr:
    """Test __repr__ method."""

    def test_repr_shows_config_path(self, tmp_path):
        """Test that repr shows the config file path."""
        config_path = tmp_path / "config.toml"
        config = Config(config_path)

        repr_str = repr(config)

        assert "Config" in repr_str
        assert str(config_path) in repr_str


class TestGetConfigSingleton:
    """Test the get_config() singleton function."""

    def test_get_config_returns_same_instance(self):
        """Test that get_config returns the same instance."""
        # Clear the global instance first
        import mtg_card_app.config.manager as manager_module
        from mtg_card_app.config import get_config

        manager_module._config = None

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_config_uses_default_path(self):
        """Test that get_config uses ~/.mtg/config.toml by default."""
        # Clear the global instance
        import mtg_card_app.config.manager as manager_module
        from mtg_card_app.config import get_config

        manager_module._config = None

        config = get_config()

        expected_path = Path.home() / ".mtg" / "config.toml"
        assert config.config_path == expected_path


class TestConfigWithRealFile:
    """Integration-style tests with real file operations (still fast)."""

    def test_full_workflow_create_modify_reload(self, tmp_path):
        """Test complete workflow: create, modify, save, reload."""
        config_path = tmp_path / "workflow_test.toml"

        # Create config
        config1 = Config(config_path)
        assert config1.get("llm.provider") == "ollama"

        # Modify
        config1.set("llm.provider", "openai")
        config1.set("custom.setting", "value")

        # Reload from disk
        config2 = Config(config_path)
        assert config2.get("llm.provider") == "openai"
        assert config2.get("custom.setting") == "value"

    def test_concurrent_config_instances_share_file(self, tmp_path):
        """Test that multiple Config instances share the same file."""
        config_path = tmp_path / "shared.toml"

        config1 = Config(config_path)
        config1.set("test.value", "from_config1")

        config2 = Config(config_path)
        # config2 reads the file at initialization
        assert config2.get("test.value") == "from_config1"
