#!/usr/bin/env python3
"""Check cache statistics after benchmark runs."""

from mtg_card_app.utils.suggestion_cache import get_suggestion_cache


def main():
    """Print cache statistics."""
    cache = get_suggestion_cache()
    stats = cache.stats()

    print("=" * 70)
    print("SUGGESTION CACHE STATISTICS")
    print("=" * 70)

    print(f"\nCache Hits: {stats['hits']}")
    print(f"Cache Misses: {stats['misses']}")
    print(f"Hit Rate: {stats['hit_rate']:.2%}")

    print(f"\nRAG Cache Size: {stats['rag_cache_size']}")
    print(f"Combo Cache Size: {stats['combo_cache_size']}")
    print(f"Total Entries: {stats['total_entries']}")

    total_requests = stats["hits"] + stats["misses"]
    print(f"\nTotal Requests: {total_requests}")

    print("=" * 70)


if __name__ == "__main__":
    main()
