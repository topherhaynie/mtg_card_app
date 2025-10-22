"""Groq LLM Service implementation.

This module provides an LLMService implementation using Groq's API.

Requires: pip install mtg-card-app[groq]
"""

from collections.abc import Generator
from typing import Any

try:
    from groq import Groq
except ImportError as e:
    msg = (
        "Groq provider requires the 'groq' package. "
        "Install it with: pip install mtg-card-app[groq] "
        "or: pip install groq"
    )
    raise ImportError(msg) from e

from .base import LLMService


class GroqLLMService(LLMService):
    """Groq implementation of LLMService protocol.

    This service uses Groq's API for ultra-fast inference.
    Has a generous free tier (30 requests/minute).

    Attributes:
        model: The Groq model to use (e.g., "llama-3.1-70b-versatile")
        api_key: Groq API key
        client: Groq client instance

    """

    def __init__(
        self,
        model: str = "llama-3.1-70b-versatile",
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Groq LLM service.

        Args:
            model: Model identifier (default: "llama-3.1-70b-versatile")
            api_key: Groq API key (if None, uses GROQ_API_KEY env var)
            **kwargs: Additional arguments passed to Groq client

        """
        self.model = model
        self.api_key = api_key
        self.client = Groq(api_key=api_key, **kwargs)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stream: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,
    ) -> str | Generator[str, None, None]:
        """Generate response from Groq.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional Groq-specific parameters

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
        """Stream response from Groq.

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
        return "Groq"

    def get_stats(self) -> dict[str, Any]:
        """Return service statistics."""
        return {
            "provider": "Groq",
            "model": self.model,
            "api_key_set": self.api_key is not None,
        }
