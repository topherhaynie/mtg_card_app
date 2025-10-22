"""Card command - Display card details."""

import json

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


@click.command()
@click.argument("name")
@click.option("--format", "-f", "output_format", type=click.Choice(["rich", "json", "text"]), default="rich")
@click.option("--prices", is_flag=True, help="Show detailed pricing information")
def card(name: str, output_format: str, prices: bool) -> None:
    """Display detailed information about a specific card.

    Examples:
        mtg card "Lightning Bolt"
        mtg card "Sol Ring" --format json
        mtg card "Mana Crypt" --prices

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status(f"[cyan]Fetching card: {name}...[/cyan]", spinner="dots"):
            card_obj = interactor.fetch_card(name)

        if not card_obj:
            console.print(f"[yellow]Card not found: {name}[/yellow]")
            return

        if output_format == "json":
            _display_json(card_obj)
        elif output_format == "text":
            _display_text(card_obj, prices)
        else:  # rich
            _display_rich(card_obj, prices)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def _display_rich(card_obj, show_prices: bool = False) -> None:
    """Display card in rich format with panels and tables.

    Args:
        card_obj: Card domain object
        show_prices: Whether to show detailed pricing

    """
    # Main card info
    title = f"🎴 {card_obj.name}"
    if hasattr(card_obj, "mana_cost") and card_obj.mana_cost:
        title += f" {card_obj.mana_cost}"

    # Build card details text
    details = []

    if hasattr(card_obj, "type_line") and card_obj.type_line:
        details.append(f"**Type:** {card_obj.type_line}")

    if hasattr(card_obj, "oracle_text") and card_obj.oracle_text:
        details.append(f"\n**Text:**\n{card_obj.oracle_text}")

    if hasattr(card_obj, "power") and hasattr(card_obj, "toughness"):
        if card_obj.power is not None and card_obj.toughness is not None:
            details.append(f"\n**P/T:** {card_obj.power}/{card_obj.toughness}")

    if hasattr(card_obj, "loyalty") and card_obj.loyalty:
        details.append(f"\n**Loyalty:** {card_obj.loyalty}")

    # Price information
    if hasattr(card_obj, "price_usd") and card_obj.price_usd:
        price = f"${float(card_obj.price_usd):.2f}"
        details.append(f"\n**Price:** {price}")

    # Display main panel
    content = "\n".join(details)
    console.print(Panel(Markdown(content), title=title, border_style="cyan"))

    # Additional metadata table
    if show_prices or hasattr(card_obj, "set_name"):
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        if hasattr(card_obj, "set_name") and card_obj.set_name:
            table.add_row("Set", card_obj.set_name)

        if hasattr(card_obj, "rarity") and card_obj.rarity:
            table.add_row("Rarity", card_obj.rarity.capitalize())

        if hasattr(card_obj, "artist") and card_obj.artist:
            table.add_row("Artist", card_obj.artist)

        console.print(table)


def _display_text(card_obj, show_prices: bool = False) -> None:
    """Display card in plain text format.

    Args:
        card_obj: Card domain object
        show_prices: Whether to show detailed pricing

    """
    print(f"\n{card_obj.name}")
    print("=" * len(card_obj.name))

    if hasattr(card_obj, "mana_cost") and card_obj.mana_cost:
        print(f"Mana Cost: {card_obj.mana_cost}")

    if hasattr(card_obj, "type_line") and card_obj.type_line:
        print(f"Type: {card_obj.type_line}")

    if hasattr(card_obj, "oracle_text") and card_obj.oracle_text:
        print(f"\n{card_obj.oracle_text}")

    if hasattr(card_obj, "power") and hasattr(card_obj, "toughness"):
        if card_obj.power is not None and card_obj.toughness is not None:
            print(f"\nP/T: {card_obj.power}/{card_obj.toughness}")

    if hasattr(card_obj, "price_usd") and card_obj.price_usd:
        print(f"\nPrice: ${float(card_obj.price_usd):.2f}")

    if show_prices:
        if hasattr(card_obj, "set_name") and card_obj.set_name:
            print(f"\nSet: {card_obj.set_name}")
        if hasattr(card_obj, "rarity") and card_obj.rarity:
            print(f"Rarity: {card_obj.rarity.capitalize()}")


def _display_json(card_obj) -> None:
    """Display card in JSON format.

    Args:
        card_obj: Card domain object

    """
    # Convert card object to dict
    card_dict = {
        "name": card_obj.name,
    }

    # Add optional attributes if they exist
    for attr in [
        "mana_cost",
        "type_line",
        "oracle_text",
        "power",
        "toughness",
        "loyalty",
        "price_usd",
        "set_name",
        "rarity",
        "artist",
    ]:
        if hasattr(card_obj, attr):
            value = getattr(card_obj, attr)
            if value is not None:
                card_dict[attr] = value

    print(json.dumps(card_dict, indent=2))
