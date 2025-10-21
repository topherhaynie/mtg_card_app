"""Card Search CLI entry point.

Examples:
    mtg-card-search search --name "Lightning Bolt"
    mtg-card-search query --text "best blue counterspells under $5"
    mtg-card-search combos --card "Isochron Scepter" --n 3

"""

from __future__ import annotations

import argparse
import json
import sys

from mtg_card_app.core.manager_registry import ManagerRegistry


def _print_json(data: dict | list | str | float | None) -> None:
    sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Run the card search CLI."""
    parser = argparse.ArgumentParser(prog="mtg-card-search", description="Card search CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="Search for a card by name")
    p_search.add_argument("--name", required=True)

    p_query = sub.add_parser("query", help="Ask a natural language question about cards")
    p_query.add_argument("--text", required=True)

    p_combos = sub.add_parser("combos", help="Find combo pieces for a card")
    p_combos.add_argument("--card", required=True)
    p_combos.add_argument("--n", type=int, default=5)

    args = parser.parse_args(argv)
    interactor = ManagerRegistry.get_instance().interactor

    if args.cmd == "search":
        cards = interactor.search_cards(args.name)
        # Ensure JSON-serializable
        serial = [c.to_dict() if hasattr(c, "to_dict") else str(c) for c in cards]
        _print_json(serial)
        return 0

    if args.cmd == "query":
        answer = interactor.answer_natural_language_query(args.text)
        _print_json(answer)
        return 0

    if args.cmd == "combos":
        result = interactor.find_combo_pieces(args.card, args.n)
        _print_json(result)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
