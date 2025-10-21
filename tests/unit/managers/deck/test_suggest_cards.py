"""Unit test for DeckBuilderManager.suggest_cards with real logic and mocks."""

import pytest

from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.managers.deck.manager import DeckBuilderManager


class DummyCard:
    def __init__(self, name, color_identity=None, colors=None, oracle_text=None, usd=None):
        self.name = name
        self.color_identity = color_identity or []
        self.colors = colors or []
        self.oracle_text = oracle_text or ""
        self.usd = usd


class DummyCardDataManager:
    def __init__(self, cards):
        self.cards = {c.name: c for c in cards}
        self.cards_by_id = {str(i): c for i, c in enumerate(cards)}

    def get_card(self, name):
        return self.cards.get(name)

    def get_card_by_id(self, cid, fetch_if_missing=False):
        return self.cards_by_id.get(cid)


class DummyRAGManager:
    def __init__(self, results):
        self._results = results

    def search_similar(self, query, n_results=5, context_cards=None, **kwargs):
        # Accept context_cards and ignore extra kwargs for compatibility
        return self._results[:n_results]


class DummyComboService:
    def search(self, query):
        # Return empty list for now (no combos in test data)
        return []


class DummyDBManager:
    def __init__(self):
        self.combo_service = DummyComboService()


class DummyInteractor:
    def __init__(self):
        self.db_manager = DummyDBManager()


@pytest.fixture
def patch_manager_registry(monkeypatch):
    # Patch ManagerRegistry.get_instance to return dummy managers
    from mtg_card_app.core import manager_registry

    dummy_cards = [
        DummyCard("Sol Ring", ["C"], ["C"], "Ramp artifact.", "1.5"),
        DummyCard("Rhystic Study", ["U"], ["U"], "Whenever an opponent casts a spell...", "30.0"),
        DummyCard("Counterspell", ["U"], ["U"], "Counter target spell.", "2.0"),
        DummyCard("Island", ["U"], ["U"], "Basic Land.", None),
    ]
    dummy_card_data = DummyCardDataManager(dummy_cards)
    dummy_rag = DummyRAGManager(
        [
            ("0", 0.99, {}),
            ("1", 0.88, {}),
            ("2", 0.77, {}),
            ("3", 0.66, {}),
        ],
    )
    dummy_interactor = DummyInteractor()

    class DummyRegistry:
        rag_manager = dummy_rag
        card_data_manager = dummy_card_data
        interactor = dummy_interactor

    monkeypatch.setattr(
        manager_registry,
        "ManagerRegistry",
        type("MR", (), {"get_instance": staticmethod(lambda: DummyRegistry)}),
    )


def test_suggest_cards_real_logic(patch_manager_registry):
    manager = DeckBuilderManager()
    deck = Deck(
        format="Commander",
        cards=["Island"],
        sections={},
        commander="Island",
        metadata={"theme": "control", "colors": ["U"]},
    )
    constraints = {"theme": "control", "budget": 10, "power": 7}
    suggestions = manager.suggest_cards(deck, constraints)
    assert isinstance(suggestions, list)
    assert suggestions, "Should return at least one suggestion"
    for s in suggestions:
        assert "name" in s
        assert "score" in s
        assert "synergy" in s
        assert "weaknesses" in s
        assert isinstance(s["weaknesses"], list)
        # Check budget constraint
        if s["name"] == "Rhystic Study":
            assert any("exceeds budget" in w for w in s["weaknesses"])
        if s["name"] == "Sol Ring":
            assert "May not fit theme" in s["weaknesses"]
