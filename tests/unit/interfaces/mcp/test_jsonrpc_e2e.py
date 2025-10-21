"""E2E JSON-RPC golden-path and schema validation tests for all MCP tools."""

import io
import json
import sys

import pytest
from jsonschema import validate

from mtg_card_app.domain.entities.card import Card
from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.stdio_service import StdioMCPService


class DummyInteractor:
    def answer_natural_language_query(self, query):
        return f"NLG:{query}"

    def find_combo_pieces(self, card_name, n_results=5):
        return f"combo:{card_name}:{n_results}"

    def search_cards(self, card_name):
        return [
            Card(
                id="cardid",
                name=card_name,
                cmc=1,
                type_line="Instant",
                oracle_text="Counter target spell.",
                colors=["U"],
            )
        ]


@pytest.fixture
def manager():
    service = StdioMCPService()
    interactor = DummyInteractor()
    return MCPManager(service, interactor, validate_output=True)


def run_jsonrpc(method, params, monkeypatch, manager):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    stdin = io.StringIO(json.dumps(req) + "\n")
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    request = manager.service.read_request()
    resp = manager.dispatch(request)
    manager.service.send_response(resp)
    return json.loads(stdout.getvalue())


def test_initialize_schema_advertised(monkeypatch, manager):
    result = run_jsonrpc("initialize", {}, monkeypatch, manager)
    assert "result" in result
    tools = result["result"]["tools"]
    assert any(t["name"] == "search_cards" and "outputSchema" in t for t in tools)


def test_search_cards_schema(monkeypatch, manager):
    result = run_jsonrpc("search_cards", {"card_name": "Counterspell"}, monkeypatch, manager)
    assert "result" in result
    # Validate output against schema
    schema = manager._output_schemas["search_cards"]
    validate(instance=result["result"], schema=schema)


def test_explain_card(monkeypatch, manager):
    result = run_jsonrpc("explain_card", {"card_name": "Sol Ring"}, monkeypatch, manager)
    assert result["result"].startswith("NLG:Explain the Magic: The Gathering card")


def test_compare_cards(monkeypatch, manager):
    result = run_jsonrpc("compare_cards", {"card_a": "Bolt", "card_b": "Shock"}, monkeypatch, manager)
    assert result["result"].startswith("NLG:Compare the cards")


def test_query_cards(monkeypatch, manager):
    result = run_jsonrpc("query_cards", {"query": "What is a counterspell?"}, monkeypatch, manager)
    assert result["result"].startswith("NLG:What is a counterspell?")


def test_find_combo_pieces(monkeypatch, manager):
    result = run_jsonrpc("find_combo_pieces", {"card_name": "Isochron Scepter", "n_results": 2}, monkeypatch, manager)
    assert result["result"].startswith("combo:Isochron Scepter:2")
