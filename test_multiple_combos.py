#!/usr/bin/env python3
"""
Test multiple famous combo types to ensure we're not overfitting to Isochron Scepter.

This tests different combo patterns:
1. Isochron Scepter + Dramatic Reversal (copy + untap loop)
2. Thassa's Oracle + Demonic Consultation (instant win condition)
3. Kiki-Jiki + Zealous Conscripts (creature copy loop)
"""

import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.core.interactor import Interactor

console = Console()
logging.basicConfig(level=logging.WARNING)

def test_combo(interactor, card_name, expected_combo_piece, combo_type):
    """Test if a combo is found and properly explained."""
    
    console.print(f"\n[bold cyan]Testing: {card_name}[/bold cyan]")
    console.print(f"[dim]Looking for: {expected_combo_piece} ({combo_type})[/dim]")
    
    result = interactor.find_combo_pieces(card_name, n_results=10, use_cache=False)
    
    # Check if combo piece is found
    found = expected_combo_piece in result
    
    # Check if properly explained
    has_infinite = "infinite" in result.lower() or "INFINITE" in result
    has_explanation = len(result) > 200  # At least some explanation
    
    return {
        "card": card_name,
        "looking_for": expected_combo_piece,
        "type": combo_type,
        "found": found,
        "has_infinite_mention": has_infinite,
        "has_explanation": has_explanation,
        "result": result
    }

def main():
    console.print("\n" + "="*80)
    console.print("[bold]Multi-Combo Generalization Test[/bold]")
    console.print("Testing if improvements work across different combo patterns")
    console.print("="*80 + "\n")
    
    # Initialize
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(
        card_data_manager=registry.card_data_manager,
        rag_manager=registry.rag_manager,
        llm_manager=registry.llm_manager,
    )
    
    # Test cases: (card_name, expected_combo_piece, combo_type)
    test_cases = [
        ("Isochron Scepter", "Dramatic Reversal", "Copy + Untap Loop"),
        ("Thassa's Oracle", "Demonic Consultation", "Instant Win Condition"),
        ("Kiki-Jiki, Mirror Breaker", "Zealous Conscripts", "Creature Copy Loop"),
    ]
    
    results = []
    for card_name, combo_piece, combo_type in test_cases:
        result = test_combo(interactor, card_name, combo_piece, combo_type)
        results.append(result)
    
    # Display results table
    console.print("\n" + "="*80)
    console.print("[bold]Test Results Summary[/bold]")
    console.print("="*80 + "\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Base Card", style="cyan")
    table.add_column("Combo Piece", style="yellow")
    table.add_column("Type", style="magenta")
    table.add_column("Found?", style="green")
    table.add_column("Infinite?", style="blue")
    table.add_column("Explained?", style="white")
    
    for r in results:
        found_emoji = "✅" if r["found"] else "❌"
        infinite_emoji = "✅" if r["has_infinite_mention"] else "❌"
        explain_emoji = "✅" if r["has_explanation"] else "❌"
        
        table.add_row(
            r["card"],
            r["looking_for"],
            r["type"],
            found_emoji,
            infinite_emoji,
            explain_emoji
        )
    
    console.print(table)
    
    # Detailed output for each combo
    console.print("\n" + "="*80)
    console.print("[bold]Detailed Analysis[/bold]")
    console.print("="*80 + "\n")
    
    for r in results:
        console.print(Panel.fit(
            f"[bold]{r['card']} → {r['looking_for']}[/bold]\n\n{r['result'][:500]}...",
            title=f"{'✅' if r['found'] else '❌'} {r['type']}",
            border_style="green" if r['found'] else "red"
        ))
    
    # Success criteria
    console.print("\n" + "="*80)
    console.print("[bold]Success Criteria[/bold]")
    console.print("="*80 + "\n")
    
    success_count = sum(1 for r in results if r["found"] and r["has_explanation"])
    total = len(results)
    success_rate = (success_count / total) * 100
    
    console.print(f"Combos Found: {success_count}/{total} ({success_rate:.0f}%)")
    console.print(f"Target: ≥2/3 (67%) for generalization")
    
    if success_rate >= 67:
        console.print("\n[bold green]✅ PASS: System generalizes across combo types![/bold green]")
    else:
        console.print("\n[bold yellow]⚠️  CAUTION: May be overfitting to specific combo patterns[/bold yellow]")
    
    console.print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
