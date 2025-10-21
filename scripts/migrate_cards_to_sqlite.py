#!/usr/bin/env python3
"""Migrate card data from JSON to SQLite.

This script migrates existing card data from data/cards.json to data/cards.db
using the new SQLite-based storage for better performance with 30k+ cards.
"""

import json
import logging
import sys
from pathlib import Path

# Ensure project root on sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.domain.entities import Card
from mtg_card_app.managers.db.services.card_sqlite_service import CardSqliteService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("migrate_cards_to_sqlite")


def migrate_json_to_sqlite(
    json_path: str = "data/cards.json",
    db_path: str = "data/cards.db",
):
    """Migrate cards from JSON to SQLite.

    Args:
        json_path: Path to source JSON file
        db_path: Path to target SQLite database

    """
    json_file = Path(json_path)
    db_file = Path(db_path)

    print("=" * 70)
    print("CARD DATA MIGRATION: JSON → SQLite")
    print("=" * 70)

    # Check if JSON file exists
    if not json_file.exists():
        logger.warning(f"JSON file not found: {json_path}")
        logger.info("Nothing to migrate. Database will be created when cards are added.")
        return

    # Load JSON data
    logger.info(f"Loading cards from {json_path}...")
    try:
        with open(json_file) as f:
            data = json.load(f)
            cards_data = data.get("cards", {})
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        sys.exit(1)

    card_count = len(cards_data)
    logger.info(f"Found {card_count} cards in JSON")

    if card_count == 0:
        logger.info("No cards to migrate")
        return

    # Check if database already exists
    if db_file.exists():
        response = input(f"\nDatabase {db_path} already exists. Overwrite? (y/n): ")
        if response.lower() != "y":
            logger.info("Migration cancelled")
            return
        db_file.unlink()
        logger.info(f"Deleted existing database: {db_path}")

    # Initialize SQLite service
    logger.info(f"Creating SQLite database at {db_path}...")
    sqlite_service = CardSqliteService(db_path=db_path)

    # Migrate cards
    logger.info("Migrating cards...")
    cards = []

    for card_id, card_data in cards_data.items():
        try:
            card = Card(**card_data)
            cards.append(card)
        except Exception as e:
            logger.warning(f"Failed to parse card {card_id}: {e}")

    # Bulk insert
    logger.info(f"Inserting {len(cards)} cards into SQLite...")
    inserted = sqlite_service.bulk_create(cards)

    # Verify
    total_in_db = sqlite_service.count()

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print(f"Total cards in JSON:  {card_count}")
    print(f"Cards migrated:       {inserted}")
    print(f"Cards in database:    {total_in_db}")
    print(f"Skipped (duplicates): {len(cards) - inserted}")
    print("=" * 70)

    # Backup original JSON
    if inserted > 0:
        backup_path = json_file.with_suffix(".json.bak")
        logger.info(f"\nBacking up original JSON to {backup_path}")
        import shutil

        shutil.copy(json_file, backup_path)

    print("\n✅ Migration successful!")
    print(f"\nOld: {json_path} (backed up to {backup_path})")
    print(f"New: {db_path}")
    print(f"\nYou can now delete {json_path} if everything works correctly.")


if __name__ == "__main__":
    migrate_json_to_sqlite()
