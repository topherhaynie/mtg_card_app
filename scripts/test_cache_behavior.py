#!/usr/bin/env python3
"""Test that caching is working correctly."""

import time

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.utils.suggestion_cache import get_suggestion_cache


def main():
    """Test cache behavior."""
    print("=" * 70)
    print("CACHE BEHAVIOR TEST")
    print("=" * 70)

    # Initialize
    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor
    cache = get_suggestion_cache()

    # Create test deck
    test_deck = Deck(
        format="Commander",
        cards=["Sol Ring", "Lightning Bolt", "Counterspell"],
        sections={},
        commander="Atraxa, Praetors' Voice",
        metadata={"theme": "control", "power": 7},
    )

    # Same constraints for all runs
    constraints = {
        "theme": "control",
        "n_results": 10,
        "combo_mode": "focused",
        "combo_limit": 3,
        "explain_combos": False,
    }

    print("\n1. FIRST RUN (cold cache):")
    cache.clear()
    start = time.time()
    result1 = interactor.suggest_cards(test_deck, constraints)
    elapsed1 = (time.time() - start) * 1000
    stats1 = cache.stats()
    print(f"   Time: {elapsed1:.2f}ms")
    print(f"   Results: {len(result1)} suggestions")
    print(f"   Cache stats: {stats1}")

    print("\n2. SECOND RUN (warm cache):")
    start = time.time()
    result2 = interactor.suggest_cards(test_deck, constraints)
    elapsed2 = (time.time() - start) * 1000
    stats2 = cache.stats()
    print(f"   Time: {elapsed2:.2f}ms")
    print(f"   Results: {len(result2)} suggestions")
    print(f"   Cache stats: {stats2}")

    print("\n3. THIRD RUN (warm cache):")
    start = time.time()
    result3 = interactor.suggest_cards(test_deck, constraints)
    elapsed3 = (time.time() - start) * 1000
    stats3 = cache.stats()
    print(f"   Time: {elapsed3:.2f}ms")
    print(f"   Results: {len(result3)} suggestions")
    print(f"   Cache stats: {stats3}")

    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("=" * 70)

    if elapsed2 < elapsed1 * 0.5:
        print(f"✅ Cache is working! Run 2 was {elapsed1 / elapsed2:.1f}x faster than run 1")
    else:
        print(f"❌ Cache may not be working. Run 2 ({elapsed2:.2f}ms) vs Run 1 ({elapsed1:.2f}ms)")

    if elapsed3 < elapsed1 * 0.5:
        print(f"✅ Cache is consistent! Run 3 was {elapsed1 / elapsed3:.1f}x faster than run 1")
    else:
        print(f"❌ Cache may not be consistent. Run 3 ({elapsed3:.2f}ms) vs Run 1 ({elapsed1:.2f}ms)")

    total_requests = stats3["hits"] + stats3["misses"]
    if total_requests > 0:
        print(f"\n📊 Cache Hit Rate: {stats3['hit_rate']:.1%}")
        print(f"   Total Hits: {stats3['hits']}")
        print(f"   Total Misses: {stats3['misses']}")
    else:
        print("\n⚠️ WARNING: Cache shows zero requests! Cache may not be integrated properly.")

    print("=" * 70)


if __name__ == "__main__":
    main()
