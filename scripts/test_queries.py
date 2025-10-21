"""Manual query testing script for validation.

MIGRATED: Now uses Interactor instead of deprecated QueryOrchestrator.

Tests real-world queries to validate:
1. Semantic search quality at scale
2. Query performance
3. Cache effectiveness
4. Filter accuracy
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_query(interactor: Interactor, query: str, query_num: int, total: int):
    """Test a single query and display results."""
    print(f"\n{'=' * 80}")
    print(f'QUERY {query_num}/{total}: "{query}"')
    print(f"{'=' * 80}")

    start_time = time.time()
    response = interactor.answer_natural_language_query(query)
    elapsed = time.time() - start_time

    print(f"\n📊 Response Time: {elapsed:.2f}s")
    print("\n🤖 AI Response:")
    print(f"{'-' * 80}")
    print(response)
    print(f"{'-' * 80}")


def main():
    """Run manual query validation tests."""
    print("=" * 80)
    print("MTG CARD APP - MANUAL QUERY VALIDATION (1,000 Cards)")
    print("=" * 80)
    print()

    # Initialize interactor with manager registry
    registry = ManagerRegistry.get_instance()
    interactor = Interactor(registry=registry)

    # Test queries covering different use cases
    test_queries = [
        # 1. Simple card search
        "Show me powerful blue counterspells",
        # 2. Combo detection
        "What are some infinite mana combos?",
        # 3. Filtering by mana cost
        "Find efficient removal spells under 2 mana",
        # 4. Type-specific search
        "What are the best planeswalkers for card advantage?",
        # 5. Color-specific + strategy
        "Recommend green ramp spells for a Commander deck",
        # 6. Complex multi-constraint
        "Show me red creatures under 3 mana that deal damage when they enter",
    ]

    total_queries = len(test_queries)
    total_time = 0

    for i, query in enumerate(test_queries, 1):
        start = time.time()
        test_query(interactor, query, i, total_queries)
        query_time = time.time() - start
        total_time += query_time

        # Brief pause between queries
        if i < total_queries:
            print("\n⏳ Moving to next query...\n")
            time.sleep(1)

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total queries: {total_queries}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {total_time / total_queries:.2f}s")
    print()

    # Get RAG stats
    rag_stats = registry.rag_manager.get_stats()
    print("RAG System Stats:")
    print(f"  - Total embeddings: {rag_stats['total_embeddings']}")
    print(f"  - Disk usage: {rag_stats['disk_usage_mb']:.2f} MB")
    print(f"  - Model: {rag_stats['model_name']}")
    print()

    print("=" * 80)
    print("✅ VALIDATION COMPLETE!")
    print("=" * 80)
    print()
    print("Key Observations:")
    print("  1. Semantic search quality at scale")
    print("  2. Query response times")
    print("  3. LLM accuracy with more card context")
    print("  4. Filter effectiveness")
    print()
    print("Next Steps:")
    print("  - Review query results above")
    print("  - Note any areas for improvement")
    print("  - Identify polish priorities (caching, conversation history, etc.)")
    print()


if __name__ == "__main__":
    main()
