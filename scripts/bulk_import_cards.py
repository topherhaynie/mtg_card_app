"""Script to bulk import popular MTG cards from Scryfall.

This script:
1. Fetches 1,000 popular cards from Scryfall using search queries
2. Imports them into the local database
3. Displays import statistics

Usage:
    python scripts/bulk_import_cards.py
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.core.manager_registry import ManagerRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_popular_cards_queries():
    """Get Scryfall search queries for popular cards.

    Returns diverse, playable cards across all formats and colors.
    """
    return [
        # Popular commanders and legendaries
        "is:commander game:paper year>=2020",
        "is:commander game:paper year>=2015 year<2020",
        # Staples by color
        "c:w t:instant OR t:sorcery game:paper",
        "c:u t:instant OR t:sorcery game:paper",
        "c:b t:instant OR t:sorcery game:paper",
        "c:r t:instant OR t:sorcery game:paper",
        "c:g t:instant OR t:sorcery game:paper",
        # Creatures
        "t:creature c:w game:paper",
        "t:creature c:u game:paper",
        "t:creature c:b game:paper",
        "t:creature c:r game:paper",
        "t:creature c:g game:paper",
        # Multicolor staples
        "c:wu t:creature game:paper",
        "c:ub t:creature game:paper",
        "c:br t:creature game:paper",
        "c:rg t:creature game:paper",
        "c:gw t:creature game:paper",
        # Artifacts and colorless
        "t:artifact c:c game:paper",
        "t:equipment game:paper",
        # Enchantments
        "t:enchantment game:paper",
        # Planeswalkers
        "t:planeswalker game:paper",
        # Popular combo pieces
        "o:infinite game:paper",
        "o:tutor game:paper",
        "o:counter game:paper",
        "o:draw game:paper",
    ]


def main():
    """Import 1,000 popular cards from Scryfall."""
    logger.info("=" * 80)
    logger.info("BULK CARD IMPORT - Fetching 1,000 Popular Cards")
    logger.info("=" * 80)
    print()

    # Initialize manager
    registry = ManagerRegistry.get_instance()
    card_manager = registry.card_data_manager

    # Get current card count
    current_stats = card_manager.get_stats()
    initial_count = current_stats.get("total_cards", 0)
    logger.info(f"Current cards in database: {initial_count}")
    print()

    # Calculate target
    target_cards = 1000
    cards_needed = max(0, target_cards - initial_count)

    if cards_needed == 0:
        logger.info(f"✅ Already have {initial_count} cards (target: {target_cards})")
        logger.info("Skipping import. Use vectorize_cards.py to ensure all cards are embedded.")
        return

    logger.info(f"Target: {target_cards} cards")
    logger.info(f"Need to import: ~{cards_needed} cards")
    print()

    # Import cards using Scryfall search
    logger.info("Starting import from Scryfall...")
    logger.info("This may take several minutes due to API rate limits...")
    print()

    all_card_names = set()
    queries = get_popular_cards_queries()

    for i, query in enumerate(queries, 1):
        if len(all_card_names) >= target_cards:
            break

        logger.info(f"Query {i}/{len(queries)}: {query[:60]}...")

        try:
            # Search for cards
            results = card_manager.search_cards(query, use_local=False, use_scryfall=True)

            # Add card names to set (deduplicate)
            for card in results:
                if len(all_card_names) >= target_cards:
                    break
                all_card_names.add(card.name)

            logger.info(f"  Found {len(results)} cards (total unique: {len(all_card_names)})")

            # Respect Scryfall rate limits (100ms between requests)
            time.sleep(0.1)

        except Exception as e:
            logger.warning(f"  Query failed: {e}")
            continue

    logger.info(f"\nCollected {len(all_card_names)} unique card names")
    print()

    # Import the cards
    logger.info("Importing cards into local database...")
    card_names_list = list(all_card_names)

    stats = card_manager.bulk_import_cards(card_names_list, fuzzy=False)

    # Display results
    print()
    logger.info("=" * 80)
    logger.info("IMPORT COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total attempted:  {stats['total']}")
    logger.info(f"Successfully imported: {stats['successful']}")
    logger.info(f"Skipped (already in DB): {stats['skipped']}")
    logger.info(f"Failed:           {stats['failed']}")

    # Show final card count
    final_stats = card_manager.get_stats()
    final_count = final_stats.get("total_cards", 0)
    logger.info(f"\nFinal card count: {final_count}")

    print()
    logger.info("=" * 80)
    logger.info("NEXT STEPS")
    logger.info("=" * 80)
    logger.info("Run the vectorization script to embed these cards:")
    logger.info("  python scripts/vectorize_cards.py")
    logger.info("=" * 80)

    if stats["failed"] > 0:
        logger.warning(f"\n⚠️  {stats['failed']} cards failed to import")
        logger.warning("This is normal - some cards may have been removed or renamed")
        if stats["errors"]:
            logger.info("\nFirst few errors:")
            for error in stats["errors"][:5]:
                logger.info(f"  - {error}")


if __name__ == "__main__":
    main()
