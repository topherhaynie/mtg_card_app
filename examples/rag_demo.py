"""Demo script for RAG (semantic search) functionality.

This demonstrates:
1. Embedding MTG cards into vector database
2. Semantic search for similar cards
3. Finding cards with similar mechanics
4. Storage monitoring
"""

import logging

from mtg_card_app.core import Interactor
from mtg_card_app.managers.rag import RAGManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Run the RAG demo."""
    print("=" * 70)
    print("MTG Card App - RAG (Semantic Search) Demo")
    print("=" * 70)
    print()

    # ===== Step 1: Initialize =====
    print("1. Initializing RAG Manager")
    print("-" * 70)
    rag = RAGManager(data_dir="data")
    interactor = Interactor()
    print(f"Using model: {rag.model_name}")
    print()

    # ===== Step 2: Initial Stats =====
    print("2. Initial Storage Stats")
    print("-" * 70)
    stats = rag.get_stats()
    print(f"Embeddings in database: {stats['total_embeddings']}")
    print(f"Storage usage: {stats['disk_usage_mb']} MB")
    print()

    # ===== Step 3: Load Sample Cards =====
    print("3. Loading Sample Cards")
    print("-" * 70)
    print("Importing famous combo pieces and staples...")
    import_stats = interactor.initialize_with_sample_data()
    print(f"Loaded {import_stats['successful']} cards")
    print()

    # ===== Step 4: Embed Cards =====
    print("4. Embedding Cards")
    print("-" * 70)
    print("Creating vector embeddings for semantic search...")

    # Get all cards from the database
    from mtg_card_app.managers.db.services import CardService

    card_service = CardService(storage_path="data/cards.json")
    all_cards = card_service.get_all()

    print(f"Embedding {len(all_cards)} cards...")
    embed_stats = rag.embed_cards(all_cards)
    print(f"  Success: {embed_stats['success']}")
    print(f"  Skipped (already embedded): {embed_stats['skipped']}")
    print(f"  Failed: {embed_stats['failed']}")
    print()

    # ===== Step 5: Storage After Embedding =====
    print("5. Storage After Embedding")
    print("-" * 70)
    stats = rag.get_stats()
    print(f"Embeddings in database: {stats['total_embeddings']}")
    print(f"Storage usage: {stats['disk_usage_mb']} MB")
    print(f"Average per card: {stats['disk_usage_mb'] / max(stats['total_embeddings'], 1):.3f} MB")
    print()

    # ===== Step 6: Semantic Search Examples =====
    print("6. Semantic Search Examples")
    print("-" * 70)

    # Example 1: Search for ramp spells
    print("\\n🔍 Search: 'add mana to your mana pool'")
    results = rag.search_similar("add mana to your mana pool", n_results=3)
    for i, (card_id, similarity, metadata) in enumerate(results, 1):
        print(f"  {i}. {metadata['name']} (similarity: {similarity:.3f})")
        print(f"     Type: {metadata['type_line']}")

    # Example 2: Search for card draw
    print("\\n🔍 Search: 'draw cards whenever you cast a spell'")
    results = rag.search_similar("draw cards whenever you cast a spell", n_results=3)
    for i, (card_id, similarity, metadata) in enumerate(results, 1):
        print(f"  {i}. {metadata['name']} (similarity: {similarity:.3f})")
        print(f"     Type: {metadata['type_line']}")

    # Example 3: Search for removal
    print("\\n🔍 Search: 'destroy target creature'")
    results = rag.search_similar("destroy target creature", n_results=3)
    for i, (card_id, similarity, metadata) in enumerate(results, 1):
        print(f"  {i}. {metadata['name']} (similarity: {similarity:.3f})")
        print(f"     Type: {metadata['type_line']}")
    print()

    # ===== Step 7: Find Similar Cards =====
    print("7. Find Cards Similar to a Specific Card")
    print("-" * 70)

    # Get a card
    sol_ring = card_service.get_by_name("Sol Ring")
    if sol_ring:
        print(f"Finding cards similar to: {sol_ring.name}")
        similar = rag.search_similar_to_card(sol_ring, n_results=5)
        for i, (card_id, similarity, metadata) in enumerate(similar, 1):
            print(f"  {i}. {metadata['name']} (similarity: {similarity:.3f})")
            print(f"     Type: {metadata['type_line']}")
    print()

    # ===== Step 8: Filtered Search =====
    print("8. Filtered Search (Blue Cards Only)")
    print("-" * 70)
    print("🔍 Search: 'counter target spell' (filtered to blue cards)")

    # Note: This requires the card to have 'U' in its color_identity
    # This works if we stored color_identity in metadata
    results = rag.search_similar("counter target spell", n_results=5)
    blue_results = [(cid, sim, meta) for cid, sim, meta in results if "U" in meta.get("color_identity", "")]

    for i, (card_id, similarity, metadata) in enumerate(blue_results[:3], 1):
        print(f"  {i}. {metadata['name']} (similarity: {similarity:.3f})")
        print(f"     Colors: {metadata.get('color_identity', 'N/A')}")
    print()

    # ===== Final Summary =====
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"""
RAG (Retrieval-Augmented Generation) is now enabled!

✓ Embedded {stats["total_embeddings"]} cards
✓ Storage: {stats["disk_usage_mb"]} MB
✓ Semantic search is working
✓ Can find similar cards by meaning, not just keywords

Benefits:
- Find cards with similar mechanics even if they use different words
- Discover combo pieces you didn't know about
- Search by describing what you want, not exact card names
- Foundation for LLM integration (next phase)

Next Steps:
- Phase 3: Integrate LLM for combo analysis and recommendations
- Phase 4: Build MCP interface for natural language queries
- Phase 5: Complete deck builder with AI suggestions

Demo complete!
    """)


if __name__ == "__main__":
    main()
