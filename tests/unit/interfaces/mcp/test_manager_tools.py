"""Happy-path tests for new MCP tools with schemas (explain_card, compare_cards)."""

import io
import json
import sys

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.stdio_service import StdioMCPService


class DummyInteractor(Interactor):
    def __init__(self):
        super().__init__(
            card_data_manager=self,
            rag_manager=self,
            llm_manager=self,
            db_manager=self,
            query_cache=None,
        )

    def answer_natural_language_query(self, query):  # pragma: no cover - passthrough
        # Return a deterministic echo for assertions
        return f"NLG:{query}"


def _run_one(input_obj, monkeypatch):
    stdin = io.StringIO(json.dumps(input_obj) + "\n")
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    service = StdioMCPService()
    interactor = DummyInteractor()
    manager = MCPManager(service, interactor)
    req = service.read_request()
    resp = manager.dispatch(req)
    service.send_response(resp)
    return stdout.getvalue()


def test_explain_card_legacy(monkeypatch):
    out = _run_one({"tool": "explain_card", "args": {"card_name": "Sol Ring"}}, monkeypatch)
    assert "NLG:Explain the Magic: The Gathering card 'Sol Ring'" in out


def test_explain_card_jsonrpc(monkeypatch):
    out = _run_one(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "explain_card",
            "params": {"card_name": "Sol Ring"},
        },
        monkeypatch,
    )
    assert '"jsonrpc": "2.0"' in out
    assert '"id": 1' in out
    assert "NLG:Explain the Magic: The Gathering card 'Sol Ring'" in out


def test_compare_cards_legacy(monkeypatch):
    out = _run_one(
        {"tool": "compare_cards", "args": {"card_a": "Sol Ring", "card_b": "Mana Vault"}},
        monkeypatch,
    )
    assert "NLG:Compare the cards 'Sol Ring' vs 'Mana Vault'" in out


def test_compare_cards_jsonrpc(monkeypatch):
    out = _run_one(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "compare_cards",
            "params": {"card_a": "Sol Ring", "card_b": "Mana Vault"},
        },
        monkeypatch,
    )
    assert '"jsonrpc": "2.0"' in out
    assert '"id": 2' in out
    assert "NLG:Compare the cards 'Sol Ring' vs 'Mana Vault'" in out
