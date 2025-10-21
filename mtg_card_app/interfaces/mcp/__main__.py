"""Entry point to launch the MCP server via stdio."""

from mtg_card_app.core.manager_registry import ManagerRegistry


def main():
    registry = ManagerRegistry.get_instance()
    mcp_manager = registry.mcp_manager
    mcp_manager.run()


if __name__ == "__main__":
    main()
