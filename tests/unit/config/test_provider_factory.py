"""Unit tests for ProviderFactory.

These are true unit tests:
- All LLM service imports are mocked
- No external dependencies (LLM SDKs)
- Fast execution
- Test factory logic in isolation
"""

from unittest.mock import MagicMock, patch

import pytest

from mtg_card_app.config.manager import Config
from mtg_card_app.config.provider_factory import ProviderFactory

pytestmark = [pytest.mark.config, pytest.mark.config_provider]  # Mark all tests in this module


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock config instance for testing."""
    return Config(tmp_path / "test_config.toml")


@pytest.fixture
def factory(mock_config):
    """Create a ProviderFactory instance for testing."""
    return ProviderFactory(mock_config)


class TestProviderFactoryInit:
    """Test ProviderFactory initialization."""

    def test_factory_stores_config(self, mock_config):
        """Test that factory stores the config instance."""
        factory = ProviderFactory(mock_config)
        assert factory.config is mock_config


class TestGetAvailableProviders:
    """Test get_available_providers() method."""

    def test_get_available_providers_always_includes_ollama(self, factory):
        """Test that Ollama is always available."""
        providers = factory.get_available_providers()
        assert "ollama" in providers

    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_get_available_providers_checks_all_providers(self, mock_is_available, factory):
        """Test that all providers are checked for availability."""
        mock_is_available.return_value = True

        providers = factory.get_available_providers()

        # Should check all known providers
        assert "ollama" in providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers
        assert "groq" in providers

    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_get_available_providers_excludes_unavailable(self, mock_is_available, factory):
        """Test that unavailable providers are excluded."""

        def is_available(provider):
            return provider == "ollama"

        mock_is_available.side_effect = is_available

        providers = factory.get_available_providers()

        assert "ollama" in providers
        assert "openai" not in providers
        assert "anthropic" not in providers


class TestIsProviderAvailable:
    """Test is_provider_available() method."""

    def test_ollama_is_always_available(self, factory):
        """Test that Ollama is always available."""
        assert factory.is_provider_available("ollama") is True

    @patch("importlib.import_module")
    def test_openai_available_when_module_imports(self, mock_import, factory):
        """Test that OpenAI is available when module imports successfully."""
        mock_import.return_value = MagicMock()

        assert factory.is_provider_available("openai") is True
        mock_import.assert_called_once_with("openai")

    @patch("importlib.import_module")
    def test_openai_unavailable_when_import_fails(self, mock_import, factory):
        """Test that OpenAI is unavailable when import fails."""
        mock_import.side_effect = ImportError("No module named 'openai'")

        assert factory.is_provider_available("openai") is False

    @patch("importlib.import_module")
    def test_anthropic_available_when_module_imports(self, mock_import, factory):
        """Test that Anthropic is available when module imports successfully."""
        mock_import.return_value = MagicMock()

        assert factory.is_provider_available("anthropic") is True
        mock_import.assert_called_once_with("anthropic")

    @patch("importlib.import_module")
    def test_gemini_available_when_module_imports(self, mock_import, factory):
        """Test that Gemini is available when module imports successfully."""
        mock_import.return_value = MagicMock()

        assert factory.is_provider_available("gemini") is True
        mock_import.assert_called_once_with("google.generativeai")

    @patch("importlib.import_module")
    def test_groq_available_when_module_imports(self, mock_import, factory):
        """Test that Groq is available when module imports successfully."""
        mock_import.return_value = MagicMock()

        assert factory.is_provider_available("groq") is True
        mock_import.assert_called_once_with("groq")

    def test_unknown_provider_is_unavailable(self, factory):
        """Test that unknown providers are considered unavailable."""
        assert factory.is_provider_available("unknown_provider") is False


class TestCreateProvider:
    """Test create_provider() method."""

    @patch("mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService")
    def test_create_ollama_provider(self, mock_ollama_class, factory):
        """Test creating Ollama provider."""
        mock_service = MagicMock()
        mock_ollama_class.return_value = mock_service

        service = factory.create_provider("ollama")

        assert service is mock_service
        mock_ollama_class.assert_called_once()

    @patch("importlib.import_module")
    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_create_openai_provider(self, mock_is_available, mock_import, factory):
        """Test creating OpenAI provider."""
        mock_is_available.return_value = True

        # Mock the OpenAI module and service
        mock_openai_module = MagicMock()
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Return the service module when importing
        def import_side_effect(name):
            if name == "openai":
                return mock_openai_module
            if name == "mtg_card_app.managers.llm.services.openai_service":
                service_module = MagicMock()
                service_module.OpenAIService = mock_service_class
                return service_module
            return MagicMock()

        mock_import.side_effect = import_side_effect

        service = factory.create_provider("openai")

        assert service is mock_service

    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_create_provider_raises_for_unavailable(self, mock_is_available, factory):
        """Test that creating unavailable provider raises ImportError."""
        mock_is_available.return_value = False

        with pytest.raises(ImportError, match="openai"):
            factory.create_provider("openai")

    def test_create_provider_raises_for_unknown(self, factory):
        """Test that creating unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            factory.create_provider("unknown_provider")

    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_create_provider_uses_config(self, mock_is_available, mock_config, tmp_path):
        """Test that provider creation uses config settings."""
        # Set up config
        config = Config(tmp_path / "config.toml")
        config.set("llm.ollama.model", "custom-model")
        config.set("llm.ollama.base_url", "http://custom:11434")

        factory = ProviderFactory(config)

        with patch(
            "mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService",
        ) as mock_ollama:
            mock_service = MagicMock()
            mock_ollama.return_value = mock_service

            factory.create_provider("ollama")

            # Should be called with config settings
            call_kwargs = mock_ollama.call_args[1]
            assert call_kwargs["model_name"] == "custom-model"
            assert call_kwargs["base_url"] == "http://custom:11434"


class TestCreateProviderFromConfig:
    """Test create_provider() with None (uses config default)."""

    @patch("mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService")
    def test_create_provider_uses_default_provider(self, mock_ollama_class, factory):
        """Test that passing None uses the default provider from config."""
        mock_service = MagicMock()
        mock_ollama_class.return_value = mock_service

        # Default provider is ollama
        service = factory.create_provider(None)

        assert service is mock_service

    @patch("importlib.import_module")
    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_create_provider_respects_config_setting(
        self,
        mock_is_available,
        mock_import,
        mock_config,
        tmp_path,
    ):
        """Test that create_provider(None) respects the configured provider."""
        # Change default provider to openai
        config = Config(tmp_path / "config.toml")
        config.set("llm.provider", "openai")

        factory = ProviderFactory(config)
        mock_is_available.return_value = True

        # Mock the imports
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        def import_side_effect(name):
            if name == "openai":
                return MagicMock()
            if name == "mtg_card_app.managers.llm.services.openai_service":
                service_module = MagicMock()
                service_module.OpenAIService = mock_service_class
                return service_module
            return MagicMock()

        mock_import.side_effect = import_side_effect

        service = factory.create_provider(None)

        assert service is mock_service


class TestCreateSpecificProviders:
    """Test individual _create_* methods."""

    @patch("mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService")
    def test_create_ollama_uses_config_settings(self, mock_ollama_class, tmp_path):
        """Test that _create_ollama uses config settings."""
        config = Config(tmp_path / "config.toml")
        config.set("llm.ollama.model", "llama3:70b")
        config.set("llm.ollama.base_url", "http://localhost:11434")

        factory = ProviderFactory(config)
        mock_service = MagicMock()
        mock_ollama_class.return_value = mock_service

        factory._create_ollama()

        call_kwargs = mock_ollama_class.call_args[1]
        assert call_kwargs["model_name"] == "llama3:70b"
        assert call_kwargs["base_url"] == "http://localhost:11434"

    @patch("importlib.import_module")
    @patch("mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available")
    def test_create_openai_uses_config_settings(
        self,
        mock_is_available,
        mock_import,
        tmp_path,
    ):
        """Test that _create_openai uses config settings."""
        import os

        config = Config(tmp_path / "config.toml")
        config.set("llm.openai.model", "gpt-4")
        config.set("llm.openai.api_key", "${OPENAI_API_KEY}")

        factory = ProviderFactory(config)
        mock_is_available.return_value = True

        # Mock OpenAI SDK and service
        mock_openai_client = MagicMock()
        mock_service_class = MagicMock()
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        def import_side_effect(name):
            if name == "openai":
                openai_module = MagicMock()
                openai_module.OpenAI = MagicMock(return_value=mock_openai_client)
                return openai_module
            if name == "mtg_card_app.managers.llm.services.openai_service":
                service_module = MagicMock()
                service_module.OpenAIService = mock_service_class
                return service_module
            return MagicMock()

        mock_import.side_effect = import_side_effect

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            # Get the provider config that would be passed
            provider_config = config.get_provider_config("openai")
            factory._create_openai(provider_config)

        call_kwargs = mock_service_class.call_args[1]
        assert call_kwargs["model_name"] == "gpt-4"


class TestProviderConfigIntegration:
    """Integration-style tests with real Config (still fast, no external deps)."""

    def test_full_workflow_create_multiple_providers(self, tmp_path):
        """Test creating multiple providers with different configs."""
        config = Config(tmp_path / "config.toml")

        # Configure multiple providers
        config.set("llm.ollama.model", "custom-llama")
        config.set("llm.openai.model", "gpt-4-turbo")

        factory = ProviderFactory(config)

        # Test Ollama creation
        with patch(
            "mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService",
        ) as mock_ollama:
            mock_service = MagicMock()
            mock_ollama.return_value = mock_service

            ollama_service = factory.create_provider("ollama")

            assert ollama_service is mock_service
            call_kwargs = mock_ollama.call_args[1]
            assert call_kwargs["model_name"] == "custom-llama"

    def test_switch_providers_via_config(self, tmp_path):
        """Test switching between providers using config."""
        config = Config(tmp_path / "config.toml")
        factory = ProviderFactory(config)

        # Ensure we start with Ollama (reset if needed from previous tests)
        config.set("llm.provider", "ollama")
        assert config.get("llm.provider") == "ollama"

        with patch(
            "mtg_card_app.managers.llm.services.ollama_service.OllamaLLMService",
        ) as mock_ollama:
            mock_ollama.return_value = MagicMock()
            service1 = factory.create_provider_from_config()
            assert service1 is not None

        # Switch to OpenAI
        config.set("llm.provider", "openai")

        with (
            patch("importlib.import_module") as mock_import,
            patch(
                "mtg_card_app.config.provider_factory.ProviderFactory.is_provider_available",
            ) as mock_is_available,
        ):
            mock_is_available.return_value = True

            mock_service_class = MagicMock()
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            def import_side_effect(name):
                if name == "openai":
                    return MagicMock()
                if name == "mtg_card_app.managers.llm.services.openai_service":
                    service_module = MagicMock()
                    service_module.OpenAIService = mock_service_class
                    return service_module
                return MagicMock()

            mock_import.side_effect = import_side_effect

            service2 = factory.create_provider_from_config()
            assert service2 is mock_service
