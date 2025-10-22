"""E2E tests for query functionality in Interactor.

NOTE: These are END-TO-END tests that hit:
- Real Ollama LLM service (~30 seconds per test)
- Real ChromaDB vector store
- Real SQLite database

Mark tests with @pytest.mark.e2e to skip them in fast test runs.
Run with: pytest -m "not e2e" to skip these tests.
"""

import pytest

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry


@pytest.fixture
def interactor():
    """Fixture providing Interactor with full manager registry."""
    registry = ManagerRegistry.get_instance()
    return Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
        db_manager=registry.db_manager,
        query_cache=registry.query_cache,
    )


class TestInteractor:
    """Protocol-based tests for the Interactor using dependency-injected managers."""

    @pytest.mark.e2e
    def test_answer_natural_language_query_basic(self, interactor) -> None:
        """Test basic query answering for green ramp cards."""
        user_query = "List two green ramp spells in Magic: The Gathering."
        response = interactor.answer_natural_language_query(user_query)
        assert isinstance(response, str)
        assert len(response) > 0
        assert "green" in response.lower() or "ramp" in response.lower()

    @pytest.mark.e2e
    def test_answer_natural_language_query_formatting(self, interactor) -> None:
        """Test query formatting for tutor/draw cards."""
        user_query = "Explain the difference between tutors and card draw."
        response = interactor.answer_natural_language_query(user_query)
        assert isinstance(response, str)
        assert "tutor" in response.lower() or "draw" in response.lower()
