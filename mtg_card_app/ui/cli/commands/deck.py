"""Deck building and analysis commands."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


@click.group()
def deck() -> None:
    """Build, analyze, and manage MTG decks.

    Examples:
        mtg deck new commander --commander "Muldrotha"
        mtg deck validate my_deck.txt
        mtg deck suggest my_deck.txt --theme "graveyard"

    """


@deck.command()
@click.argument(
    "deck_format", type=click.Choice(["standard", "modern", "commander", "legacy", "vintage", "pioneer", "pauper"])
)
@click.option("--commander", "-c", help="Commander card name (for Commander format)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def new(deck_format: str, commander: str | None, output: str | None) -> None:
    """Create a new deck.

    Examples:
        mtg deck new commander --commander "Muldrotha, the Gravetide"
        mtg deck new modern --output my_modern.txt
        mtg deck new standard

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        if deck_format == "commander" and not commander:
            console.print("[yellow]Warning:[/yellow] Commander format typically requires a commander card")
            console.print("[dim]Use --commander flag to specify one[/dim]")

        with console.status("[cyan]Creating new deck...[/cyan]", spinner="dots"):
            deck_data = interactor.create_new_deck(
                deck_format=deck_format,
                commander=commander,
            )

        # Display summary
        console.print(f"\n[green]✓[/green] Created new [bold]{deck_format}[/bold] deck")
        if commander:
            console.print(f"   Commander: [bold]{commander}[/bold]")

        # Save if output specified
        if output:
            output_path = Path(output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(deck_data, f, indent=2)
            console.print(f"   Saved to: {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@deck.command()
@click.argument("deck_file", type=click.Path(exists=True))
def validate(deck_file: str) -> None:
    """Validate a deck for format legality.

    Examples:
        mtg deck validate my_deck.txt
        mtg deck validate commander_deck.json

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        # Load deck
        deck_path = Path(deck_file)
        with open(deck_path, encoding="utf-8") as f:
            if deck_path.suffix == ".json":
                deck_data = json.load(f)
            else:
                # Parse text format
                deck_data = {"cards": f.read().strip().split("\n")}

        with console.status(f"[cyan]Validating deck: {deck_file}...[/cyan]", spinner="dots"):
            validation = interactor.validate_deck(deck_data)

        # Display results
        is_legal = validation.get("is_legal", False)
        issues = validation.get("issues", [])

        if is_legal:
            console.print(f"\n[green]✓[/green] Deck is legal for {validation.get('format', 'Unknown')} format")
        else:
            console.print("\n[red]✗[/red] Deck has validation issues:\n")
            for i, issue in enumerate(issues, 1):
                console.print(f"  {i}. {issue}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@deck.command()
@click.argument("deck_file", type=click.Path(exists=True))
@click.option("--format", "-f", "output_format", type=click.Choice(["rich", "markdown", "json"]), default="rich")
def analyze(deck_file: str, output_format: str) -> None:
    """Analyze deck statistics and mana curve.

    Examples:
        mtg deck analyze my_deck.txt
        mtg deck analyze commander.json --format markdown
        mtg deck analyze modern.txt --format json

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        # Load deck
        deck_path = Path(deck_file)
        with open(deck_path, encoding="utf-8") as f:
            if deck_path.suffix == ".json":
                deck_data = json.load(f)
            else:
                deck_data = {"cards": f.read().strip().split("\n")}

        with console.status(f"[cyan]Analyzing deck: {deck_file}...[/cyan]", spinner="dots"):
            analysis = interactor.analyze_deck(deck_data)

        # Display based on format
        if output_format == "json":
            print(json.dumps(analysis, indent=2))
        elif output_format == "markdown":
            md_text = _format_analysis_markdown(analysis)
            console.print(Markdown(md_text))
        else:
            _display_analysis_rich(analysis)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@deck.command()
@click.argument("deck_file", type=click.Path(exists=True))
@click.option("--theme", "-t", help="Deck theme or strategy")
@click.option("--budget", "-b", type=float, help="Maximum budget for suggestions")
@click.option("--combo-mode", type=click.Choice(["none", "focused", "mixed"]), default="mixed")
def suggest(deck_file: str, theme: str | None, budget: float | None, combo_mode: str) -> None:
    """Get AI-powered deck suggestions.

    Examples:
        mtg deck suggest my_deck.txt --theme "graveyard recursion"
        mtg deck suggest commander.txt --budget 200 --combo-mode focused
        mtg deck suggest modern.txt --theme "control"

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        # Load deck
        deck_path = Path(deck_file)
        with open(deck_path, encoding="utf-8") as f:
            if deck_path.suffix == ".json":
                deck_data = json.load(f)
            else:
                deck_data = {"cards": f.read().strip().split("\n")}

        with console.status("[cyan]Generating suggestions...[/cyan]", spinner="dots"):
            suggestions = interactor.suggest_deck_improvements(
                deck_data=deck_data,
                theme=theme,
                max_budget=budget,
                combo_mode=combo_mode,
            )

        # Display suggestions
        console.print("\n[bold cyan]🎴 Deck Suggestions:[/bold cyan]\n")

        for i, suggestion in enumerate(suggestions, 1):
            card_name = suggestion.get("card_name", "Unknown")
            reason = suggestion.get("reason", "")
            price = suggestion.get("price")

            title = f"{i}. {card_name}"
            if price is not None:
                title += f" - [green]${price:.2f}[/green]"

            console.print(Panel(reason, title=title, border_style="cyan"))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@deck.command()
@click.argument("deck_file", type=click.Path(exists=True))
@click.argument("export_format", type=click.Choice(["txt", "json", "mtgo", "arena", "markdown"]))
@click.option("--output", "-o", type=click.Path(), help="Output file (default: same name, new extension)")
def export(deck_file: str, export_format: str, output: str | None) -> None:
    """Export deck to various formats.

    Examples:
        mtg deck export my_deck.json txt
        mtg deck export commander.txt arena --output arena_import.txt
        mtg deck export modern.txt mtgo

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        # Load deck
        deck_path = Path(deck_file)
        with open(deck_path, encoding="utf-8") as f:
            if deck_path.suffix == ".json":
                deck_data = json.load(f)
            else:
                deck_data = {"cards": f.read().strip().split("\n")}

        with console.status(f"[cyan]Exporting to {export_format}...[/cyan]", spinner="dots"):
            exported_content = interactor.export_deck(deck_data, export_format)

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = deck_path.with_suffix(f".{export_format}")

        # Write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(exported_content)

        console.print(f"[green]✓[/green] Exported deck to: {output_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@deck.command()
@click.argument("deck_file", type=click.Path())
@click.option(
    "--format",
    "-f",
    "deck_format",
    type=click.Choice(["standard", "modern", "commander", "legacy", "vintage", "pioneer", "pauper"]),
    required=True,
)
@click.option("--budget", "-b", type=float, help="Maximum budget")
@click.option("--theme", "-t", help="Deck theme or strategy")
def build(deck_file: str, deck_format: str, budget: float | None, theme: str | None) -> None:
    """Build a deck from scratch using AI.

    Examples:
        mtg deck build my_new_deck.txt --format commander --theme "sacrifice"
        mtg deck build budget_modern.txt --format modern --budget 100
        mtg deck build control.txt --format standard --theme "control"

    """
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )

    try:
        with console.status("[cyan]Building deck with AI...[/cyan]", spinner="dots"):
            deck_data = interactor.build_deck(
                deck_format=deck_format,
                theme=theme,
                max_budget=budget,
            )

        # Save deck
        deck_path = Path(deck_file)
        with open(deck_path, "w", encoding="utf-8") as f:
            json.dump(deck_data, f, indent=2)

        # Display summary
        total_cards = len(deck_data.get("cards", []))
        console.print(f"\n[green]✓[/green] Built {deck_format} deck with {total_cards} cards")
        if theme:
            console.print(f"   Theme: {theme}")
        if budget:
            console.print(f"   Budget: ${budget:.2f}")
        console.print(f"   Saved to: {deck_path}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def _display_analysis_rich(analysis: dict) -> None:
    """Display deck analysis in rich format."""
    console.print("\n[bold cyan]📊 Deck Analysis:[/bold cyan]\n")

    # Basic stats
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="bold")

    stats_table.add_row("Total Cards", str(analysis.get("total_cards", 0)))
    stats_table.add_row("Creatures", str(analysis.get("creatures", 0)))
    stats_table.add_row("Spells", str(analysis.get("spells", 0)))
    stats_table.add_row("Lands", str(analysis.get("lands", 0)))
    stats_table.add_row("Avg CMC", f"{analysis.get('avg_cmc', 0):.2f}")

    console.print(Panel(stats_table, title="Deck Statistics", border_style="cyan"))

    # Mana curve
    mana_curve = analysis.get("mana_curve", {})
    if mana_curve:
        console.print("\n[bold]Mana Curve:[/bold]")
        for cmc, count in sorted(mana_curve.items()):
            bar = "█" * count
            console.print(f"  {cmc}: {bar} ({count})")


def _format_analysis_markdown(analysis: dict) -> str:
    """Format deck analysis as markdown."""
    lines = ["# Deck Analysis\n"]

    lines.append("## Statistics\n")
    lines.append(f"- **Total Cards:** {analysis.get('total_cards', 0)}")
    lines.append(f"- **Creatures:** {analysis.get('creatures', 0)}")
    lines.append(f"- **Spells:** {analysis.get('spells', 0)}")
    lines.append(f"- **Lands:** {analysis.get('lands', 0)}")
    lines.append(f"- **Average CMC:** {analysis.get('avg_cmc', 0):.2f}\n")

    mana_curve = analysis.get("mana_curve", {})
    if mana_curve:
        lines.append("## Mana Curve\n")
        for cmc, count in sorted(mana_curve.items()):
            lines.append(f"- **{cmc}:** {count}")

    return "\n".join(lines)
