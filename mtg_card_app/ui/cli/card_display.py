"""Rich card display formatting for CLI interface.

This module provides functions to display MTG cards with detailed
information in visually appealing panels.
"""

from rich.console import Console
from rich.panel import Panel

from mtg_card_app.domain.entities import Card

# Relevance score color thresholds
HIGH_RELEVANCE_THRESHOLD = 0.8
MEDIUM_RELEVANCE_THRESHOLD = 0.6


def display_card_results(
    cards_with_scores: list[tuple[Card, float]],
    console: Console,
    title: str = "Found Cards",
) -> None:
    """Display a list of cards with relevance scores in rich panels.

    Args:
        cards_with_scores: List of (Card, relevance_score) tuples
        console: Rich console instance
        title: Title for the display section

    """
    if not cards_with_scores:
        console.print("[yellow]No cards found.[/yellow]")
        return

    # Create header
    console.print(f"\n[bold cyan]═══ {title} ═══[/bold cyan]\n")

    # Display each card
    for idx, (card, score) in enumerate(cards_with_scores, 1):
        panel = create_card_panel(card, score, idx)
        console.print(panel)
        console.print()  # Add spacing between cards


def create_card_panel(card: Card, relevance_score: float, card_number: int) -> Panel:
    """Create a rich panel displaying a single card's details.

    Args:
        card: The card to display
        relevance_score: Relevance score from RAG search
        card_number: Reference number for the card (e.g., [1], [2])

    Returns:
        Rich Panel with formatted card information

    """
    # Build panel title and content
    title = _build_card_title(card)
    content_lines = _build_card_content(card, relevance_score)
    content = "\n".join(content_lines)

    # Create panel with card number reference
    panel_title = f"[{card_number}] {title}"

    return Panel(
        content,
        title=panel_title,
        title_align="left",
        border_style="cyan",
        padding=(0, 1),
    )


def _build_card_title(card: Card) -> str:
    """Build the card title with name and mana cost."""
    title_parts = [f"[bold white]{card.name}[/bold white]"]
    if card.mana_cost:
        title_parts.append(f"[cyan]{card.mana_cost}[/cyan]")
    return " - ".join(title_parts)


def _build_card_content(card: Card, relevance_score: float) -> list[str]:
    """Build the content lines for card display."""
    content_lines = []

    # Type line
    if card.type_line:
        content_lines.append(f"[yellow]{card.type_line}[/yellow]")

    # CMC and colors
    _add_card_metadata(card, content_lines)

    # Separator
    if content_lines:
        content_lines.append("─" * 40)

    # Oracle text
    _add_oracle_text(card, content_lines)

    # Power/Toughness or Loyalty
    _add_card_stats(card, content_lines)

    # Relevance score
    _add_relevance_score(relevance_score, content_lines)

    return content_lines


def _add_card_metadata(card: Card, content_lines: list[str]) -> None:
    """Add CMC and color information to content."""
    info_parts = []
    if card.cmc is not None:
        info_parts.append(f"CMC: {card.cmc}")
    if card.colors:
        colors_str = ", ".join(card.colors)
        info_parts.append(f"Colors: {colors_str}")
    if info_parts:
        content_lines.append("[dim]" + " | ".join(info_parts) + "[/dim]")


def _add_oracle_text(card: Card, content_lines: list[str]) -> None:
    """Add oracle text with proper formatting."""
    if not card.oracle_text:
        return

    oracle_lines = card.oracle_text.split("\n")
    for line in oracle_lines:
        if line.strip():
            content_lines.append(f"[white]{line}[/white]")
        else:
            content_lines.append("")


def _add_card_stats(card: Card, content_lines: list[str]) -> None:
    """Add power/toughness or loyalty information."""
    stats = []
    if card.power and card.toughness:
        stats.append(f"[green]P/T: {card.power}/{card.toughness}[/green]")
    if card.loyalty:
        stats.append(f"[magenta]Loyalty: {card.loyalty}[/magenta]")
    if stats:
        content_lines.append("─" * 40)
        content_lines.append(" | ".join(stats))


def _add_relevance_score(relevance_score: float, content_lines: list[str]) -> None:
    """Add relevance score with color coding."""
    if relevance_score >= HIGH_RELEVANCE_THRESHOLD:
        score_color = "green"
    elif relevance_score >= MEDIUM_RELEVANCE_THRESHOLD:
        score_color = "yellow"
    else:
        score_color = "red"

    content_lines.append("")
    content_lines.append(f"[dim {score_color}]Relevance: {relevance_score:.3f}[/dim {score_color}]")


def create_card_reference_guide(num_cards: int, console: Console) -> None:
    """Display a guide showing how to reference cards in the response.

    Args:
        num_cards: Number of cards displayed
        console: Rich console instance

    """
    if num_cards == 0:
        return

    guide_text = (
        f"[dim]💡 Cards are numbered [1] through [{num_cards}] - "
        "the response will reference them by number.[/dim]"
    )
    console.print(guide_text)
    console.print()


def format_card_for_llm(card: Card, card_number: int, relevance_score: float) -> str:
    """Format a card's information for inclusion in LLM prompt.

    Args:
        card: The card to format
        card_number: Reference number for the card
        relevance_score: Relevance score from RAG search

    Returns:
        Formatted string with card details

    """
    lines = [f"[{card_number}] {card.name}"]

    # Mana cost and type
    details = []
    if card.mana_cost:
        details.append(card.mana_cost)
    if card.type_line:
        details.append(card.type_line)
    if details:
        lines.append(f"    {' - '.join(details)}")

    # CMC, colors
    meta = []
    if card.cmc is not None:
        meta.append(f"CMC: {card.cmc}")
    if card.colors:
        meta.append(f"Colors: {', '.join(card.colors)}")
    if meta:
        lines.append(f"    {' | '.join(meta)}")

    # Oracle text
    if card.oracle_text:
        lines.append(f'    "{card.oracle_text}"')

    # Power/toughness
    if card.power and card.toughness:
        lines.append(f"    P/T: {card.power}/{card.toughness}")

    # Relevance
    lines.append(f"    (Relevance: {relevance_score:.3f})")

    return "\n".join(lines)
