"""Protocol-based tests for QueryOrchestrator (multi-manager workflow)"""

import pytest

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.orchestrator import QueryOrchestrator
from mtg_card_app.managers.llm.manager import LLMManager
from mtg_card_app.managers.llm.services.ollama_service import OllamaLLMService


@pytest.fixture
def orchestrator():
    registry = ManagerRegistry.get_instance()
    llm_manager = LLMManager(service=OllamaLLMService(model="llama3"))
    return QueryOrchestrator(registry=registry, llm_manager=llm_manager)


class TestOrchestrator:
    """Protocol-based tests for the QueryOrchestrator using dependency-injected managers."""

    def test_answer_query_basic(self, orchestrator) -> None:
        """Test basic query answering for green ramp cards."""
        user_query = "List two green ramp spells in Magic: The Gathering."
        response = orchestrator.answer_query(user_query)
        assert isinstance(response, str)
        assert len(response) > 0
        assert "green" in response.lower() or "ramp" in response.lower()

    def test_answer_query_formatting(self, orchestrator) -> None:
        """Test query formatting for tutor/draw cards."""
        user_query = "Explain the difference between tutors and card draw."
        response = orchestrator.answer_query(user_query)
        assert isinstance(response, str)
        assert "tutor" in response.lower() or "draw" in response.lower()
