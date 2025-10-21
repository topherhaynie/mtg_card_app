"""MCP Server scaffold for MTG Card App (Phase 4)"""

import logging

from mtg_card_app.core.interactor import Interactor

logger = logging.getLogger(__name__)


class MTGCardMCPServer:
    """Model Context Protocol (MCP) server for MTG Card App.
    Handles incoming MCP requests and delegates to Interactor.
    """

    def __init__(self):
        self.interactor = Interactor()
        logger.info("MCP Server initialized.")

    def handle_query_cards(self, query: str, filters: dict = None):
        # TODO: Implement filter support
        return self.interactor.answer_natural_language_query(query)

    def handle_find_combo_pieces(self, card_name: str, n_results: int = 5):
        return self.interactor.find_combo_pieces(card_name, n_results)

    def handle_search_cards(self, card_name: str):
        return self.interactor.search_cards(card_name)

    # TODO: Add advanced tool handlers (explain_card, compare_cards, etc.)

    # TODO: Implement MCP protocol loop (stdio or socket)
