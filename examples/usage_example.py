#!/usr/bin/env python3
"""
Example usage of the MTG Card App package.

This script demonstrates:
1. Importing and using the package modules
2. Running modules independently
3. Using the package's functionality programmatically
"""

from mtg_card_app.deck_builder import DeckBuilder, create_deck
from mtg_card_app.card_search import CardSearch, search_by_name, search_by_color


def example_deck_builder():
    """Example of using the deck builder module."""
    print("=" * 60)
    print("EXAMPLE 1: Deck Builder Module")
    print("=" * 60)
    
    # Create a new deck
    deck = DeckBuilder("Burn Deck")
    
    # Add cards to the deck
    deck.add_card("Lightning Bolt", 4)
    deck.add_card("Lava Spike", 4)
    deck.add_card("Mountain", 20)
    
    # List the deck contents
    deck.list_cards()
    
    print(f"\nTotal cards in deck: {deck.get_card_count()}")


def example_card_search():
    """Example of using the card search module."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Card Search Module")
    print("=" * 60)
    
    # Create a card searcher
    searcher = CardSearch()
    
    # Search by name
    print("\nSearching for cards with 'bolt' in the name:")
    results = searcher.search_by_name("bolt")
    searcher.print_results(results)
    
    # Search by color
    print("\n\nSearching for Red cards:")
    results = searcher.search_by_color("Red")
    searcher.print_results(results)
    
    # Search by type
    print("\n\nSearching for Instant cards:")
    results = searcher.search_by_type("Instant")
    searcher.print_results(results)


def example_combined_workflow():
    """Example of combining both modules."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Combined Workflow")
    print("=" * 60)
    
    # Search for cards
    print("\nStep 1: Search for Blue instant spells")
    searcher = CardSearch()
    blue_cards = searcher.search_by_color("Blue")
    instant_cards = [card for card in blue_cards if "Instant" in card["type"]]
    
    print(f"Found {len(instant_cards)} Blue instant spell(s)")
    for card in instant_cards:
        print(f"  - {card['name']}")
    
    # Build a deck with those cards
    print("\nStep 2: Build a deck with Blue control cards")
    deck = create_deck("Blue Control")
    
    for card in instant_cards:
        deck.add_card(card["name"], 4)
    
    # Add some lands
    deck.add_card("Island", 24)
    
    print()
    deck.list_cards()


def main():
    """Run all examples."""
    print("\nMTG Card App - Example Usage")
    print("This demonstrates how to use the package programmatically\n")
    
    # Run examples
    example_deck_builder()
    example_card_search()
    example_combined_workflow()
    
    # Show how to run modules independently
    print("\n" + "=" * 60)
    print("RUNNING MODULES INDEPENDENTLY")
    print("=" * 60)
    print("\nYou can run each module independently:")
    print("\n1. Using python -m:")
    print("   python -m mtg_card_app.deck_builder")
    print("   python -m mtg_card_app.card_search")
    print("\n2. Using the main package:")
    print("   python -m mtg_card_app deck-builder")
    print("   python -m mtg_card_app card-search")
    print("\n3. After installation, using entry point scripts:")
    print("   mtg-card-app")
    print("   mtg-deck-builder")
    print("   mtg-card-search")
    print("\n4. Interactive modes:")
    print("   mtg-deck-builder --interactive")
    print("   mtg-card-search --interactive")


if __name__ == "__main__":
    main()
