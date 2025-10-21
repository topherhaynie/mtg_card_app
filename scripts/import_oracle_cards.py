"""Import all unique MTG cards (oracle_cards) from Scryfall bulk data.

This script downloads the Scryfall oracle_cards bulk JSON, converts each
entry into a Card entity, and stores them in the local database via
CardService. This yields one entry per unique card name (no duplicate prints),
which is a good trade-off between completeness and storage size.

Usage:
  python scripts/import_oracle_cards.py

Notes:
- Resulting data file: data/cards.json
- For full prints (all printings), consider adapting this script to use
  bulk type "default_cards". That dataset is very large and not recommended
  for JSON storage.

"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Iterable
from pathlib import Path

# Ensure project root on sys.path when running as a script
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities import Card
from mtg_card_app.interfaces.scryfall.client import ScryfallClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("import_oracle_cards")


def download_file(url: str, dest: Path) -> None:
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading bulk data to {dest} ...")
    with urllib.request.urlopen(url) as resp, open(dest, "wb") as f:
        chunk = resp.read(8192)
        total = 0
        while chunk:
            f.write(chunk)
            total += len(chunk)
            chunk = resp.read(8192)
    logger.info(f"Downloaded {total / 1_000_000:.1f} MB")


def load_cards_from_file(path: Path) -> Iterable[Card]:
    logger.info(f"Loading JSON from {path} ...")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Parsed {len(data)} card objects")
    for item in data:
        try:
            yield Card.from_scryfall(item)
        except Exception as e:  # best-effort import; log and continue
            logger.debug(f"Skipping invalid card entry: {e}")


def main() -> None:
    logger.info("=" * 80)
    logger.info("SCRYFALL BULK IMPORT: oracle_cards (unique cards)")
    logger.info("=" * 80)

    # Managers
    registry = ManagerRegistry.get_instance()
    card_service = registry.db_manager.card_service  # write via DB layer

    # Show current stats
    initial = card_service.count()
    logger.info(f"Current cards in DB: {initial}")

    # Discover bulk URL
    client = ScryfallClient()
    url = client.get_bulk_data("oracle_cards")
    logger.info(f"Bulk URL: {url}")

    # Download to local cache
    bulk_dir = Path("data/scryfall")
    bulk_path = bulk_dir / "oracle_cards.json"
    download_file(url, bulk_path)

    # Load, convert, and store
    cards = list(load_cards_from_file(bulk_path))
    logger.info(f"Converting and writing {len(cards)} cards to local DB ...")
    created = card_service.bulk_create(cards)
    logger.info(f"Upserted {created} cards")

    final = card_service.count()
    logger.info(f"Final cards in DB: {final}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
