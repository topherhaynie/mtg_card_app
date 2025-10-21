"""MCPService: Handles parsing, formatting, and dispatching MCP requests."""

from mtg_card_app.core.interactor import Interactor


class MCPService:
    """Service for handling MCP requests and responses."""

    def __init__(self, interactor: Interactor):
        self.interactor = interactor

    def handle_request(self, request: dict) -> dict:
        """Dispatch request to the appropriate Interactor method."""
        # TODO: Implement request parsing and dispatch logic
        return {"error": "Not implemented"}
