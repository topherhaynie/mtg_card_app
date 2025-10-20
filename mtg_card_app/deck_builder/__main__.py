"""
Deck Builder Module - Standalone entry point

This module can be run independently using:
    python -m mtg_card_app.deck_builder
    
Or using the installed script:
    mtg-deck-builder
"""

import sys
import argparse
from mtg_card_app.deck_builder import DeckBuilder


def main():
    """Main entry point for the deck builder module."""
    parser = argparse.ArgumentParser(
        description="MTG Deck Builder - Build and manage your MTG decks"
    )
    
    parser.add_argument(
        "--name",
        default="My Deck",
        help="Name of the deck to create (default: My Deck)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Create a new deck
    deck = DeckBuilder(args.name)
    
    if args.interactive:
        print(f"\nDeck Builder - Interactive Mode")
        print(f"Building deck: {args.name}")
        print("\nCommands:")
        print("  add <card_name> [quantity] - Add a card to the deck")
        print("  list - List all cards in the deck")
        print("  quit - Exit the deck builder")
        print()
        
        while True:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit":
                    print("Goodbye!")
                    break
                elif cmd == "list":
                    deck.list_cards()
                elif cmd == "add" and len(parts) >= 2:
                    card_name = " ".join(parts[1:-1]) if len(parts) > 2 and parts[-1].isdigit() else " ".join(parts[1:])
                    quantity = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 1
                    deck.add_card(card_name, quantity)
                else:
                    print("Unknown command. Try 'add', 'list', or 'quit'")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Example usage in non-interactive mode
        print(f"\nDeck Builder Module - Example Usage")
        print(f"Creating deck: {args.name}\n")
        
        # Add some example cards
        deck.add_card("Lightning Bolt", 4)
        deck.add_card("Counterspell", 4)
        deck.add_card("Island", 10)
        deck.add_card("Mountain", 10)
        
        # List the deck
        print()
        deck.list_cards()
        
        print("\n\nTo use interactive mode, run with --interactive flag:")
        print("  python -m mtg_card_app.deck_builder --interactive")
        print("  mtg-deck-builder --interactive")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
