"""Initialization metadata tests for MCPManager.

Validates that initialize advertises tools with input schemas and output schemas.
"""

import io
import json
import sys

from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.stdio_service import StdioMCPService


class _DummyInteractor:
    def answer_natural_language_query(self, query: str) -> str:
        return f"query:{query}"

    def find_combo_pieces(self, card_name: str, n_results: int = 5) -> str:
        return f"combo:{card_name}:{n_results}"

    def search_cards(self, card_name: str):
        # Return minimal objects with to_dict to simulate Card
        class _C:
            def __init__(self, name: str):
                self.name = name

            def to_dict(self):
                return {
                    "id": "x",
                    "name": self.name,
                    "cmc": 1,
                    "type_line": "Instant",
                    "colors": ["R"],
                    "oracle_text": "",
                }

        return [_C(card_name)]


def test_initialize_advertises_output_schema(monkeypatch):
    stdin = io.StringIO(json.dumps({"tool": "initialize", "args": {}}) + "\n")
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)

    service = StdioMCPService()
    interactor = _DummyInteractor()
    manager = MCPManager(service, interactor)  # type: ignore[arg-type]

    request = service.read_request()
    resp = manager.dispatch(request)
    service.send_response(resp)

    data = json.loads(stdout.getvalue())
    assert "result" in data or "tools" in data  # legacy path returns result directly

    # Handle legacy structure
    payload = data.get("result", data)
    assert "tools" in payload and isinstance(payload["tools"], list)

    # Find search_cards tool and assert outputSchema present
    tools = {t["name"]: t for t in payload["tools"]}
    assert "search_cards" in tools
    assert "outputSchema" in tools["search_cards"]
