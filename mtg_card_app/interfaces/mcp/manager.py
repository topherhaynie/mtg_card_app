"""MCPManager: Orchestrates MCP service and delegates to Interactor."""

import uuid
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from time import perf_counter

from jsonschema import ValidationError, validate

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities.card import Card
from mtg_card_app.interfaces.mcp.services.base import MCPService


class MCPManager:
    """Manager for MCP service lifecycle and request dispatch."""

    DEFAULT_MAX_HISTORY = 100

    def __init__(
        self, service: MCPService, interactor: Interactor, validate_output: bool = False, max_history: int = None
    ) -> None:
        """Initialize with a service transport and the domain interactor.

        :param validate_output: If True, validate tool outputs against outputSchema.
        :param max_history: Maximum number of history entries to keep (default: 100)
        """
        self.service = service
        self.interactor = interactor
        self._history: list[dict] = []
        self._validate_output = validate_output
        self._max_history = max_history if max_history is not None else self.DEFAULT_MAX_HISTORY
        # JSON Schemas for tool/method outputs (optional)
        self._output_schemas: dict[str, dict] = {
            "query_cards": {"type": "string"},
            "explain_card": {"type": "string"},
            "compare_cards": {"type": "string"},
            "find_combo_pieces": {"type": "string"},
            "search_cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "cmc": {"type": "number"},
                        "type_line": {"type": "string"},
                        "colors": {"type": "array", "items": {"type": "string"}},
                        "oracle_text": {"type": ["string", "null"]},
                    },
                    "additionalProperties": True,
                },
            },
        }
        # JSON Schemas for tool/method parameters
        self._schemas: dict[str, dict] = {
            "query_cards": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False,
            },
            "explain_card": {
                "type": "object",
                "properties": {"card_name": {"type": "string"}},
                "required": ["card_name"],
                "additionalProperties": False,
            },
            "compare_cards": {
                "type": "object",
                "properties": {
                    "card_a": {"type": "string"},
                    "card_b": {"type": "string"},
                },
                "required": ["card_a", "card_b"],
                "additionalProperties": False,
            },
            "find_combo_pieces": {
                "type": "object",
                "properties": {
                    "card_name": {"type": "string"},
                    "n_results": {"type": "integer", "minimum": 1},
                },
                "required": ["card_name"],
                "additionalProperties": False,
            },
            "search_cards": {
                "type": "object",
                "properties": {"card_name": {"type": "string"}},
                "required": ["card_name"],
                "additionalProperties": False,
            },
            "get_history": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1},
                    "tool": {"type": "string"},
                    "since": {"type": "string"},
                    "id": {"type": ["string", "number", "null"]},
                    "error_only": {"type": "boolean"},
                },
                "additionalProperties": False,
            },
            "clear_history": {"type": "object", "additionalProperties": False},
        }

    def run(self) -> None:
        """Run the MCP main loop: read requests, dispatch, send responses."""
        try:
            while True:
                request = self.service.read_request()
                response = self.dispatch(request)
                self.service.send_response(response)
        except (EOFError, KeyboardInterrupt):
            self.service.close()

    def dispatch(self, request: dict) -> dict:
        """Dispatch an MCP request to the appropriate Interactor method.

        Supports two formats:
        - Legacy tool format: {"tool": str, "args": dict}
        - JSON-RPC 2.0 format: {"jsonrpc": "2.0", "id": X, "method": str, "params": dict}
        """
        # JSON-RPC detection
        is_jsonrpc = request.get("jsonrpc") == "2.0" and "method" in request
        response: dict
        if is_jsonrpc:
            method = request.get("method")
            params = request.get("params", {}) or {}
            req_id = request.get("id")
            _start = perf_counter()

            try:
                self._validate_params(method, params)
                result = self._dispatch_tool(method, params)
                # Output validation if enabled and schema exists
                if self._validate_output and method in self._output_schemas:
                    try:
                        validate(instance=result, schema=self._output_schemas[method])
                    except ValidationError as ve:
                        raise RuntimeError(f"Output validation failed: {ve.message}")
                duration_ms = (perf_counter() - _start) * 1000.0
                self._record_history(
                    method,
                    params,
                    result=result,
                    meta={
                        "id": req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": round(duration_ms, 3),
                    },
                )
                response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            except ValidationError as e:
                msg = f"Invalid params: {e.message}"
                duration_ms = (perf_counter() - _start) * 1000.0
                self._record_history(
                    method,
                    params,
                    error=msg,
                    meta={
                        "id": req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": round(duration_ms, 3),
                    },
                )
                response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": msg}}
            except KeyError as e:
                duration_ms = (perf_counter() - _start) * 1000.0
                self._record_history(
                    method,
                    params,
                    error=f"Invalid params: {e}",
                    meta={
                        "id": req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": round(duration_ms, 3),
                    },
                )
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": f"Invalid params: {e}"},
                }
            except (TypeError, RuntimeError, ValueError) as e:
                duration_ms = (perf_counter() - _start) * 1000.0
                self._record_history(
                    method,
                    params,
                    error=str(e),
                    meta={
                        "id": req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": round(duration_ms, 3),
                    },
                )
                response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
        else:
            # Legacy tool format
            tool = request.get("tool")
            args = request.get("args", {}) or {}
            # Generate an internal request id for observability in legacy mode
            legacy_req_id = uuid.uuid4().hex[:8]
            try:
                _start = perf_counter()
                self._validate_params(tool, args)
                result = self._dispatch_tool(tool, args)
                duration_ms = (perf_counter() - _start) * 1000.0
                self._record_history(
                    tool,
                    args,
                    result=result,
                    meta={
                        "id": legacy_req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": round(duration_ms, 3),
                    },
                )
                response = {"result": result}
            except ValidationError as e:
                msg = f"Invalid params: {e.message}"
                duration_ms = (perf_counter() - _start) * 1000.0 if "_start" in locals() else None
                self._record_history(
                    tool,
                    args,
                    error=msg,
                    meta={
                        "id": legacy_req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        **({"duration_ms": round(duration_ms, 3)} if duration_ms is not None else {}),
                    },
                )
                response = {
                    "error": {
                        "code": -32602,
                        "message": msg,
                        "id": legacy_req_id,
                        "tool": tool,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                }
            except (TypeError, RuntimeError, ValueError) as e:
                duration_ms = (perf_counter() - _start) * 1000.0 if "_start" in locals() else None
                self._record_history(
                    tool,
                    args,
                    error=str(e),
                    meta={
                        "id": legacy_req_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        **({"duration_ms": round(duration_ms, 3)} if duration_ms is not None else {}),
                    },
                )
                response = {
                    "error": {
                        "code": -32000,
                        "message": str(e),
                        "id": legacy_req_id,
                        "tool": tool,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                }

        return response

    def _dispatch_tool(self, name: str | None, args: dict) -> object:
        """Map tool/method name to interactor calls and server utilities."""
        # Server/meta methods
        if name in {"initialize", "mcp.initialize"}:
            try:
                version_str = importlib_metadata.version("mtg-card-app")
            except importlib_metadata.PackageNotFoundError:  # local dev fallback
                version_str = "0.1.0"
            # Tool descriptions and examples
            tool_metadata = {
                "query_cards": {
                    "description": (
                        "Answer a natural language query about Magic: The Gathering cards, rules, or combos."
                    ),
                    "example": {"query": "What are the best blue counterspells under $5?"},
                },
                "explain_card": {
                    "description": "Explain a specific card in simple terms and provide strategic uses.",
                    "example": {"card_name": "Sol Ring"},
                },
                "compare_cards": {
                    "description": (
                        "Compare two cards, including pros/cons, synergies, and when to choose one over the other."
                    ),
                    "example": {"card_a": "Lightning Bolt", "card_b": "Shock"},
                },
                "find_combo_pieces": {
                    "description": "Find cards that combo with a given card.",
                    "example": {"card_name": "Isochron Scepter", "n_results": 5},
                },
                "search_cards": {
                    "description": "Search for cards by name (fuzzy match). Returns a list of card objects.",
                    "example": {"card_name": "Lightning"},
                },
                "get_history": {
                    "description": "Retrieve recent tool invocations, optionally filtered by tool, id, or error_only.",
                    "example": {"limit": 10, "tool": "query_cards"},
                },
                "clear_history": {
                    "description": "Clear the invocation history.",
                    "example": {},
                },
            }
            tools_desc = []
            for key, schema in self._schemas.items():
                tool_info = {"name": key, "schema": schema}
                out_schema = self._output_schemas.get(key)
                if out_schema is not None:
                    tool_info["outputSchema"] = out_schema
                meta = tool_metadata.get(key, {})
                if meta.get("description"):
                    tool_info["description"] = meta["description"]
                if meta.get("example"):
                    tool_info["example"] = meta["example"]
                tools_desc.append(tool_info)
            return {
                "server": "mtg_card_app",
                "version": version_str,
                "capabilities": {
                    "protocol": "jsonrpc-2.0",
                    "contentTypes": ["application/json"],
                    "history": True,
                    "historyMaxSize": self._max_history,
                    "historyConfigurable": True,
                    "validation": "jsonschema",
                    "outputSchemas": True,
                    "toolDescriptions": True,
                    "examples": True,
                    "outputValidationToggle": True,
                    "outputValidationEnabled": self._validate_output,
                },
                "tools": tools_desc,
            }
        if name == "get_history":
            limit = int(args.get("limit", 50))
            tool_filter = args.get("tool")
            req_id_filter = args.get("id")
            since_str = args.get("since")
            error_only = bool(args.get("error_only", False))

            def _since_ok(entry: dict) -> bool:
                if not since_str:
                    return True
                try:
                    ts = entry.get("timestamp")
                    if not ts:
                        return False
                    entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    since_dt = datetime.fromisoformat(str(since_str).replace("Z", "+00:00"))
                    return entry_dt >= since_dt
                except (ValueError, TypeError):  # parsing-safe fallback
                    return True

            results: list[dict] = []
            for entry in self._history:
                if tool_filter and entry.get("tool") != tool_filter:
                    continue
                if req_id_filter is not None and entry.get("id") != req_id_filter:
                    continue
                if error_only and "error" not in entry:
                    continue
                if not _since_ok(entry):
                    continue
                results.append(entry)

            return results[-limit:]
        if name == "clear_history":
            self._history.clear()
            return {"ok": True}

        # Tool handlers mapping to reduce returns and improve readability
        def _explain_card() -> object:
            card_name = args.get("card_name", "")
            prompt = f"Explain the Magic: The Gathering card '{card_name}' in simple terms and provide strategic uses."
            return self.interactor.answer_natural_language_query(prompt)

        def _compare_cards() -> object:
            card_a = args.get("card_a", "")
            card_b = args.get("card_b", "")
            prompt = (
                "Compare the cards "
                f"'{card_a}' vs '{card_b}' "
                "with pros/cons, synergies, and when to choose one over the other."
            )
            return self.interactor.answer_natural_language_query(prompt)

        def _query_cards() -> object:
            query = args.get("query", "")
            return self.interactor.answer_natural_language_query(query)

        def _find_combo_pieces() -> object:
            card_name = args.get("card_name", "")
            n_results = args.get("n_results", 5)
            return self.interactor.find_combo_pieces(card_name, n_results)

        def _search_cards() -> object:
            card_name = args.get("card_name", "")
            cards = self.interactor.search_cards(card_name)
            # Ensure JSON-serializable response of Card entities
            return [c.to_dict() if isinstance(c, Card) else c for c in cards]

        handlers = {
            "explain_card": _explain_card,
            "compare_cards": _compare_cards,
            "query_cards": _query_cards,
            "find_combo_pieces": _find_combo_pieces,
            "search_cards": _search_cards,
        }

        if name in handlers:
            return handlers[name]()

        msg = f"Unknown tool: {name}"
        raise ValueError(msg)

    def _record_history(
        self,
        name: str | None,
        args: dict,
        *,
        result: object | None = None,
        error: str | None = None,
        meta: dict | None = None,
    ) -> None:
        entry = {"tool": name, "args": args}
        if meta:
            entry.update(meta)
        if error is not None:
            entry["error"] = error
        # Lightly summarize large result payloads
        if result is not None:
            entry["result"] = result if isinstance(result, (str, int, float, bool, type(None))) else "ok"
        self._history.append(entry)
        if len(self._history) > self._max_history:
            del self._history[: -self._max_history]

    def _validate_params(self, name: str | None, params: dict) -> None:
        """Validate params against a registered JSON Schema for the tool/method.

        If no schema is registered, this is a no-op for forward compatibility.
        """
        if not name:
            return
        schema = self._schemas.get(name)
        if schema is None:
            return
        validate(instance=params, schema=schema)
