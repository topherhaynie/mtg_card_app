"""Shared pytest fixtures for all tests."""

from __future__ import annotations

import pytest

from mtg_card_app.domain.entities import Card
from tests.mocks import MockLLMService


@pytest.fixture
def sample_card_data() -> dict:
    """Provide sample card data from Scryfall API format.

    Returns:
        Dictionary representing a card in Scryfall API format

    """
    return {
        "id": "fd0c3051-a334-427b-9294-e42c43c93fab",
        "name": "Sol Ring",
        "mana_cost": "{1}",
        "cmc": 1.0,
        "type_line": "Artifact",
        "oracle_text": "{T}: Add {C}{C}.",
        "colors": [],
        "color_identity": [],
        "keywords": [],
        "legalities": {
            "standard": "not_legal",
            "modern": "not_legal",
            "legacy": "legal",
            "vintage": "restricted",
            "commander": "legal",
        },
        "set": "cmr",
        "set_name": "Commander Legends",
        "rarity": "uncommon",
        "artist": "Mike Bierek",
        "prices": {"usd": "1.50", "eur": "1.20"},
    }


@pytest.fixture
def sample_card() -> Card:
    """Provide a sample Card entity.

    Returns:
        Card entity instance

    """
    return Card(
        id="fd0c3051-a334-427b-9294-e42c43c93fab",
        name="Sol Ring",
        mana_cost="{1}",
        cmc=1.0,
        type_line="Artifact",
        oracle_text="{T}: Add {C}{C}.",
        colors=[],
        color_identity=[],
        keywords=[],
        legalities={
            "standard": "not_legal",
            "modern": "not_legal",
            "legacy": "legal",
            "vintage": "restricted",
            "commander": "legal",
        },
        set_code="cmr",
        set_name="Commander Legends",
        rarity="uncommon",
        artist="Mike Bierek",
        prices={"usd": "1.50", "eur": "1.20"},
    )


@pytest.fixture
def mock_llm() -> MockLLMService:
    """Provide a mock LLM service for unit tests.

    Returns:
        MockLLMService instance with default behavior

    """
    return MockLLMService()


@pytest.fixture
def mock_llm_with_responses():
    """Provide a factory for creating mock LLMs with custom responses.

    Returns:
        Function that creates MockLLMService with custom responses

    """

    def _mock_llm(responses: dict[str, str]) -> MockLLMService:
        return MockLLMService(responses=responses)

    return _mock_llm
