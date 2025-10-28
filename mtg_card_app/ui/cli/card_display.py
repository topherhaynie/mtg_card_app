"""Rich card display formatting for CLI interface.

This module provides functions to display MTG cards with detailed
information in visually appealing panels w                           else:
                formatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")
        # Generic mana (numbers) - show as dim white number
        elif symbol.isdigit():
            formatted_parts.append(f"[dim white]{symbol}[/dim white]")
        # X costs or other variables
        elif symbol.upper() in ["X", "Y", "Z"]:
            formatted_parts.append(f"[bold magenta]{symbol}[/bold magenta]")
        # Unknown/special symbols - keep as-is with color
        else:
            formatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")ormatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")
        # Generic mana (numbers) - show as dim white number
        elif symbol.isdigit():
            formatted_parts.append(f"[dim white]{symbol}[/dim white]")
        # X costs or other variables
        elif symbol.upper() in ["X", "Y", "Z"]:
            formatted_parts.append(f"[bold magenta]{symbol}[/bold magenta]")
        # Unknown/special symbols - keep as-is with colorneric mana (numbers) - show as dim white number
        elif symbol.isdigit():
            formatted_parts.append(f"[dim white]{symbol}[/dim white]")
        # X costs or other variables
        elif symbol.upper() in ["X", "Y", "Z"]:
            formatted_parts.append(f"[bold magenta]{symbol}[/bold magenta]")eneric mana (numbers) - show as dim white number
        elif symbol.isdigit():
            formatted_parts.append(f"[dim white]{symbol}[/dim white]")
        # X costs or other variables
        elif symbol.upper() in ["X", "Y", "Z"]:
            formatted_parts.append(f"[bold magenta]{symbol}[/bold magenta]")proved UX.
"""

import re

from rich.console import Console
from rich.panel import Panel

from mtg_card_app.domain.entities import Card

# Relevance score thresholds for star ratings
EXCELLENT_THRESHOLD = 0.8  # ⭐⭐⭐⭐⭐
GREAT_THRESHOLD = 0.6      # ⭐⭐⭐⭐
GOOD_THRESHOLD = 0.4       # ⭐⭐⭐
FAIR_THRESHOLD = 0.2       # ⭐⭐
# Below 0.2                # ⭐

# Mana symbol color mapping for Rich markup
MANA_COLORS = {
    "W": "white",
    "U": "blue",
    "B": "dim white",  # Black text on black background doesn't work well
    "R": "red",
    "G": "green",
    "C": "dim white",  # Colorless
}

# Color abbreviation to full name mapping
COLOR_NAMES = {
    "W": "White",
    "U": "Blue",
    "B": "Black",
    "R": "Red",
    "G": "Green",
}

# Mana symbol to emoji/symbol mapping for better readability
MANA_SYMBOLS = {
    "W": "⚪",  # White circle
    "U": "🔵",  # Blue circle
    "B": "⚫",  # Black circle
    "R": "🔴",  # Red circle
    "G": "🟢",  # Green circle
    "C": "◆",   # Colorless diamond (bold)
    "S": "❄️",  # Snow mana
}


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
    """Build the card title with name and colored mana cost."""
    title_parts = [f"[bold white]{card.name}[/bold white]"]
    if card.mana_cost:
        # Format mana symbols with colors
        formatted_mana = _format_mana_cost(card.mana_cost)
        title_parts.append(formatted_mana)
    return " - ".join(title_parts)


def _format_mana_cost(mana_cost: str) -> str:
    """Format mana cost with colored emoji symbols.

    Converts {2}{U}{U} to "2🔵🔵" - visual symbols only.

    Args:
        mana_cost: Raw mana cost string like "{2}{U}{U}"

    Returns:
        Formatted string with emoji symbols (no text explanation)

    """
    # Split by {} to get individual symbols
    symbols = re.findall(r"\{([^}]+)\}", mana_cost)

    formatted_parts = []

    for symbol in symbols:
        # Check if it's a colored mana symbol
        if symbol in MANA_SYMBOLS:
            emoji = MANA_SYMBOLS[symbol]
            color = MANA_COLORS[symbol]
            formatted_parts.append(f"[bold {color}]{emoji}[/bold {color}]")
        # Handle hybrid mana like {W/U}
        elif "/" in symbol and "P" not in symbol and "p" not in symbol:
            parts = symbol.split("/")
            if parts[0] in MANA_SYMBOLS and parts[1] in MANA_SYMBOLS:
                emoji1 = MANA_SYMBOLS[parts[0]]
                emoji2 = MANA_SYMBOLS[parts[1]]
                color1 = MANA_COLORS[parts[0]]
                formatted_parts.append(f"[{color1}]{emoji1}/{emoji2}[/{color1}]")
            else:
                # Fallback for unknown hybrid
                formatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")
        # Handle Phyrexian mana like {W/P}
        elif "P" in symbol or "p" in symbol:
            base_color = symbol.replace("/P", "").replace("/p", "")
            if base_color in MANA_SYMBOLS:
                emoji = MANA_SYMBOLS[base_color]
                color = MANA_COLORS[base_color]
                formatted_parts.append(f"[{color}]{emoji}Φ[/{color}]")
            else:
                formatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")
        # Generic mana (numbers) - show as dim number + dim grey circle
        elif symbol.isdigit():
            formatted_parts.append(f"[dim white]{symbol}⚪[/dim white]")
        # X costs or other variables
        elif symbol.upper() in ["X", "Y", "Z"]:
            formatted_parts.append(f"[bold magenta]{symbol}⚪[/bold magenta]")
        # Unknown/special symbols - keep as-is with color
        else:
            formatted_parts.append(f"[cyan]{{{symbol}}}[/cyan]")

    return "".join(formatted_parts)


def _format_mana_cost_breakdown(mana_cost: str) -> str:
    """Format mana cost as text breakdown (backup for emoji display).
    
    Converts {2}{U}{U} to "2 Generic, 2 Blue" with colored text.
    
    Args:
        mana_cost: Raw mana cost string like "{2}{U}{U}"
    
    Returns:
        Formatted breakdown with colored text (no emojis)
    
    """
    # Split by {} to get individual symbols
    symbols = re.findall(r"\{([^}]+)\}", mana_cost)
    
    # Count occurrences of each type
    generic_count = 0
    color_counts = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0}
    colorless_count = 0
    x_count = 0
    special = []
    
    for symbol in symbols:
        if symbol.isdigit():
            generic_count += int(symbol)
        elif symbol == "C":
            colorless_count += 1
        elif symbol in color_counts:
            color_counts[symbol] += 1
        elif symbol.upper() in ["X", "Y", "Z"]:
            x_count += 1
        else:
            special.append(symbol)
    
    # Build breakdown
    parts = []
    
    if generic_count > 0:
        parts.append(f"[dim white]{generic_count} Generic[/dim white]")
    
    if colorless_count > 0:
        parts.append(f"[dim white]{colorless_count} Colorless[/dim white]")
    
    if x_count > 0:
        parts.append(f"[bold magenta]{x_count} Variable[/bold magenta]")
    
    # Add colored mana
    color_names = {
        "W": ("White", "white"),
        "U": ("Blue", "blue"),
        "B": ("Black", "dim white"),
        "R": ("Red", "red"),
        "G": ("Green", "green"),
    }
    
    for color_abbr, count in color_counts.items():
        if count > 0:
            name, style = color_names[color_abbr]
            parts.append(f"[{style}]{count} {name}[/{style}]")
    
    # Add special symbols
    for spec in special:
        parts.append(f"[cyan]{spec}[/cyan]")
    
    return ", ".join(parts) if parts else "[dim]No cost[/dim]"


def _build_card_content(card: Card, relevance_score: float) -> list[str]:
    """Build the content lines for card display."""
    content_lines = []

    # Type line with label
    if card.type_line:
        content_lines.append(f"[dim]Type:[/dim] [yellow]{card.type_line}[/yellow]")

    # CMC
    if card.cmc is not None:
        cmc_display = int(card.cmc) if card.cmc == int(card.cmc) else card.cmc
        content_lines.append(f"[dim]Mana Value:[/dim] [cyan]{cmc_display}[/cyan]")

    # Mana cost breakdown (colored text, no emojis - backup if symbols don't render)
    if card.mana_cost:
        cost_breakdown = _format_mana_cost_breakdown(card.mana_cost)
        content_lines.append(f"[dim]Cost:[/dim] {cost_breakdown}")

    # Oracle text section
    if card.oracle_text:
        content_lines.append("")  # Blank line for spacing
        content_lines.append("[dim]─── Card Text ───[/dim]")
        _add_oracle_text(card, content_lines)

    # Power/Toughness or Loyalty with emoji
    _add_card_stats(card, content_lines)

    # Scryfall link
    _add_scryfall_link(card, content_lines)

    # Relevance score with star rating
    _add_relevance_score(relevance_score, content_lines)

    return content_lines


def _format_color_names(colors_str: str) -> str:
    """Format color abbreviations with emoji, colors, and full names.

    Args:
        colors_str: Comma-separated color abbreviations (e.g., "W, U, B")

    Returns:
        Formatted string with emojis and color names (e.g., "⚪ White, 🔵 Blue")

    """
    color_display = {
        "W": "[white]⚪ White[/white]",
        "U": "[blue]🔵 Blue[/blue]",
        "B": "[dim white]⚫ Black[/dim white]",
        "R": "[red]🔴 Red[/red]",
        "G": "[green]🟢 Green[/green]",
    }

    formatted_colors = []
    for color in colors_str.split(", "):
        formatted_colors.append(color_display.get(color.strip(), color))

    return ", ".join(formatted_colors)


def _add_oracle_text(card: Card, content_lines: list[str]) -> None:
    """Add oracle text with proper formatting and mana symbol conversion."""
    if not card.oracle_text:
        return

    oracle_lines = card.oracle_text.split("\n")
    for line in oracle_lines:
        if line.strip():
            # Convert mana symbols in text to emojis
            formatted_line = _convert_mana_symbols_in_text(line)
            content_lines.append(f"[white]{formatted_line}[/white]")
        else:
            content_lines.append("")


def _convert_mana_symbols_in_text(text: str) -> str:
    """Convert mana symbols like {T}, {2}, {U} to emoji format in card text.
    
    Args:
        text: Text containing mana symbols
    
    Returns:
        Text with mana symbols converted to emojis
    
    """
    # Find all {X} patterns
    def replace_symbol(match):
        symbol = match.group(1)
        
        # Tap symbol
        if symbol == "T" or symbol == "t":
            return "⟳"
        
        # Untap symbol  
        if symbol == "Q" or symbol == "q":
            return "⟲"
        
        # Energy symbol
        if symbol == "E" or symbol == "e":
            return "⚡"
        
        # Colored mana
        if symbol in MANA_SYMBOLS:
            emoji = MANA_SYMBOLS[symbol]
            return emoji
        
        # Generic mana (numbers)
        if symbol.isdigit():
            return f"[dim white]{symbol}⚪[/dim white]"
        
        # X costs
        if symbol.upper() in ["X", "Y", "Z"]:
            return f"[bold magenta]{symbol}⚪[/bold magenta]"
        
        # Hybrid mana
        if "/" in symbol and "P" not in symbol:
            parts = symbol.split("/")
            if len(parts) == 2 and parts[0] in MANA_SYMBOLS and parts[1] in MANA_SYMBOLS:
                emoji1 = MANA_SYMBOLS[parts[0]]
                emoji2 = MANA_SYMBOLS[parts[1]]
                return f"{emoji1}/{emoji2}"
        
        # Phyrexian mana
        if "P" in symbol or "p" in symbol:
            base = symbol.replace("/P", "").replace("/p", "")
            if base in MANA_SYMBOLS:
                return f"{MANA_SYMBOLS[base]}Φ"
        
        # Keep unknown symbols as-is
        return f"{{{symbol}}}"
    
    return re.sub(r"\{([^}]+)\}", replace_symbol, text)


def _add_card_stats(card: Card, content_lines: list[str]) -> None:
    """Add power/toughness or loyalty information with emoji."""
    stats = []
    if card.power and card.toughness:
        stats.append(f"⚔️  [green]{card.power}/{card.toughness}[/green]")
    if card.loyalty:
        stats.append(f"🛡️  [magenta]{card.loyalty}[/magenta]")
    if stats:
        content_lines.append("")  # Blank line for spacing
        content_lines.append(" | ".join(stats))


def _add_scryfall_link(card: Card, content_lines: list[str]) -> None:
    """Add Scryfall image link for the card.

    Args:
        card: The card to link to
        content_lines: List of content lines to append to

    """
    # Generate Scryfall URL from card name
    # Scryfall uses URL-encoded card names
    card_name_encoded = card.name.replace(" ", "+").replace("'", "").replace(",", "")
    scryfall_url = f"https://scryfall.com/search?q=!%22{card_name_encoded}%22"

    content_lines.append("")  # Blank line for spacing
    content_lines.append(f"[dim]🔗 View card:[/dim] [link={scryfall_url}]{scryfall_url}[/link]")


def _add_relevance_score(relevance_score: float, content_lines: list[str]) -> None:
    """Add relevance score with star rating and color coding.

    Args:
        relevance_score: Relevance score from RAG (typically -1.0 to 1.0)
        content_lines: List of content lines to append to

    """
    # Convert to percentage for easier understanding
    percentage = int(max(0, min(100, (relevance_score + 1) * 50)))

    # Determine star rating and color
    if relevance_score >= EXCELLENT_THRESHOLD:
        stars = "⭐⭐⭐⭐⭐"
        score_color = "green"
        quality = "Excellent"
    elif relevance_score >= GREAT_THRESHOLD:
        stars = "⭐⭐⭐⭐⚝"
        score_color = "green"
        quality = "Great"
    elif relevance_score >= GOOD_THRESHOLD:
        stars = "⭐⭐⭐⚝⚝"
        score_color = "yellow"
        quality = "Good"
    elif relevance_score >= FAIR_THRESHOLD:
        stars = "⭐⭐⚝⚝⚝"
        score_color = "yellow"
        quality = "Fair"
    else:
        stars = "⭐⚝⚝⚝⚝"
        score_color = "red"
        quality = "Weak"

    content_lines.append("")  # Blank line for spacing
    content_lines.append(
        f"[dim]🎯 Match Quality:[/dim] [{score_color}]{quality} {stars}[/{score_color}] "
        f"[dim]({percentage}%)[/dim]"
    )


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
