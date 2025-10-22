"""OllamaLLMService: Implements LLMService protocol using local Ollama API."""

from collections.abc import Generator
from typing import Any

import requests

from .base import LLMService


class OllamaLLMService(LLMService):
    def __init__(self, model: str = "llama3", api_url: str = "http://localhost:11434/api/generate"):
        self.model = model
        self.api_url = api_url

    def generate(self, prompt: str, max_tokens: int = 256, stream: bool = False, **kwargs) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        payload.update(kwargs)
        if stream:
            return self._stream_response(payload)
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    def _stream_response(self, payload: dict) -> Generator[str, None, None]:
        with requests.post(self.api_url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        chunk = line.decode("utf-8")
                        data = requests.utils.json.loads(chunk)
                        yield data.get("response", "")
                    except Exception:
                        continue

    def get_model_name(self) -> str:
        return self.model

    def get_service_name(self) -> str:
        return "Ollama"

    def get_stats(self) -> dict[str, Any]:
        return {
            "provider": "Ollama",
            "model": self.model,
            "api_url": self.api_url,
        }
