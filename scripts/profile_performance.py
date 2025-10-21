#!/usr/bin/env python3
"""Detailed profiling of suggestion performance to identify bottleneck."""

import time

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck


def profile_suggestion():
    """Profile each step of the suggestion process."""
    print("=" * 70)
    print("DETAILED PERFORMANCE PROFILING")
    print("=" * 70)

    # Setup
    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor

    test_deck = Deck(
        format="Commander",
        cards=["Sol Ring", "Lightning Bolt", "Counterspell"],
        sections={},
        commander="Atraxa, Praetors' Voice",
        metadata={"theme": "control", "power": 7},
    )

    constraints = {
        "theme": "control",
        "n_results": 10,
        "combo_mode": "focused",
        "combo_limit": 3,
        "explain_combos": False,
    }

    print("\nStarting profiling...\n")

    # Total time
    start_total = time.time()

    # Call the suggestion
    print("1. Building query and calling suggest_cards()...")
    start_suggest = time.time()
    results = interactor.suggest_cards(test_deck, constraints)
    elapsed_suggest = (time.time() - start_suggest) * 1000

    elapsed_total = (time.time() - start_total) * 1000

    print(f"\n{'=' * 70}")
    print("TIMING RESULTS")
    print(f"{'=' * 70}")
    print(f"\nTotal suggestion time: {elapsed_suggest:.2f}ms ({elapsed_suggest / 1000:.2f}s)")
    print(f"Number of suggestions: {len(results)}")
    print(f"\nAverage time per suggestion: {elapsed_suggest / len(results) if results else 0:.2f}ms")

    # Now let's manually time the RAG search
    print(f"\n{'=' * 70}")
    print("MANUAL COMPONENT TIMING")
    print(f"{'=' * 70}")

    # Test RAG search directly
    print("\n2. Testing RAG search directly...")
    rag_manager = registry.rag_manager
    query = "control cards for Commander deck power level 7"

    start_rag = time.time()
    rag_results = rag_manager.search_similar(query, n_results=10)
    elapsed_rag = (time.time() - start_rag) * 1000
    print(f"   RAG search time: {elapsed_rag:.2f}ms ({elapsed_rag / 1000:.2f}s)")
    print(f"   Results found: {len(rag_results)}")

    # Test embedding generation
    print("\n3. Testing embedding generation...")
    start_embed = time.time()
    embedding = rag_manager.embedding_service.embed_text(query)
    elapsed_embed = (time.time() - start_embed) * 1000
    print(f"   Embedding time: {elapsed_embed:.2f}ms ({elapsed_embed / 1000:.2f}s)")
    print(f"   Embedding dimension: {len(embedding)}")

    # Test vector search only
    print("\n4. Testing vector search only...")
    start_vector = time.time()
    vector_results = rag_manager.vector_store.search_similar(embedding, n_results=10)
    elapsed_vector = (time.time() - start_vector) * 1000
    print(f"   Vector search time: {elapsed_vector:.2f}ms ({elapsed_vector / 1000:.2f}s)")

    # Test combo search
    print("\n5. Testing combo search...")
    combo_service = registry.db_manager.combo_service
    start_combo = time.time()
    combo_query = {"card_ids": [rag_results[0][0], rag_results[1][0]]} if len(rag_results) >= 2 else {}
    combos = combo_service.search(combo_query) if combo_query else []
    elapsed_combo = (time.time() - start_combo) * 1000
    print(f"   Combo search time: {elapsed_combo:.2f}ms ({elapsed_combo / 1000:.2f}s)")
    print(f"   Combos found: {len(combos)}")

    print(f"\n{'=' * 70}")
    print("BREAKDOWN ANALYSIS")
    print(f"{'=' * 70}")
    print(f"\nTotal suggestion time: {elapsed_suggest:.2f}ms")
    print(f"  RAG component: {elapsed_rag:.2f}ms ({elapsed_rag / elapsed_suggest * 100:.1f}%)")
    print(f"    - Embedding: {elapsed_embed:.2f}ms ({elapsed_embed / elapsed_suggest * 100:.1f}%)")
    print(f"    - Vector search: {elapsed_vector:.2f}ms ({elapsed_vector / elapsed_suggest * 100:.1f}%)")
    print(f"  Combo search (sample): {elapsed_combo:.2f}ms")
    print(
        f"  Other processing: {elapsed_suggest - elapsed_rag:.2f}ms ({(elapsed_suggest - elapsed_rag) / elapsed_suggest * 100:.1f}%)"
    )

    print(f"\n{'=' * 70}")
    print("BOTTLENECK IDENTIFICATION")
    print(f"{'=' * 70}")

    # Calculate what's taking the most time
    other_time = elapsed_suggest - elapsed_rag

    if elapsed_rag > elapsed_suggest * 0.5:
        print(
            f"\n⚠️  RAG search is the bottleneck ({elapsed_rag / 1000:.1f}s / {elapsed_rag / elapsed_suggest * 100:.0f}%)"
        )
        if elapsed_embed > elapsed_rag * 0.5:
            print(f"   → Embedding generation is slow ({elapsed_embed / 1000:.1f}s)")
        if elapsed_vector > elapsed_rag * 0.5:
            print(f"   → Vector search is slow ({elapsed_vector / 1000:.1f}s)")
    elif other_time > elapsed_suggest * 0.5:
        print(
            f"\n⚠️  Other processing is the bottleneck ({other_time / 1000:.1f}s / {other_time / elapsed_suggest * 100:.0f}%)"
        )
        print("   → Likely combo searches (multiple DB queries)")
        print("   → Try running with combo_limit=0 to confirm")
    else:
        print("\n✅ Performance is balanced across components")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    profile_suggestion()
