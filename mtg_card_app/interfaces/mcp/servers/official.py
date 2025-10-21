"""Optional integration with the official MCP Python server.

This adapter reuses our MCPManager.dispatch by wrapping each tool as a handler
in the official server. It requires the `mcp` package at runtime.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from collections.abc import Callable

    from mtg_card_app.interfaces.mcp.manager import MCPManager

# Optional dependency: attempt import at module load
try:  # pragma: no cover - exercised only when dependency installed
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    HAS_MCP = True
except ImportError:  # pragma: no cover - no MCP available
    HAS_MCP = False


def _build_dispatch_wrapper(manager: MCPManager) -> dict[str, Callable[..., object]]:
    """Return callables for each tool that proxy to MCPManager.dispatch.

    Each callable takes keyword args, constructs a JSON-RPC-like dict, and
    returns the unwrapped `result` from the manager (or raises on error).
    """

    def _proxy(method: str) -> Callable[..., object]:
        def _call(**kwargs: object) -> object:
            req = {"jsonrpc": "2.0", "id": 0, "method": method, "params": dict(kwargs)}
            resp = manager.dispatch(req)
            if "error" in resp:
                # Raise a ValueError to let the MCP server format an error
                raise ValueError(resp["error"])  # intentional propagation
            return resp.get("result")

        return _call

    return {
        "query_cards": _proxy("query_cards"),
        "explain_card": _proxy("explain_card"),
        "compare_cards": _proxy("compare_cards"),
        "find_combo_pieces": _proxy("find_combo_pieces"),
        "search_cards": _proxy("search_cards"),
        "get_history": _proxy("get_history"),
        "clear_history": _proxy("clear_history"),
    }


def main() -> None:
    """Run the official MCP stdio server if available.

    Falls back with a clear message if the dependency is missing.
    """
    if not HAS_MCP:
        msg = (
            "The 'mcp' package is not installed. Install with:\n"
            "  pip install mcp\n"
            "or run the classic stdio server: 'python -m mtg_card_app.interfaces.mcp'"
        )
        raise SystemExit(msg)

    # Construct interactor and manager using our registry wiring
    from mtg_card_app.core.manager_registry import ManagerRegistry
    from mtg_card_app.interfaces.mcp.manager import MCPManager

    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor

    # We don't need an MCPService for the official server; pass a dummy
    class _NullService:
        def read_request(self) -> dict[str, object]:  # pragma: no cover - not used in official mode
            raise NotImplementedError

        def send_response(self, response: object) -> None:  # pragma: no cover - not used in official mode
            raise NotImplementedError

        def close(self) -> None:  # pragma: no cover - not used in official mode
            return None

    manager = MCPManager(_NullService(), interactor)
    tools = _build_dispatch_wrapper(manager)

    server = Server("mtg-card-app")

    # Dynamically register tools
    for name, func in tools.items():
        server.tool(name=name)(func)  # type: ignore[misc]

    # Start stdio server loop
    stdio_server(server).run()
