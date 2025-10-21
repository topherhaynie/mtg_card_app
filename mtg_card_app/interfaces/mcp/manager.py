"""MCPManager: Orchestrates MCP service and delegates to Interactor."""

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.interfaces.mcp.services.base import MCPService


class MCPManager:
    """Manager for MCP service lifecycle and request dispatch."""

    def __init__(self, service: MCPService, interactor: Interactor):
        self.service = service
        self.interactor = interactor

    def run(self):
        """Run the MCP main loop: read requests, dispatch, send responses."""
        try:
            while True:
                request = self.service.read_request()
                response = self.dispatch(request)
                self.service.send_response(response)
        except (EOFError, KeyboardInterrupt):
            self.service.close()

    def dispatch(self, request: dict) -> dict:
        """Dispatch an MCP request to the appropriate Interactor method."""
        # Example: expects {"tool": "query_cards", "args": {...}}
        tool = request.get("tool")
        args = request.get("args", {})
        try:
            if tool == "query_cards":
                query = args.get("query", "")
                return {"result": self.interactor.answer_natural_language_query(query)}
            if tool == "find_combo_pieces":
                card_name = args.get("card_name", "")
                n_results = args.get("n_results", 5)
                return {"result": self.interactor.find_combo_pieces(card_name, n_results)}
            if tool == "search_cards":
                card_name = args.get("card_name", "")
                return {"result": self.interactor.search_cards(card_name)}
            # TODO: Add advanced tool dispatches
            return {"error": f"Unknown tool: {tool}"}
        except Exception as e:
            return {"error": str(e)}
