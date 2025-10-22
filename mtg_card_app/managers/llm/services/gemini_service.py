"""Google Gemini LLM Service implementation.

This module provides an LLMService implementation using Google's Gemini API.

Requires: pip install mtg-card-app[gemini]
"""

from collections.abc import Generator
from typing import Any

try:
    import google.generativeai as genai
except ImportError as e:
    msg = (
        "Gemini provider requires the 'google-generativeai' package. "
        "Install it with: pip install mtg-card-app[gemini] "
        "or: pip install google-generativeai"
    )
    raise ImportError(msg) from e

from .base import LLMService


class GeminiLLMService(LLMService):
    """Google Gemini implementation of LLMService protocol.

    This service uses Google's Gemini API to generate responses.
    Has a generous free tier (15 requests/minute).

    Attributes:
        model: The Gemini model to use (e.g., "gemini-1.5-flash")
        api_key: Google API key
        model_instance: Configured Gemini model instance

    """

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Gemini LLM service.

        Args:
            model: Model identifier (default: "gemini-1.5-flash")
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var)
            **kwargs: Additional generation config parameters

        """
        self.model = model
        self.api_key = api_key

        # Configure API key
        if api_key:
            genai.configure(api_key=api_key)

        # Create model instance with generation config
        self.model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=kwargs.get("generation_config"),
        )

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        stream: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,
    ) -> str | Generator[str, None, None]:
        """Generate response from Gemini.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Complete response string or generator of chunks

        """
        generation_config = {"max_output_tokens": max_tokens, **kwargs}

        if stream:
            return self._stream_response(prompt, generation_config)

        response = self.model_instance.generate_content(
            prompt,
            generation_config=generation_config,
        )

        return response.text

    def _stream_response(
        self,
        prompt: str,
        generation_config: dict[str, Any],
    ) -> Generator[str, None, None]:
        """Stream response from Gemini.

        Args:
            prompt: Input prompt
            generation_config: Generation configuration

        Yields:
            Response chunks

        """
        response = self.model_instance.generate_content(
            prompt,
            generation_config=generation_config,
            stream=True,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    def get_model_name(self) -> str:
        """Return the model identifier."""
        return self.model

    def get_service_name(self) -> str:
        """Return the service provider name."""
        return "Gemini"

    def get_stats(self) -> dict[str, Any]:
        """Return service statistics."""
        return {
            "provider": "Gemini",
            "model": self.model,
            "api_key_set": self.api_key is not None,
        }
