"""JSON-RPC tests for MCP deck tools: analyze_deck and suggest_cards."""

import io
import json
import sys

import pytest

from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.stdio_service import StdioMCPService


class _DummyInteractor:
    def analyze_deck(self, deck: Deck) -> dict:
        # Ensure we received a Deck instance
        assert isinstance(deck, Deck)
        # Return minimal analysis structure
        return {"curve": {"0": 0, "1": 1}, "types": {"creature": 10}, "colors": ["U"], "issues": []}

    def suggest_cards(self, deck: Deck, constraints: dict | None = None):
        assert isinstance(deck, Deck)
        # Return minimal suggestions
        return [
            {"name": "Sol Ring", "score": 0.99, "reason": "Staple ramp"},
            {"name": "Rhystic Study", "score": 0.88, "reason": "Card draw"},
        ]


@pytest.fixture
def manager():
    service = StdioMCPService()
    interactor = _DummyInteractor()
    return MCPManager(service, interactor, validate_output=True)


def _run_jsonrpc(method: str, params: dict, monkeypatch, manager: MCPManager):
    req = {"jsonrpc": "2.0", "id": 42, "method": method, "params": params}
    stdin = io.StringIO(json.dumps(req) + "\n")
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    request = manager.service.read_request()
    resp = manager.dispatch(request)
    manager.service.send_response(resp)
    return json.loads(stdout.getvalue())


def test_analyze_deck_jsonrpc(monkeypatch, manager):
    deck = {
        "format": "Commander",
        "cards": [f"Card{i}" for i in range(1, 101)],
        "sections": {},
        "commander": "Card1",
        "metadata": {"theme": "control"},
    }
    result = _run_jsonrpc("analyze_deck", {"deck": deck}, monkeypatch, manager)
    assert result["jsonrpc"] == "2.0"
    assert result["id"] == 42
    assert isinstance(result["result"], dict)
    assert "curve" in result["result"]


def test_suggest_cards_jsonrpc(monkeypatch, manager):
    deck = {
        "format": "Commander",
        "cards": [f"Card{i}" for i in range(1, 101)],
        "sections": {},
        "commander": "Card1",
        "metadata": {"theme": "control"},
    }
    constraints = {"budget": 200}
    result = _run_jsonrpc("suggest_cards", {"deck": deck, "constraints": constraints}, monkeypatch, manager)
    assert result["jsonrpc"] == "2.0"
    assert result["id"] == 42
    assert isinstance(result["result"], list)
    assert result["result"] and {"name", "score"} <= set(result["result"][0].keys())
