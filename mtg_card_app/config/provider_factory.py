"""LLM Provider factory for creating service instances from configuration.

This module provides a factory for instantiating LLM providers based on
configuration settings, handling missing optional dependencies gracefully.
"""

import logging
from typing import Any

from mtg_card_app.config import Config
from mtg_card_app.managers.llm.services import LLMService, OllamaLLMService

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating LLM provider instances from configuration.

    This factory reads the configuration and instantiates the appropriate
    LLM provider service with the configured settings.

    Example:
        >>> from mtg_card_app.config import get_config
        >>> config = get_config()
        >>> factory = ProviderFactory(config)
        >>> service = factory.create_provider()
        >>> print(service.get_service_name())
        Ollama

    """

    # Map provider names to service classes
    PROVIDER_MAP: dict[str, str] = {
        "ollama": "OllamaLLMService",
        "openai": "OpenAILLMService",
        "anthropic": "AnthropicLLMService",
        "gemini": "GeminiLLMService",
        "groq": "GroqLLMService",
    }

    def __init__(self, config: Config) -> None:
        """Initialize the provider factory.

        Args:
            config: Configuration instance

        """
        self.config = config

    def create_provider(self, provider: str | None = None) -> LLMService:
        """Create an LLM provider instance from configuration.

        Args:
            provider: Provider name (e.g., "ollama", "openai").
                     If None, uses the configured default provider.

        Returns:
            LLM service instance

        Raises:
            ValueError: If provider is not supported
            ImportError: If provider's optional dependency is not installed

        Example:
            >>> service = factory.create_provider("openai")
            >>> service.get_model_name()
            'gpt-4o-mini'

        """
        if provider is None:
            provider = self.config.get("llm.provider", "ollama")

        logger.debug("Creating LLM provider: %s", provider)

        # Get provider configuration
        provider_config = self.config.get_provider_config(provider)

        # Create provider instance
        if provider == "ollama":
            return self._create_ollama(provider_config)
        if provider == "openai":
            return self._create_openai(provider_config)
        if provider == "anthropic":
            return self._create_anthropic(provider_config)
        if provider == "gemini":
            return self._create_gemini(provider_config)
        if provider == "groq":
            return self._create_groq(provider_config)

        msg = f"Unsupported provider: {provider}"
        raise ValueError(msg)

    def _create_ollama(self, config: dict[str, Any]) -> LLMService:
        """Create Ollama service instance.

        Args:
            config: Provider-specific configuration

        Returns:
            OllamaLLMService instance

        """
        return OllamaLLMService(
            model=config.get("model", "llama3"),
            api_url=config.get("base_url", "http://localhost:11434/api/generate"),
        )

    def _create_openai(self, config: dict[str, Any]) -> LLMService:
        """Create OpenAI service instance.

        Args:
            config: Provider-specific configuration

        Returns:
            OpenAILLMService instance

        Raises:
            ImportError: If openai package not installed

        """
        try:
            from mtg_card_app.managers.llm.services import OpenAILLMService
        except ImportError as e:
            msg = "OpenAI provider requires the 'openai' package. Install it with: pip install mtg-card-app[openai]"
            raise ImportError(msg) from e

        return OpenAILLMService(
            model=config.get("model", "gpt-4o-mini"),
            api_key=config.get("api_key"),
        )

    def _create_anthropic(self, config: dict[str, Any]) -> LLMService:
        """Create Anthropic service instance.

        Args:
            config: Provider-specific configuration

        Returns:
            AnthropicLLMService instance

        Raises:
            ImportError: If anthropic package not installed

        """
        try:
            from mtg_card_app.managers.llm.services import AnthropicLLMService
        except ImportError as e:
            msg = (
                "Anthropic provider requires the 'anthropic' package. "
                "Install it with: pip install mtg-card-app[anthropic]"
            )
            raise ImportError(msg) from e

        return AnthropicLLMService(
            model=config.get("model", "claude-3-5-sonnet-20241022"),
            api_key=config.get("api_key"),
        )

    def _create_gemini(self, config: dict[str, Any]) -> LLMService:
        """Create Gemini service instance.

        Args:
            config: Provider-specific configuration

        Returns:
            GeminiLLMService instance

        Raises:
            ImportError: If google-generativeai package not installed

        """
        try:
            from mtg_card_app.managers.llm.services import GeminiLLMService
        except ImportError as e:
            msg = (
                "Gemini provider requires the 'google-generativeai' package. "
                "Install it with: pip install mtg-card-app[gemini]"
            )
            raise ImportError(msg) from e

        return GeminiLLMService(
            model=config.get("model", "gemini-1.5-flash"),
            api_key=config.get("api_key"),
        )

    def _create_groq(self, config: dict[str, Any]) -> LLMService:
        """Create Groq service instance.

        Args:
            config: Provider-specific configuration

        Returns:
            GroqLLMService instance

        Raises:
            ImportError: If groq package not installed

        """
        try:
            from mtg_card_app.managers.llm.services import GroqLLMService
        except ImportError as e:
            msg = "Groq provider requires the 'groq' package. Install it with: pip install mtg-card-app[groq]"
            raise ImportError(msg) from e

        return GroqLLMService(
            model=config.get("model", "llama-3.1-70b-versatile"),
            api_key=config.get("api_key"),
        )

    def get_available_providers(self) -> list[str]:
        """Get list of providers that are available (dependencies installed).

        Returns:
            List of provider names that can be instantiated

        Example:
            >>> factory.get_available_providers()
            ['ollama', 'openai']

        """
        available = ["ollama"]  # Always available

        # Check optional providers
        try:
            from mtg_card_app.managers.llm.services import OpenAILLMService  # noqa: F401

            available.append("openai")
        except ImportError:
            pass

        try:
            from mtg_card_app.managers.llm.services import AnthropicLLMService  # noqa: F401

            available.append("anthropic")
        except ImportError:
            pass

        try:
            from mtg_card_app.managers.llm.services import GeminiLLMService  # noqa: F401

            available.append("gemini")
        except ImportError:
            pass

        try:
            from mtg_card_app.managers.llm.services import GroqLLMService  # noqa: F401

            available.append("groq")
        except ImportError:
            pass

        return available

    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available (dependencies installed).

        Args:
            provider: Provider name to check

        Returns:
            True if provider can be instantiated

        Example:
            >>> factory.is_provider_available("openai")
            True

        """
        return provider in self.get_available_providers()
