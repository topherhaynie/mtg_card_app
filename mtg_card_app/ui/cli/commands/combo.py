"""Combo commands - Find and manage combos."""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


@click.group()
def combo() -> None:
    """Find and manage MTG card combos.

    Examples:
        mtg combo find "Isochron Scepter"
        mtg combo search "Thoracle"
        mtg combo budget 100
    """


@combo.command()
@click.argument("card_name")
@click.option("--limit", "-n", default=5, help="Maximum number of results")
def find(card_name: str, limit: int) -> None:
    """Find potential combo pieces using semantic search.

    This uses AI-powered semantic search to find cards that combo well
    with the specified card.

    Examples:
        mtg combo find "Isochron Scepter" --limit 10
        mtg combo find "Thassa's Oracle"
    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status(f"[cyan]Finding combos for: {card_name}...[/cyan]", spinner="dots"):
            results = interactor.find_combo_pieces(card_name, n_results=limit)

        if not results:
            console.print(f"[yellow]No combo pieces found for: {card_name}[/yellow]")
            return

        # Display results
        console.print(f"\n[bold cyan]🎴 Potential Combo Pieces for '{card_name}':[/bold cyan]\n")

        for i, card in enumerate(results, 1):
            name = card.get("name", "Unknown")
            oracle_text = card.get("oracle_text", "")[:150]  # Truncate
            if len(card.get("oracle_text", "")) > 150:
                oracle_text += "..."

            console.print(f"[bold]{i}. {name}[/bold]")
            if oracle_text:
                console.print(f"   [dim]{oracle_text}[/dim]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@combo.command()
@click.argument("card_name")
def search(card_name: str) -> None:
    """Search for existing combos containing a specific card.

    This searches the combo database for known combos that include
    the specified card.

    Examples:
        mtg combo search "Demonic Consultation"
        mtg combo search "Dramatic Reversal"
    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status(f"[cyan]Searching combos with: {card_name}...[/cyan]", spinner="dots"):
            combos = interactor.find_combos_by_card(card_name)

        if not combos:
            console.print(f"[yellow]No combos found for: {card_name}[/yellow]")
            console.print("[dim]Try using 'mtg combo find' for semantic search[/dim]")
            return

        # Display combos
        console.print(f"\n[bold cyan]🎴 Known Combos with '{card_name}':[/bold cyan]\n")

        for i, combo in enumerate(combos, 1):
            name = combo.get("name", f"Combo {i}")
            cards = combo.get("cards", [])
            description = combo.get("description", "No description")

            panel_content = f"**Cards:** {', '.join(cards)}\n\n{description}"
            console.print(Panel(Markdown(panel_content), title=f"{i}. {name}", border_style="cyan"))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@combo.command()
@click.argument("max_price", type=float)
@click.option("--limit", "-n", default=10, help="Maximum number of results")
def budget(max_price: float, limit: int) -> None:
    """Find combos under a specific price.

    Examples:
        mtg combo budget 50
        mtg combo budget 100 --limit 20
    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status(f"[cyan]Finding combos under ${max_price}...[/cyan]", spinner="dots"):
            combos = interactor.get_budget_combos(max_price=max_price)

        if not combos:
            console.print(f"[yellow]No combos found under ${max_price}[/yellow]")
            return

        # Limit results
        combos = combos[:limit]

        # Display results
        console.print(f"\n[bold cyan]🎴 Combos under ${max_price}:[/bold cyan]\n")

        for i, combo in enumerate(combos, 1):
            name = combo.get("name", f"Combo {i}")
            cards = combo.get("cards", [])
            total_price = combo.get("total_price", 0)

            console.print(f"[bold]{i}. {name}[/bold] - [green]${total_price:.2f}[/green]")
            console.print(f"   Cards: {', '.join(cards)}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@combo.command()
@click.argument("card_names", nargs=-1, required=True)
@click.option("--name", "-n", help="Name for the combo")
@click.option("--description", "-d", help="Description of how the combo works")
def create(card_names: tuple[str, ...], name: str | None, description: str | None) -> None:
    """Manually create a new combo.

    Examples:
        mtg combo create "Card A" "Card B" --name "My Combo"
        mtg combo create "Thassa's Oracle" "Demonic Consultation" --description "Win the game"
    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        card_list = list(card_names)

        if not name:
            name = f"{' + '.join(card_names[:2])} Combo"

        if not description:
            description = "No description provided"

        with console.status("[cyan]Creating combo...[/cyan]", spinner="dots"):
            result = interactor.create_combo(
                card_names=card_list,
                combo_name=name,
                description=description,
            )

        console.print(f"[green]✓[/green] Created combo: [bold]{name}[/bold]")
        console.print(f"   Cards: {', '.join(card_list)}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
