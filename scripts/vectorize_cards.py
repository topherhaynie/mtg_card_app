"""Script to vectorize all cards in the local database.

This script:
1. Fetches all cards from CardDataManager
2. Embeds them using RAGManager
3. Stores embeddings in ChromaDB
4. Displays statistics

Usage:
    python scripts/vectorize_cards.py
"""

import logging
import sys
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


def main():
    """Vectorize all cards in the local database."""
    logger.info("Starting card vectorization process...")

    # Initialize managers through registry
    registry = ManagerRegistry.get_instance()

    # Get managers
    card_manager = registry.card_data_manager
    rag_manager = registry.rag_manager

    # Fetch all cards
    logger.info("Fetching all cards from local database...")
    cards = card_manager.get_all_cards()

    if not cards:
        logger.warning("No cards found in local database!")
        logger.info("Please import cards first using the data layer demo or bulk import.")
        return

    logger.info(f"Found {len(cards)} cards to vectorize")

    # Show sample cards
    logger.info("Sample cards:")
    for card in cards[:3]:
        logger.info(f"  - {card.name} ({card.type_line})")

    # Vectorize cards
    logger.info("Embedding cards...")
    stats = rag_manager.embed_cards(cards)

    # Display results
    logger.info("=" * 60)
    logger.info("VECTORIZATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total cards:     {stats['total']}")
    logger.info(f"Successfully embedded: {stats['success']}")
    logger.info(f"Skipped (already embedded): {stats['skipped']}")
    logger.info(f"Failed:          {stats['failed']}")

    # Get RAG stats
    rag_stats = rag_manager.get_stats()
    logger.info("=" * 60)
    logger.info("RAG SYSTEM STATISTICS")
    logger.info("=" * 60)
    for key, value in rag_stats.items():
        logger.info(f"{key}: {value}")

    logger.info("=" * 60)

    # Test semantic search
    logger.info("\nTesting semantic search...")
    test_queries = [
        "blue counterspells",
        "card draw effects",
        "creature removal",
    ]

    for query in test_queries:
        logger.info(f"\nQuery: '{query}'")
        results = rag_manager.search_similar(query, n_results=3)

        if results:
            logger.info(f"  Found {len(results)} results:")
            for card_id, score, metadata in results:
                logger.info(f"    - {metadata.get('name', 'Unknown')} (score: {score:.3f})")
        else:
            logger.info("  No results found")

    logger.info("\n" + "=" * 60)
    logger.info("Vectorization complete! Vector database is ready.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
