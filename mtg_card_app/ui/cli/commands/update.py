"""Update command - Download latest card data from Scryfall."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from mtg_card_app.config import get_config
from mtg_card_app.core.manager_registry import ManagerRegistry

console = Console()


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force re-download even if data exists")
@click.option("--cards-only", is_flag=True, help="Only update card database (skip embeddings)")
@click.option("--embeddings-only", is_flag=True, help="Only regenerate embeddings (skip card download)")
def update(force: bool, cards_only: bool, embeddings_only: bool) -> None:
    """Update card database from Scryfall.

    Downloads the latest Oracle card data from Scryfall's bulk data API
    and optionally regenerates vector embeddings for semantic search.

    Examples:
        mtg update                    # Full update (cards + embeddings)
        mtg update --force            # Force re-download
        mtg update --cards-only       # Skip embedding generation
        mtg update --embeddings-only  # Only regenerate embeddings

    """
    console.print(Panel.fit(
        "[bold cyan]📥 MTG Card App - Data Update[/bold cyan]\n\n"
        "This will download the latest card data from Scryfall.",
        border_style="cyan",
    ))

    # Validate options
    if cards_only and embeddings_only:
        console.print("[red]Error:[/red] Cannot use --cards-only and --embeddings-only together")
        return

    # Get configuration
    config = get_config()
    data_dir = Path(config.get("data.directory", "data"))
    data_dir.mkdir(exist_ok=True, parents=True)

    # Update cards
    if not embeddings_only:
        _update_cards(data_dir, force)

    # Update embeddings
    if not cards_only:
        _update_embeddings(force)

    # Final summary
    console.print(Panel.fit(
        "[green]✓[/green] Update complete!\n\n"
        "Your card database is up to date.\n\n"
        "[bold]Next steps:[/bold]\n"
        "  mtg stats              # View updated statistics\n"
        "  mtg search \"blue\"      # Try searching cards\n"
        "  mtg                    # Start chat mode",
        border_style="green",
        title="🎉 Success",
    ))


def _update_cards(data_dir: Path, force: bool) -> None:
    """Download and import card data from Scryfall."""
    console.print("\n[bold cyan]📦 Step 1: Card Database Update[/bold cyan]")

    cards_db = data_dir / "cards.db"

    # Check if already exists
    if cards_db.exists() and not force:
        console.print("[yellow]⚠[/yellow] Card database already exists")
        if not click.confirm("Re-download and replace?", default=False):
            console.print("[dim]Skipping card download[/dim]")
            return

    try:
        # Import the script functionality
        from scripts.import_oracle_cards import main as import_cards

        console.print("Downloading Oracle card data from Scryfall...")
        console.print("[dim]This may take 2-5 minutes for ~35,000 cards[/dim]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Importing cards...", total=None)

            # Run the import
            import_cards()

            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Card database updated: {cards_db}")

        # Show stats
        registry = ManagerRegistry.get_instance()
        card_data_manager = registry.card_data_manager
        total_cards = len(card_data_manager.get_all_cards())
        console.print(f"  Total cards: [bold]{total_cards:,}[/bold]")

    except Exception as e:
        console.print(f"[red]✗ Failed to update cards:[/red] {e}")
        console.print("\n[bold]Troubleshooting:[/bold]")
        console.print("• Check your internet connection")
        console.print("• Verify Scryfall is accessible: https://scryfall.com")
        console.print("• Try again with --force flag")
        raise click.Abort()


def _update_embeddings(force: bool) -> None:
    """Generate vector embeddings for semantic search."""
    console.print("\n[bold cyan]🧠 Step 2: Vector Embeddings[/bold cyan]")

    try:
        registry = ManagerRegistry.get_instance()
        rag_manager = registry.rag_manager

        # Check if embeddings exist
        stats = rag_manager.get_stats()
        current_count = stats.get("total_documents", 0)

        if current_count > 0 and not force:
            console.print(f"[yellow]⚠[/yellow] Embeddings already exist ({current_count:,} cards)")
            if not click.confirm("Regenerate embeddings?", default=False):
                console.print("[dim]Skipping embedding generation[/dim]")
                return

        console.print("Generating vector embeddings for semantic search...")
        console.print("[dim]This may take 5-15 minutes depending on your hardware[/dim]\n")

        # Get all cards
        card_data_manager = registry.card_data_manager
        all_cards = card_data_manager.get_all_cards()
        total_cards = len(all_cards)

        console.print(f"Processing [bold]{total_cards:,}[/bold] cards...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Vectorizing 0/{total_cards} cards...", total=total_cards)

            # Batch process cards
            batch_size = 100
            for i in range(0, total_cards, batch_size):
                batch = all_cards[i:i + batch_size]

                # Add to RAG (will embed and store)
                for card in batch:
                    rag_manager.add_card(card)

                progress.update(task, completed=min(i + batch_size, total_cards),
                               description=f"Vectorizing {min(i + batch_size, total_cards)}/{total_cards} cards...")

        # Verify
        stats = rag_manager.get_stats()
        final_count = stats.get("total_documents", 0)

        console.print(f"[green]✓[/green] Vector embeddings generated")
        console.print(f"  Total vectors: [bold]{final_count:,}[/bold]")

    except Exception as e:
        console.print(f"[red]✗ Failed to generate embeddings:[/red] {e}")
        console.print("\n[bold]Troubleshooting:[/bold]")
        console.print("• Ensure card database is populated first")
        console.print("• Check available disk space")
        console.print("• Try with smaller batches if memory issues occur")
        raise click.Abort()
