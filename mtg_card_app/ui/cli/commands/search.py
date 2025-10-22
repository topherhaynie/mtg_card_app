"""Search command - Search for MTG cards."""

import click
from rich.console import Console

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--limit", "-n", default=10, help="Maximum number of results")
@click.option("--budget", "-b", type=float, help="Maximum price filter")
@click.option("--format", "-f", type=click.Choice(["table", "json", "text"]), default="table", help="Output format")
def search(query: tuple[str, ...], limit: int, budget: float | None, format: str) -> None:
    """Search for MTG cards using natural language or Scryfall syntax.

    Examples:
        mtg search "Lightning Bolt"

        mtg search "blue counterspells" --limit 20

        mtg search "t:creature cmc<=3" --budget 5

    """
    # Join query parts
    query_str = " ".join(query)

    # Initialize interactor
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status(f"[cyan]Searching for: {query_str}...[/cyan]", spinner="dots"):
            # Use natural language query for semantic search
            response = interactor.answer_natural_language_query(
                f"Find cards matching: {query_str}. Show top {limit} results.",
            )

        if format == "table":
            _display_table_results(response)
        elif format == "json":
            # TODO: Parse response and output JSON
            console.print(response)
        else:  # text
            console.print(response)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def _display_table_results(response: str) -> None:
    """Display search results in a table format.

    Args:
        response: The LLM response text

    """
    # For now, just display the response as markdown
    # TODO: Parse structured results from LLM and format as table
    from rich.markdown import Markdown

    console.print(Markdown(response))
