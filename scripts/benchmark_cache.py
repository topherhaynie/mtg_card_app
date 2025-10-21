#!/usr/bin/env python3
"""Performance benchmark focusing on caching improvements.

This benchmark tests:
1. Cold cache (first run) performance
2. Warm cache (subsequent runs) performance
3. Cache effectiveness (hit rate, speedup)
"""

import json
import statistics
import time

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.utils.suggestion_cache import clear_suggestion_cache, get_suggestion_cache


def timer(func):
    """Decorator to time function execution."""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        return result, elapsed_ms

    return wrapper


class CacheBenchmark:
    """Benchmark for cache performance testing."""

    def __init__(self):
        """Initialize benchmark with registry."""
        self.registry = ManagerRegistry.get_instance()
        self.interactor = self.registry.interactor
        self.test_deck = self._create_test_deck()
        self.cache = get_suggestion_cache()

    def _create_test_deck(self) -> Deck:
        """Create a test deck for benchmarking."""
        # Small Commander deck for testing
        cards = [
            "Sol Ring",
            "Lightning Bolt",
            "Counterspell",
            "Path to Exile",
            "Swords to Plowshares",
            "Mana Vault",
            "Mana Crypt",
            "Dark Ritual",
            "Birds of Paradise",
            "Noble Hierarch",
        ]

        return Deck(
            format="Commander",
            cards=cards,
            sections={},
            commander="Atraxa, Praetors' Voice",
            metadata={"theme": "control", "power": 7},
        )

    @timer
    def run_suggestion(self, combo_limit: int = 3):
        """Run a single suggestion query."""
        constraints = {
            "theme": "control",
            "n_results": 10,
            "combo_mode": "focused",
            "combo_limit": combo_limit,
            "explain_combos": False,
        }
        return self.interactor.suggest_cards(self.test_deck, constraints)

    def benchmark_cold_vs_warm(self):
        """Compare cold cache vs warm cache performance."""
        print("=" * 70)
        print("CACHE PERFORMANCE BENCHMARK")
        print("=" * 70)

        # Test 1: Cold cache
        print("\n1. COLD CACHE (first run):")
        clear_suggestion_cache()
        results1, time1 = self.run_suggestion()
        stats1 = self.cache.stats()
        print(f"   Time: {time1:.2f}ms")
        print(f"   Results: {len(results1)}")
        print(f"   Cache misses: {stats1['misses']}")
        print(f"   Cache entries created: {stats1['total_entries']}")

        # Test 2: Warm cache (immediate repeat)
        print("\n2. WARM CACHE (immediate repeat):")
        results2, time2 = self.run_suggestion()
        stats2 = self.cache.stats()
        print(f"   Time: {time2:.2f}ms")
        print(f"   Results: {len(results2)}")
        print(f"   Cache hits: {stats2['hits'] - stats1['hits']}")
        print(f"   Hit rate: {stats2['hit_rate']:.1%}")
        speedup = time1 / time2
        print(f"   Speedup: {speedup:.2f}x faster")

        # Test 3: Multiple warm runs
        print("\n3. SUSTAINED WARM CACHE (5 more runs):")
        times = []
        for i in range(5):
            _, elapsed = self.run_suggestion()
            times.append(elapsed)

        avg_time = statistics.mean(times)
        stats3 = self.cache.stats()
        print(f"   Average time: {avg_time:.2f}ms")
        print(f"   Min: {min(times):.2f}ms, Max: {max(times):.2f}ms")
        print(f"   Overall hit rate: {stats3['hit_rate']:.1%}")
        print(f"   Sustained speedup: {time1 / avg_time:.2f}x faster than cold")

        # Analysis
        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)

        if speedup >= 2.0:
            print(f"✅ EXCELLENT: Cache provides {speedup:.1f}x speedup")
        elif speedup >= 1.5:
            print(f"✅ GOOD: Cache provides {speedup:.1f}x speedup")
        elif speedup >= 1.2:
            print(f"⚠️  MODEST: Cache provides only {speedup:.1f}x speedup")
        else:
            print(f"❌ MINIMAL: Cache provides minimal speedup ({speedup:.1f}x)")

        print("\nCache Statistics:")
        print(f"  Total requests: {stats3['hits'] + stats3['misses']}")
        print(f"  Hits: {stats3['hits']}")
        print(f"  Misses: {stats3['misses']}")
        print(f"  Hit rate: {stats3['hit_rate']:.1%}")
        print(f"  RAG cache size: {stats3['rag_cache_size']}")
        print(f"  Combo cache size: {stats3['combo_cache_size']}")

        print("\n" + "=" * 70)

        return {
            "cold_time_ms": time1,
            "warm_time_ms": time2,
            "sustained_avg_ms": avg_time,
            "speedup": speedup,
            "sustained_speedup": time1 / avg_time,
            "cache_hit_rate": stats3["hit_rate"],
            "cache_hits": stats3["hits"],
            "cache_misses": stats3["misses"],
        }


def main():
    """Run cache performance benchmarks."""
    benchmark = CacheBenchmark()
    results = benchmark.benchmark_cold_vs_warm()

    # Save results
    output_file = "cache_benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")
    print("\n✅ Cache benchmark complete!")


if __name__ == "__main__":
    main()
