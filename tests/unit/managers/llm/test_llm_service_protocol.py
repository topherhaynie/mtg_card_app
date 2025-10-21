"""Protocol-based tests for LLMService implementations (OllamaLLMService)"""

import pytest

from mtg_card_app.managers.llm.services.ollama_service import OllamaLLMService


@pytest.fixture(
    params=[
        pytest.param("ollama", id="OllamaLLMService"),
        # Future: pytest.param("openai", id="OpenAILLMService"),
    ]
)
def llm_service(request):
    if request.param == "ollama":
        return OllamaLLMService(model="llama3")
    # elif request.param == "openai":
    #     return OpenAILLMService(...)


class TestGenerate:
    def test_basic_prompt(self, llm_service):
        prompt = "List two red burn spells in Magic: The Gathering."
        response = llm_service.generate(prompt, max_tokens=64)
        assert isinstance(response, str)
        assert len(response) > 0
        assert "red" in response.lower() or "burn" in response.lower()

    def test_longer_prompt(self, llm_service):
        prompt = "Explain the difference between counterspells and removal spells in Magic: The Gathering."
        response = llm_service.generate(prompt, max_tokens=128)
        assert isinstance(response, str)
        assert "counter" in response.lower() or "removal" in response.lower()


class TestModelInfo:
    def test_get_model_name(self, llm_service):
        name = llm_service.get_model_name()
        assert isinstance(name, str)
        assert name == "llama3"

    def test_get_stats(self, llm_service):
        stats = llm_service.get_stats()
        assert isinstance(stats, dict)
        assert "model" in stats
        assert stats["model"] == "llama3"
        assert "api_url" in stats
