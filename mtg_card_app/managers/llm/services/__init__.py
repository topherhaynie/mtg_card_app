"""LLM services package.

This package contains implementations of the LLMService protocol for various
LLM providers including Ollama, OpenAI, Anthropic, Gemini, and Groq.

Note: Provider services are imported lazily. Install the corresponding optional
dependency to use a specific provider:
    - OpenAI: pip install mtg-card-app[openai]
    - Anthropic: pip install mtg-card-app[anthropic]
    - Gemini: pip install mtg-card-app[gemini]
    - Groq: pip install mtg-card-app[groq]
    - All: pip install mtg-card-app[all-providers]
"""

from .base import LLMService
from .ollama_service import OllamaLLMService

# Always available
__all__ = [
    "LLMService",
    "OllamaLLMService",
]

# Optional providers - only import if dependencies are installed
try:
    from .openai_service import OpenAILLMService

    __all__ += ["OpenAILLMService"]
except ImportError:
    pass

try:
    from .anthropic_service import AnthropicLLMService

    __all__ += ["AnthropicLLMService"]
except ImportError:
    pass

try:
    from .gemini_service import GeminiLLMService

    __all__ += ["GeminiLLMService"]
except ImportError:
    pass

try:
    from .groq_service import GroqLLMService

    __all__ += ["GroqLLMService"]
except ImportError:
    pass
