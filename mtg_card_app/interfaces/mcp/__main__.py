"""Entry point to launch the MCP server.

Usage:
  - Default (classic stdio): mtg-card-app (or python -m mtg_card_app.interfaces.mcp)
  - Official MCP server:     python -m mtg_card_app.interfaces.mcp --server official
"""

import argparse
import os

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.interfaces.mcp.servers.official import main as official_main


def main() -> None:
    """Run the MCP server with a selectable backend (classic or official)."""
    parser = argparse.ArgumentParser(description="Run MCP server")
    parser.add_argument(
        "--server",
        choices=["classic", "official"],
        default=os.environ.get("MCP_SERVER", "classic"),
        help="Choose the server implementation (default: classic)",
    )
    args = parser.parse_args()

    if args.server == "official":
        # Run the official MCP server adapter (requires 'mcp' dependency)
        official_main()
        return

    # Classic stdio server path (default)
    registry = ManagerRegistry.get_instance()
    mcp_manager = registry.mcp_manager
    mcp_manager.run()


if __name__ == "__main__":
    main()
