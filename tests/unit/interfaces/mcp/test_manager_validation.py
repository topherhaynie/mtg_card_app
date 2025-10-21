"""Validation tests for MCPManager parameter schemas."""

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

    # Interactor-facing implementations used by dispatch
    def answer_natural_language_query(self, query):  # pragma: no cover - not hit in invalid tests
        return f"query:{query}"

    def find_combo_pieces(self, card_name, n_results=5):  # pragma: no cover - not hit in invalid tests
        return [f"combo:{card_name}:{n_results}"]

    def search_cards(self, card_name):  # pragma: no cover - not hit in invalid tests
        return [f"card:{card_name}"]


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


def test_legacy_query_cards_missing_param(monkeypatch):
    # Missing required "query" param
    out = _run_one({"tool": "query_cards", "args": {}}, monkeypatch)
    assert "Invalid params" in out


def test_legacy_find_combo_pieces_wrong_type(monkeypatch):
    # n_results must be integer
    out = _run_one(
        {"tool": "find_combo_pieces", "args": {"card_name": "Sol Ring", "n_results": "two"}},
        monkeypatch,
    )
    assert "Invalid params" in out


def test_jsonrpc_search_cards_missing_param(monkeypatch):
    # JSON-RPC: missing required card_name
    out = _run_one(
        {"jsonrpc": "2.0", "id": 7, "method": "search_cards", "params": {}},
        monkeypatch,
    )
    assert '"code": -32602' in out and "Invalid params" in out
