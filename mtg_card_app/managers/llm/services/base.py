from typing import Any, Protocol


class LLMService(Protocol):
    """Protocol for Large Language Model (LLM) services."""

    def generate(self, prompt: str, max_tokens: int = 256, stream: bool = False, **kwargs) -> str:
        """Generate a response from the LLM given a prompt.
        If stream=True, returns a generator of response chunks.
        """
        ...

    def get_model_name(self) -> str:
        """Return the name of the underlying LLM model."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Return statistics or metadata about the LLM service."""
        ...
