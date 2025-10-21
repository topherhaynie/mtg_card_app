from .services.base import LLMService


class LLMManager:
    """Manager for LLMService implementations.
    Handles service lifecycle and dependency injection.
    """

    def __init__(self, service: LLMService | None = None):
        self._service = service

    @property
    def service(self) -> LLMService:
        if self._service is None:
            raise ValueError("No LLMService implementation provided.")
        return self._service

    def generate(self, prompt: str, max_tokens: int = 256, stream: bool = False, **kwargs):
        return self.service.generate(prompt, max_tokens=max_tokens, stream=stream, **kwargs)

    def get_model_name(self) -> str:
        return self.service.get_model_name()

    def get_stats(self):
        return self.service.get_stats()
