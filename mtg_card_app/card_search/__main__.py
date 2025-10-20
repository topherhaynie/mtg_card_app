"""
Card Search Module - Standalone entry point

This module can be run independently using:
    python -m mtg_card_app.card_search
    
Or using the installed script:
    mtg-card-search
"""

import sys
import argparse
from mtg_card_app.card_search import CardSearch


def main():
    """Main entry point for the card search module."""
    parser = argparse.ArgumentParser(
        description="MTG Card Search - Search for MTG cards"
    )
    
    parser.add_argument(
        "--name",
        help="Search for cards by name"
    )
    
    parser.add_argument(
        "--color",
        help="Search for cards by color (e.g., Red, Blue, Green)"
    )
    
    parser.add_argument(
        "--type",
        help="Search for cards by type (e.g., Instant, Creature, Land)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    searcher = CardSearch()
    
    if args.interactive:
        print("\nCard Search - Interactive Mode")
        print("\nCommands:")
        print("  name <query> - Search by card name")
        print("  color <color> - Search by color")
        print("  type <type> - Search by card type")
        print("  quit - Exit the search tool")
        print()
        
        while True:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                
                if cmd == "quit":
                    print("Goodbye!")
                    break
                elif cmd == "name" and len(parts) == 2:
                    results = searcher.search_by_name(parts[1])
                    searcher.print_results(results)
                elif cmd == "color" and len(parts) == 2:
                    results = searcher.search_by_color(parts[1])
                    searcher.print_results(results)
                elif cmd == "type" and len(parts) == 2:
                    results = searcher.search_by_type(parts[1])
                    searcher.print_results(results)
                else:
                    print("Unknown command. Try 'name', 'color', 'type', or 'quit'")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Command-line search mode
        found_results = False
        
        if args.name:
            results = searcher.search_by_name(args.name)
            print(f"\nSearching for cards with name containing '{args.name}':")
            searcher.print_results(results)
            found_results = True
        
        if args.color:
            results = searcher.search_by_color(args.color)
            print(f"\nSearching for {args.color} cards:")
            searcher.print_results(results)
            found_results = True
        
        if args.type:
            results = searcher.search_by_type(args.type)
            print(f"\nSearching for {args.type} cards:")
            searcher.print_results(results)
            found_results = True
        
        if not found_results:
            # Example usage
            print("\nCard Search Module - Example Usage\n")
            print("Searching for 'bolt':")
            results = searcher.search_by_name("bolt")
            searcher.print_results(results)
            
            print("\n\nSearching for Blue cards:")
            results = searcher.search_by_color("Blue")
            searcher.print_results(results)
            
            print("\n\nTo search cards, use:")
            print("  python -m mtg_card_app.card_search --name 'Lightning'")
            print("  python -m mtg_card_app.card_search --color Red")
            print("  python -m mtg_card_app.card_search --type Instant")
            print("\nOr use interactive mode:")
            print("  python -m mtg_card_app.card_search --interactive")
            print("  mtg-card-search --interactive")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
