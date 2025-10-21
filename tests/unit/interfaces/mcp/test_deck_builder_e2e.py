"""E2E tests for MCP deck builder tools."""

import pytest

from mtg_card_app.core.manager_registry import ManagerRegistry


@pytest.fixture(scope="module")
def interactor():
    registry = ManagerRegistry.get_instance()
    return registry.interactor


def test_build_deck_basic(interactor):
    deck_format = "Commander"
    card_pool = [f"Card{i}" for i in range(1, 101)]
    commander = "Card1"
    constraints = {"budget": 200}
    metadata = {"theme": "aristocrats"}
    deck = interactor.build_deck(deck_format, card_pool, commander, constraints, metadata)
    assert deck.format == deck_format
    assert deck.commander == commander
    assert len(deck.cards) == 100
    assert deck.metadata["theme"] == "aristocrats"


def test_validate_deck_basic(interactor):
    deck_format = "Commander"
    card_pool = [f"Card{i}" for i in range(1, 101)]
    commander = "Card1"
    deck = interactor.build_deck(deck_format, card_pool, commander)
    deck_obj = type(deck).from_dict(deck.to_dict())
    result = interactor.validate_deck(deck_obj)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_deck_missing_commander(interactor):
    deck_format = "Commander"
    card_pool = [f"Card{i}" for i in range(1, 101)]
    deck = interactor.build_deck(deck_format, card_pool)
    deck_obj = type(deck).from_dict(deck.to_dict())
    result = interactor.validate_deck(deck_obj)
    assert result["valid"] is False
    assert any("commander" in e for e in result["errors"])


def test_validate_deck_wrong_size(interactor):
    deck_format = "Commander"
    card_pool = [f"Card{i}" for i in range(1, 99)]
    commander = "Card1"
    deck = interactor.build_deck(deck_format, card_pool, commander)
    deck_obj = type(deck).from_dict(deck.to_dict())
    result = interactor.validate_deck(deck_obj)
    assert result["valid"] is False
    assert any("100 cards" in e for e in result["errors"])
