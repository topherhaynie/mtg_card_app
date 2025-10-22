"""Anthropic Claude LLM Service implementation.

This module provides an LLMService implementation using Anthropic's Claude API.

Requires: pip install mtg-card-app[anthropic]
"""

from collections.abc import Generator
from typing import Any

try:
    from anthropic import Anthropic
except ImportError as e:
    msg = (
        "Anthropic provider requires the 'anthropic' package. "
        "Install it with: pip install mtg-card-app[anthropic] "
        "or: pip install anthropic"
    )
    raise ImportError(msg) from e

from .base import LLMService


class AnthropicLLMService(LLMService):
    """Anthropic Claude implementation of LLMService protocol.

    This service uses Anthropic's Claude API to generate responses. Requires an API key.

    Attributes:
        model: The Claude model to use (e.g., "claude-3-5-sonnet-20241022")
        api_key: Anthropic API key
        client: Anthropic client instance

    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Anthropic LLM service.

        Args:
            model: Model identifier (default: "claude-3-5-sonnet-20241022")
            api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY env var)
            **kwargs: Additional arguments passed to Anthropic client

        """
        self.model = model
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key, **kwargs)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stream: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,
    ) -> str | Generator[str, None, None]:
        """Generate response from Claude.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            Complete response string or generator of chunks

        """
        if stream:
            return self._stream_response(prompt, max_tokens, **kwargs)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )

        # Extract text from content blocks
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        return "".join(text_blocks)

    def _stream_response(
        self,
        prompt: str,
        max_tokens: int,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """Stream response from Claude.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Response chunks

        """
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def get_model_name(self) -> str:
        """Return the model identifier."""
        return self.model

    def get_service_name(self) -> str:
        """Return the service provider name."""
        return "Anthropic"

    def get_stats(self) -> dict[str, Any]:
        """Return service statistics."""
        return {
            "provider": "Anthropic",
            "model": self.model,
            "api_key_set": self.api_key is not None,
        }
