"""Stats command - Show system statistics."""

from rich.console import Console
from rich.table import Table

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


def show_stats() -> None:
    """Display system statistics and service information."""
    # Initialize interactor
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    # Get stats
    stats = interactor.get_system_stats()

    # Create table
    table = Table(title="🎴 MTG Card App - System Statistics", show_header=True)
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # LLM stats
    llm_stats = stats.get("llm", {})
    if llm_stats:
        table.add_row("LLM Provider", llm_stats.get("provider", "Unknown"))
        table.add_row("LLM Model", llm_stats.get("model", "Unknown"))

    # Card data stats
    card_stats = stats.get("card_data")
    if card_stats:
        table.add_row("Total Cards", f"{card_stats.get('total_cards', 0):,}")

    # RAG stats
    rag_stats = stats.get("rag")
    if rag_stats:
        table.add_row("RAG Service", "Active" if rag_stats else "N/A")

    # DB stats
    db_stats = stats.get("db")
    if db_stats:
        table.add_row("Database", "SQLite")

    # Display table
    console.print(table)
