"""Unit tests for MCPManager and StdioMCPService."""

import io
import json
import sys

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.stdio_service import StdioMCPService


# Minimal dummy managers for explicit Interactor signature
class DummyManager:
    def get_card(self, name):
        return f"card:{name}"

    def search_cards(self, query, use_local=True, use_scryfall=False):
        return [f"card:{query}"]

    def bulk_import_cards(self, card_names):
        return {"imported": card_names}

    def get_budget_cards(self, max_price):
        return [f"budget_card:{max_price}"]

    def find_combo_pieces(self, card_name, n_results=5):
        return [f"combo:{card_name}:{n_results}"]


class DummyInteractor(Interactor):
    def __init__(self):
        super().__init__(
            card_data_manager=DummyManager(),
            rag_manager=DummyManager(),
            llm_manager=DummyManager(),
            db_manager=DummyManager(),
            query_cache=None,
        )

    def answer_natural_language_query(self, query):
        return f"query:{query}"

    def find_combo_pieces(self, card_name, n_results=5):
        return [f"combo:{card_name}:{n_results}"]

    def search_cards(self, card_name):
        return [f"card:{card_name}"]


def test_mcpmanager_query_cards(monkeypatch):
    # Simulate stdio input/output
    input_data = json.dumps({"tool": "query_cards", "args": {"query": "foo"}}) + "\n"
    stdin = io.StringIO(input_data)
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    service = StdioMCPService()
    interactor = DummyInteractor()
    manager = MCPManager(service, interactor)
    # Run one loop iteration
    request = service.read_request()
    response = manager.dispatch(request)
    service.send_response(response)
    output = stdout.getvalue()
    assert "query:foo" in output


def test_mcpmanager_find_combo_pieces(monkeypatch):
    input_data = json.dumps({"tool": "find_combo_pieces", "args": {"card_name": "bar", "n_results": 2}}) + "\n"
    stdin = io.StringIO(input_data)
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    service = StdioMCPService()
    interactor = DummyInteractor()
    manager = MCPManager(service, interactor)
    request = service.read_request()
    response = manager.dispatch(request)
    service.send_response(response)
    output = stdout.getvalue()
    assert "combo:bar:2" in output


def test_mcpmanager_search_cards(monkeypatch):
    input_data = json.dumps({"tool": "search_cards", "args": {"card_name": "baz"}}) + "\n"
    stdin = io.StringIO(input_data)
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    service = StdioMCPService()
    interactor = DummyInteractor()
    manager = MCPManager(service, interactor)
    request = service.read_request()
    response = manager.dispatch(request)
    service.send_response(response)
    output = stdout.getvalue()
    assert "card:baz" in output
