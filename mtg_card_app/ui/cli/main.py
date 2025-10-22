"""Main CLI entry point for MTG Card App.

This module provides the primary command-line interface using Click.
Supports both conversational chat mode and direct commands.
"""

import sys

import click
from rich.console import Console

from mtg_card_app.core.dependency_manager import DependencyManager

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """🎴 MTG Card App - Your Magic: The Gathering assistant.

    Run without arguments to start interactive chat mode, or use specific commands
    for direct operations.

    Examples:
        mtg                                    # Start chat mode
        mtg search "Lightning Bolt"            # Search for cards
        mtg combo find "Isochron Scepter"      # Find combos
        mtg deck build --commander Muldrotha   # Build a deck
        mtg config show                        # Show configuration
    """
    if version:
        console.print("[bold cyan]MTG Card App[/bold cyan] version 0.1.0")
        sys.exit(0)

    # If no subcommand provided, start chat mode
    if ctx.invoked_subcommand is None:
        from .chat import start_chat

        start_chat()


@cli.command()
@click.argument("query", nargs=-1, required=False)
def chat(query: tuple[str, ...]) -> None:
    """Start interactive chat mode or ask a single question.

    Examples:
        mtg chat                           # Interactive mode
        mtg chat "show me blue counterspells"  # Single question
    """
    from .chat import start_chat

    if query:
        # Single-shot query
        question = " ".join(query)
        start_chat(single_query=question)
    else:
        # Interactive mode
        start_chat()


@cli.command()
def stats() -> None:
    """Show system statistics and service info."""
    from .commands.stats import show_stats

    show_stats()


@cli.command()
def setup() -> None:
    """Run initial setup wizard."""
    console.print("[yellow]Setup wizard not yet implemented.[/yellow]")
    console.print("Coming in Track 1 Phase 2!")


@cli.command()
def update() -> None:
    """Update card database from Scryfall."""
    console.print("[yellow]Update not yet implemented.[/yellow]")
    console.print("Coming in Track 1 Phase 2!")


# Import and register subcommands
from .commands import config as config_cmd
from .commands import search as search_cmd

cli.add_command(search_cmd.search)
cli.add_command(config_cmd.config)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
