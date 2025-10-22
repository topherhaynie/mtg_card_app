"""Base protocol for LLM service implementations.

This module defines the LLMService protocol that all LLM providers must implement.
"""

from collections.abc import Generator
from typing import Any, Protocol


class LLMService(Protocol):
    """Protocol for Large Language Model (LLM) services.

    This protocol defines the interface that all LLM providers must implement.
    It supports both streaming and non-streaming responses, and provides
    metadata about the service.
    """

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stream: bool = False,
        **kwargs: Any,
    ) -> str | Generator[str, None, None]:
        """Generate a response from the LLM given a prompt.

        Args:
            prompt: The input prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            stream: If True, returns a generator of response chunks
            **kwargs: Additional provider-specific parameters

        Returns:
            If stream=False: Complete response string
            If stream=True: Generator yielding response chunks

        Example:
            >>> service = OllamaLLMService()
            >>> response = service.generate("What is Magic: The Gathering?")
            >>> print(response)
            Magic: The Gathering is a collectible card game...

        """
        ...

    def get_model_name(self) -> str:
        """Return the name of the underlying LLM model.

        Returns:
            Model identifier (e.g., "llama3", "gpt-4o-mini")

        Example:
            >>> service.get_model_name()
            'llama3'

        """
        ...

    def get_service_name(self) -> str:
        """Return the name of the LLM service provider.

        Returns:
            Provider name (e.g., "Ollama", "OpenAI", "Anthropic")

        Example:
            >>> service.get_service_name()
            'Ollama'

        """
        ...

    def get_stats(self) -> dict[str, Any]:
        """Return statistics or metadata about the LLM service.

        Returns:
            Dictionary with service metadata including:
            - provider: Service provider name
            - model: Model identifier
            - Additional provider-specific stats

        Example:
            >>> service.get_stats()
            {'provider': 'Ollama', 'model': 'llama3', 'api_url': 'http://localhost:11434'}

        """
        ...
