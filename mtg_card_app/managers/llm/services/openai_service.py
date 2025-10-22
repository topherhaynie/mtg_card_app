"""OpenAI LLM Service implementation.

This module provides an LLMService implementation using OpenAI's API.

Requires: pip install mtg-card-app[openai]
"""

from collections.abc import Generator
from typing import Any

try:
    from openai import OpenAI
except ImportError as e:
    msg = (
        "OpenAI provider requires the 'openai' package. "
        "Install it with: pip install mtg-card-app[openai] "
        "or: pip install openai"
    )
    raise ImportError(msg) from e

from .base import LLMService


class OpenAILLMService(LLMService):
    """OpenAI implementation of LLMService protocol.

    This service uses OpenAI's API to generate responses. Requires an API key.

    Attributes:
        model: The OpenAI model to use (e.g., "gpt-4o-mini", "gpt-4o")
        api_key: OpenAI API key
        client: OpenAI client instance

    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI LLM service.

        Args:
            model: Model identifier (default: "gpt-4o-mini")
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            **kwargs: Additional arguments passed to OpenAI client

        """
        self.model = model
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, **kwargs)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stream: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,
    ) -> str | Generator[str, None, None]:
        """Generate response from OpenAI.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            Complete response string or generator of chunks

        """
        messages = [{"role": "user", "content": prompt}]

        if stream:
            return self._stream_response(messages, max_tokens, **kwargs)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            **kwargs,
        )

        return response.choices[0].message.content or ""

    def _stream_response(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """Stream response from OpenAI.

        Args:
            messages: Chat messages
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Response chunks

        """
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_model_name(self) -> str:
        """Return the model identifier."""
        return self.model

    def get_service_name(self) -> str:
        """Return the service provider name."""
        return "OpenAI"

    def get_stats(self) -> dict[str, Any]:
        """Return service statistics."""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "api_key_set": self.api_key is not None,
        }
