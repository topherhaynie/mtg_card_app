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

from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.core.manager_registry import ManagerRegistry

# Configure logging - set to WARNING to avoid cluttering progress bar
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Vectorize all cards in the local database."""
    print("Starting card vectorization process...")

    # Initialize managers through registry
    registry = ManagerRegistry.get_instance()

    # Get managers
    card_manager = registry.card_data_manager
    rag_manager = registry.rag_manager

    # Fetch all cards (no limit to get all 35k+)
    print("Fetching all cards from local database...")
    cards = card_manager.get_all_cards(limit=None)

    if not cards:
        print("❌ No cards found in local database!")
        print("Please import cards first using the data layer demo or bulk import.")
        return

    print(f"✓ Found {len(cards):,} cards to vectorize\n")

    success_count = 0
    skipped_count = 0
    failed_count = 0

    # Use tqdm for progress bar
    with tqdm(total=len(cards), desc="Vectorizing cards", unit="card") as pbar:
        for card in cards:
            try:
                # Check if already embedded using RAGManager's exists() method
                if rag_manager.vector_store.exists(card.id):
                    skipped_count += 1
                    pbar.set_postfix({"success": success_count, "skipped": skipped_count, "failed": failed_count})
                    pbar.update(1)
                    continue

                # Embed the card
                if rag_manager.embed_card(card):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to embed card {card.name}: {e}")
                failed_count += 1

            pbar.set_postfix({"success": success_count, "skipped": skipped_count, "failed": failed_count})
            pbar.update(1)

    stats = {
        "total": len(cards),
        "success": success_count,
        "skipped": skipped_count,
        "failed": failed_count,
    }

    # Display results
    print("\n" + "=" * 60)
    print("  VECTORIZATION COMPLETE")
    print("=" * 60)
    print(f"Total cards:               {stats['total']:,}")
    print(f"Successfully embedded:     {stats['success']:,}")
    print(f"Skipped (already embedded): {stats['skipped']:,}")
    print(f"Failed:                    {stats['failed']:,}")

    # Get RAG stats
    rag_stats = rag_manager.get_stats()
    print("\n" + "=" * 60)
    print("  RAG SYSTEM STATISTICS")
    print("=" * 60)
    for key, value in rag_stats.items():
        if isinstance(value, (int, float)) and value > 1000:
            print(f"{key}: {value:,}")
        else:
            print(f"{key}: {value}")

    # Test semantic search
    print("\n" + "=" * 60)
    print("  TESTING SEMANTIC SEARCH")
    print("=" * 60)
    test_queries = [
        "blue counterspells",
        "card draw effects",
        "creature removal",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag_manager.search_similar(query, n_results=3)

        if results:
            print(f"  ✓ Found {len(results)} results:")
            for card_id, score, metadata in results:
                print(f"    - {metadata.get('name', 'Unknown')} (score: {score:.3f})")
        else:
            print("  ✗ No results found")

    print("\n" + "=" * 60)
    print("✓ Vectorization complete! Vector database is ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()
