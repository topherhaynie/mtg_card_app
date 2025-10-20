"""Main entry point for the MTG Card App.

This module serves as the main entry point when the package is run with:
    python -m mtg_card_app

It can also be invoked using the installed script:
    mtg-card-app
"""

import sys


def main():
    # """Main entry point for the MTG Card App."""
    # parser = argparse.ArgumentParser(
    #     description="MTG Card App - Find new MTG card combos",
    #     epilog="Use subcommands to access specific functionality",
    # )

    # parser.add_argument(
    #     "--version",
    #     action="version",
    #     version="mtg-card-app 0.1.0",
    # )

    # subparsers = parser.add_subparsers(
    #     dest="command",
    #     help="Available commands",
    # )

    # # Deck builder subcommand
    # deck_parser = subparsers.add_parser(
    #     "deck-builder",
    #     help="Build and manage MTG decks",
    # )

    # # Card search subcommand
    # search_parser = subparsers.add_parser(
    #     "card-search",
    #     help="Search for MTG cards",
    # )

    # # Parse known args to allow submodule args to pass through
    # args, remaining_args = parser.parse_known_args()

    # if args.command == "deck-builder":
    #     # Replace sys.argv with remaining args for the submodule
    #     import sys

    #     from mtg_card_app.deck_builder.__main__ import main as deck_main

    #     original_argv = sys.argv
    #     sys.argv = [sys.argv[0]] + remaining_args
    #     result = deck_main()
    #     sys.argv = original_argv
    #     return result
    # if args.command == "card-search":
    #     # Replace sys.argv with remaining args for the submodule
    #     import sys

    #     from mtg_card_app.card_search.__main__ import main as search_main

    #     original_argv = sys.argv
    #     sys.argv = [sys.argv[0]] + remaining_args
    #     result = search_main()
    #     sys.argv = original_argv
    #     return result
    # print("MTG Card App - An application for finding new MTG card combos")
    # print("\nAvailable modules:")
    # print("  - deck-builder: Build and manage MTG decks")
    # print("  - card-search: Search for MTG cards")
    # print("\nRun with -h for help or use a subcommand")
    # print("\nYou can also run modules directly:")
    # print("  python -m mtg_card_app.deck_builder")
    # print("  python -m mtg_card_app.card_search")
    # print("\nOr use the installed scripts:")
    # print("  mtg-deck-builder")
    # print("  mtg-card-search")
    # return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
