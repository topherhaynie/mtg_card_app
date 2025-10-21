"""MCPManager: Orchestrates MCP service and delegates to Interactor."""

import uuid
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from time import perf_counter

from jsonschema import ValidationError, validate

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities.card import Card
from mtg_card_app.domain.entities.deck import Deck as DeckEntity
from mtg_card_app.interfaces.mcp.services.base import MCPService


class MCPManager:
    """Manager for MCP service lifecycle and request dispatch."""

    DEFAULT_MAX_HISTORY = 100

    def __init__(
        self,
        service: MCPService,
        interactor: Interactor,
        *,
        validate_output: bool = False,
        max_history: int | None = None,
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
            "build_deck": {
                "type": "object",
                "properties": {
                    "format": {"type": "string"},
                    "cards": {"type": "array", "items": {"type": "string"}},
                    "sections": {"type": "object"},
                    "commander": {"type": ["string", "null"]},
                    "metadata": {"type": "object"},
                },
                "required": ["format", "cards"],
                "additionalProperties": True,
            },
            "validate_deck": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "errors": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["valid", "errors"],
                "additionalProperties": False,
            },
            "analyze_deck": {"type": "object"},
            "suggest_cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "score": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
            },
        }
        # JSON Schemas for tool/method parameters
        self._schemas: dict[str, dict] = {
            "build_deck": {
                "type": "object",
                "properties": {
                    "deck_format": {"type": "string"},
                    "card_pool": {"type": "array", "items": {"type": "string"}},
                    "commander": {"type": ["string", "null"]},
                    "constraints": {"type": ["object", "null"]},
                    "metadata": {"type": ["object", "null"]},
                },
                "required": ["deck_format", "card_pool"],
                "additionalProperties": False,
            },
            "validate_deck": {
                "type": "object",
                "properties": {
                    "deck": {"type": "object"},
                },
                "required": ["deck"],
                "additionalProperties": False,
            },
            "analyze_deck": {
                "type": "object",
                "properties": {
                    "deck": {"type": "object"},
                },
                "required": ["deck"],
                "additionalProperties": False,
            },
            "suggest_cards": {
                "type": "object",
                "properties": {
                    "deck": {"type": "object"},
                    "constraints": {"type": ["object", "null"]},
                },
                "required": ["deck"],
                "additionalProperties": False,
            },
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
        if request.get("jsonrpc") == "2.0" and "method" in request:
            return self._dispatch_jsonrpc(request)
        return self._dispatch_legacy(request)

    def _dispatch_jsonrpc(self, request: dict) -> dict:
        method = request.get("method")
        params = request.get("params", {}) or {}
        req_id = request.get("id")
        _start = perf_counter()
        try:
            self._validate_params(method, params)
            result = self._dispatch_tool(method, params)
            if self._validate_output and method in self._output_schemas:
                try:
                    validate(instance=result, schema=self._output_schemas[method])
                except ValidationError as ve:
                    msg = f"Output validation failed: {ve.message}"
                    raise RuntimeError(msg) from ve
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
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": msg}}
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
            return {
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
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
        else:
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
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _dispatch_legacy(self, request: dict) -> dict:
        tool = request.get("tool")
        args = request.get("args", {}) or {}
        legacy_req_id = uuid.uuid4().hex[:8]
        try:
            _start = perf_counter()
            self._validate_params(tool, args)
            result = self._dispatch_tool(tool, args)
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
            return {
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
            return {
                "error": {
                    "code": -32000,
                    "message": str(e),
                    "id": legacy_req_id,
                    "tool": tool,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
        else:
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
            return {"result": result}

    def _dispatch_tool(self, name: str | None, args: dict) -> object:
        """Map tool/method name to interactor calls and server utilities."""
        if name in {"initialize", "mcp.initialize"}:
            return self._handle_initialize()
        if name == "get_history":
            return self._handle_get_history(args)
        if name == "clear_history":
            return self._handle_clear_history()

        handlers = {
            "explain_card": self._handle_explain_card,
            "compare_cards": self._handle_compare_cards,
            "query_cards": self._handle_query_cards,
            "find_combo_pieces": self._handle_find_combo_pieces,
            "search_cards": self._handle_search_cards,
            "build_deck": self._handle_build_deck,
            "validate_deck": self._handle_validate_deck,
            "analyze_deck": self._handle_analyze_deck,
            "suggest_cards": self._handle_suggest_cards,
        }
        func = handlers.get(name)
        if func is not None:
            return func(args)
        msg = f"Unknown tool: {name}"
        raise ValueError(msg)

    # ------------------------
    # Handlers (split for clarity and lint friendliness)
    # ------------------------
    def _handle_initialize(self) -> object:
        try:
            version_str = importlib_metadata.version("mtg-card-app")
        except importlib_metadata.PackageNotFoundError:  # local dev fallback
            version_str = "0.1.0"
        # Tool descriptions and examples
        tool_metadata = {
            "query_cards": {
                "description": ("Answer a natural language query about Magic: The Gathering cards, rules, or combos."),
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
            "build_deck": {
                "description": (
                    "Build a deck object from a format and card pool, with optional commander, "
                    "constraints, and metadata."
                ),
                "example": {
                    "deck_format": "Commander",
                    "card_pool": ["Sol Ring", "Swords to Plowshares", "Counterspell", "Rhystic Study", "..."],
                    "commander": "Edgar Markov",
                    "constraints": {"budget": 200},
                    "metadata": {"theme": "vampires"},
                },
            },
            "validate_deck": {
                "description": (
                    "Validate a deck against format rules (e.g., Commander requires 100 cards and a commander)."
                ),
                "example": {
                    "deck": {
                        "format": "Commander",
                        "cards": ["Sol Ring", "Arcane Signet", "..."],
                        "sections": {},
                        "commander": "Edgar Markov",
                        "metadata": {"theme": "vampires"},
                    },
                },
            },
            "analyze_deck": {
                "description": "Analyze a deck's mana curve, card types, color distribution, and potential issues.",
                "example": {
                    "deck": {
                        "format": "Commander",
                        "cards": ["Sol Ring", "Arcane Signet", "..."],
                        "sections": {},
                        "commander": "Edgar Markov",
                        "metadata": {"theme": "vampires"},
                    },
                },
            },
            "suggest_cards": {
                "description": (
                    "Suggest cards that fit the deck's theme and needs, optionally constrained by budget or "
                    "other factors."
                ),
                "example": {
                    "deck": {
                        "format": "Commander",
                        "cards": ["Sol Ring", "Arcane Signet", "..."],
                        "sections": {},
                        "commander": "Edgar Markov",
                        "metadata": {"theme": "vampires"},
                    },
                    "constraints": {"budget": 200},
                },
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

    def _handle_get_history(self, args: dict) -> object:
        limit = int(args.get("limit", 50))
        tool_filter = args.get("tool")
        req_id_filter = args.get("id")
        since_str = args.get("since")
        error_only = bool(args.get("error_only", False))

        since_dt = None
        if since_str:
            try:
                since_dt = datetime.fromisoformat(str(since_str).replace("Z", "+00:00"))
            except (ValueError, TypeError):
                since_dt = None

        def _entry_ok(entry: dict) -> bool:
            ok = True
            if tool_filter and entry.get("tool") != tool_filter:
                ok = False
            if ok and req_id_filter is not None and entry.get("id") != req_id_filter:
                ok = False
            if ok and error_only and "error" not in entry:
                ok = False
            if ok and since_dt:
                ts = entry.get("timestamp")
                if not ts:
                    ok = False
                else:
                    try:
                        entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        ok = entry_dt >= since_dt
                    except (ValueError, TypeError):
                        ok = True
            return ok

        results = [e for e in self._history if _entry_ok(e)]
        return results[-limit:]

    def _handle_clear_history(self) -> object:
        self._history.clear()
        return {"ok": True}

    def _handle_explain_card(self, args: dict) -> object:
        card_name = args.get("card_name", "")
        prompt = f"Explain the Magic: The Gathering card '{card_name}' in simple terms and provide strategic uses."
        return self.interactor.answer_natural_language_query(prompt)

    def _handle_compare_cards(self, args: dict) -> object:
        card_a = args.get("card_a", "")
        card_b = args.get("card_b", "")
        prompt = (
            "Compare the cards "
            f"'{card_a}' vs '{card_b}' "
            "with pros/cons, synergies, and when to choose one over the other."
        )
        return self.interactor.answer_natural_language_query(prompt)

    def _handle_query_cards(self, args: dict) -> object:
        query = args.get("query", "")
        return self.interactor.answer_natural_language_query(query)

    def _handle_find_combo_pieces(self, args: dict) -> object:
        card_name = args.get("card_name", "")
        n_results = args.get("n_results", 5)
        return self.interactor.find_combo_pieces(card_name, n_results)

    def _handle_search_cards(self, args: dict) -> object:
        card_name = args.get("card_name", "")
        cards = self.interactor.search_cards(card_name)
        # Ensure JSON-serializable response of Card entities
        return [c.to_dict() if isinstance(c, Card) else c for c in cards]

    def _handle_build_deck(self, args: dict) -> object:
        deck_format = args.get("deck_format", "")
        card_pool = args.get("card_pool", [])
        commander = args.get("commander")
        constraints = args.get("constraints")
        metadata = args.get("metadata")
        deck = self.interactor.build_deck(deck_format, card_pool, commander, constraints, metadata)
        # Serialize Deck object to dict for JSON
        return deck.to_dict() if hasattr(deck, "to_dict") else deck

    def _convert_deck_arg(self, deck_data: object) -> object:
        if isinstance(deck_data, dict):
            try:
                return DeckEntity.from_dict(deck_data)
            except (TypeError, ValueError):
                return deck_data
        return deck_data

    def _handle_validate_deck(self, args: dict) -> object:
        deck_data = args.get("deck")
        deck_obj = self._convert_deck_arg(deck_data)
        return self.interactor.validate_deck(deck_obj)

    def _handle_analyze_deck(self, args: dict) -> object:
        deck_data = args.get("deck")
        deck_obj = self._convert_deck_arg(deck_data)
        return self.interactor.analyze_deck(deck_obj)

    def _handle_suggest_cards(self, args: dict) -> object:
        deck_data = args.get("deck")
        constraints = args.get("constraints")
        deck_obj = self._convert_deck_arg(deck_data)
        return self.interactor.suggest_cards(deck_obj, constraints)

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
