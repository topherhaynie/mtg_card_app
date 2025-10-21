"""Tests for JSONRPCStdioService Content-Length framing."""

import io
import json
import sys

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.interfaces.mcp.manager import MCPManager
from mtg_card_app.interfaces.mcp.services.jsonrpc_stdio_service import (
    JSONRPCStdioService,
)


class DummyManager:
    """Minimal card manager stub used by DummyInteractor in tests."""

    def search_cards(self, card_name):  # type: ignore[no-untyped-def]
        """Return a single result tagged with the provided card name."""
        return [f"card:{card_name}"]


class DummyInteractor(Interactor):
    """Interactor wired with dummy managers for isolated protocol tests."""

    def __init__(self) -> None:  # pragma: no cover - trivial wiring
        """Construct with lightweight dummy dependencies."""
        super().__init__(
            card_data_manager=DummyManager(),
            rag_manager=DummyManager(),
            llm_manager=DummyManager(),
            db_manager=DummyManager(),
            query_cache=None,
        )

    def search_cards(self, card_name):  # type: ignore[no-untyped-def]
        """Delegate to the dummy card manager behavior."""
        return [f"card:{card_name}"]


def test_content_length_jsonrpc_search_cards(monkeypatch):
    """Parse a Content-Length framed JSON-RPC request and dispatch it."""
    # Prepare a JSON-RPC request body
    body_obj = {
        "jsonrpc": "2.0",
        "id": 42,
        "method": "search_cards",
        "params": {"card_name": "alpha"},
    }
    body = json.dumps(body_obj)
    header = f"Content-Length: {len(body)}\n\n"

    stdin = io.StringIO(header + body)
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)

    service = JSONRPCStdioService()
    interactor = DummyInteractor()
    manager = MCPManager(service, interactor)

    request = service.read_request()
    response = manager.dispatch(request)
    service.send_response(response)

    out = stdout.getvalue()
    assert '"jsonrpc": "2.0"' in out
    assert '"id": 42' in out
    assert "card:alpha" in out
