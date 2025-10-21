"""Deck Builder CLI entry point.

Usage examples:
    mtg-deck-builder build --format Commander \
        --commander "Edgar Markov" --pool cards.txt \
        --metadata '{"theme":"vampires"}'
    mtg-deck-builder validate --deck deck.json
    mtg-deck-builder analyze --deck deck.json
    mtg-deck-builder suggest --deck deck.json --constraints '{"budget":200}'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck


def _read_json_arg(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        msg = "Invalid JSON provided"
        raise SystemExit(msg) from exc


def _read_pool_file(path: str | None) -> list[str]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        msg = f"Card pool file not found: {path}"
        raise SystemExit(msg)
    return [line.strip() for line in p.read_text().splitlines() if line.strip()]


def _read_deck_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        msg = f"Deck file not found: {path}"
        raise SystemExit(msg)
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        msg = "Deck file is not valid JSON"
        raise SystemExit(msg) from exc


def _print_json(data: dict | list | str | float | None) -> None:
    sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Run the deck builder CLI.

    Args:
        argv: Optional argument list for testing; defaults to sys.argv

    Returns:
        Process exit code (0 on success)

    """
    parser = argparse.ArgumentParser(prog="mtg-deck-builder", description="Deck builder CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build a deck from a pool")
    p_build.add_argument("--format", required=True, dest="deck_format")
    p_build.add_argument("--pool", help="Path to newline-delimited card names")
    p_build.add_argument("--commander")
    p_build.add_argument("--constraints", help="JSON constraints", default=None)
    p_build.add_argument("--metadata", help="JSON metadata", default=None)

    p_validate = sub.add_parser("validate", help="Validate a deck JSON file")
    p_validate.add_argument("--deck", required=True, help="Path to deck.json")

    p_analyze = sub.add_parser("analyze", help="Analyze a deck JSON file")
    p_analyze.add_argument("--deck", required=True, help="Path to deck.json")

    p_suggest = sub.add_parser("suggest", help="Suggest cards for a deck JSON file")
    p_suggest.add_argument("--deck", required=True, help="Path to deck.json")
    p_suggest.add_argument(
        "--constraints",
        help=(
            "JSON constraints. Available keys: "
            "theme (str), budget (float), power (int 1-10), banned (list), "
            "n_results (int), combo_mode ('focused'/'broad'), combo_limit (int), "
            "combo_types (list), exclude_cards (list), "
            "sort_by ('power'/'price'/'popularity'/'complexity'), "
            "explain_combos (bool)"
        ),
        default=None,
    )

    p_export = sub.add_parser("export", help="Export a deck JSON file to various formats")
    p_export.add_argument("--deck", required=True, help="Path to deck.json")
    p_export.add_argument(
        "--format",
        choices=["text", "json", "moxfield", "mtgo", "arena", "archidekt"],
        default="text",
        help="Export format (default: text)",
    )
    p_export.add_argument("--output", help="Output file path (default: stdout)")

    args = parser.parse_args(argv)

    interactor = ManagerRegistry.get_instance().interactor

    if args.cmd == "build":
        card_pool = _read_pool_file(args.pool)
        constraints = _read_json_arg(args.constraints)
        metadata = _read_json_arg(args.metadata)
        deck = interactor.build_deck(
            args.deck_format,
            card_pool,
            args.commander,
            constraints,
            metadata,
        )
        _print_json(deck.to_dict() if hasattr(deck, "to_dict") else deck)
        return 0

    if args.cmd == "validate":
        deck_data = _read_deck_json(args.deck)
        result = interactor.validate_deck(Deck.from_dict(deck_data))
        _print_json(result)
        return 0

    if args.cmd == "analyze":
        deck_data = _read_deck_json(args.deck)
        result = interactor.analyze_deck(Deck.from_dict(deck_data))
        _print_json(result)
        return 0

    if args.cmd == "suggest":
        deck_data = _read_deck_json(args.deck)
        constraints = _read_json_arg(args.constraints)
        result = interactor.suggest_cards(Deck.from_dict(deck_data), constraints)
        _print_json(result)
        return 0

    if args.cmd == "export":
        deck_data = _read_deck_json(args.deck)
        result = interactor.export_deck(Deck.from_dict(deck_data), args.format)
        if args.output:
            Path(args.output).write_text(result)
            sys.stdout.write(f"Deck exported to {args.output}\n")
        else:
            sys.stdout.write(result + "\n")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
