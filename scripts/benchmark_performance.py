#!/usr/bin/env python3
"""Performance benchmarking script for deck builder operations.

Measures baseline performance and identifies bottlenecks.
"""

import statistics
import time
from pathlib import Path

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck


def timer(func):
    """Decorator to time function execution."""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration_ms = (end - start) * 1000
        return result, duration_ms

    return wrapper


def run_multiple_times(func, n=5):
    """Run a function multiple times and return statistics."""
    times = []
    result = None

    for _ in range(n):
        result, duration = func()
        times.append(duration)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "runs": len(times),
    }


class PerformanceBenchmark:
    """Benchmark deck builder performance."""

    def __init__(self):
        """Initialize benchmark with registry."""
        self.registry = ManagerRegistry.get_instance()
        self.interactor = self.registry.interactor
        self.test_deck = self._create_test_deck()

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
    def benchmark_suggest_basic(self):
        """Benchmark basic suggestion (no combos, no explanations)."""
        constraints = {
            "theme": "control",
            "n_results": 10,
            "combo_mode": "focused",
            "combo_limit": 0,  # No combos
            "explain_combos": False,
        }
        return self.interactor.suggest_cards(self.test_deck, constraints)

    @timer
    def benchmark_suggest_with_combos(self):
        """Benchmark suggestion with combo detection."""
        constraints = {
            "theme": "control",
            "n_results": 10,
            "combo_mode": "focused",
            "combo_limit": 3,
            "explain_combos": False,
        }
        return self.interactor.suggest_cards(self.test_deck, constraints)

    @timer
    def benchmark_suggest_with_explanations(self):
        """Benchmark suggestion with LLM explanations."""
        constraints = {
            "theme": "control",
            "n_results": 5,  # Fewer results to avoid long LLM time
            "combo_mode": "focused",
            "combo_limit": 2,
            "explain_combos": True,
        }
        return self.interactor.suggest_cards(self.test_deck, constraints)

    @timer
    def benchmark_validate_deck(self):
        """Benchmark deck validation."""
        return self.interactor.validate_deck(self.test_deck)

    @timer
    def benchmark_analyze_deck(self):
        """Benchmark deck analysis."""
        return self.interactor.analyze_deck(self.test_deck)

    @timer
    def benchmark_export_text(self):
        """Benchmark text export."""
        return self.interactor.export_deck(self.test_deck, "text")

    @timer
    def benchmark_export_json(self):
        """Benchmark JSON export."""
        return self.interactor.export_deck(self.test_deck, "json")

    def run_all_benchmarks(self, runs=5):
        """Run all benchmarks and return results."""
        print("=" * 70)
        print("MTG Card App - Performance Benchmark")
        print("=" * 70)
        print(f"Running each benchmark {runs} times...\n")

        results = {}

        # Basic operations (fast)
        print("1. Validating deck...")
        results["validate_deck"] = run_multiple_times(self.benchmark_validate_deck, runs)

        print("2. Analyzing deck...")
        results["analyze_deck"] = run_multiple_times(self.benchmark_analyze_deck, runs)

        print("3. Exporting to text...")
        results["export_text"] = run_multiple_times(self.benchmark_export_text, runs)

        print("4. Exporting to JSON...")
        results["export_json"] = run_multiple_times(self.benchmark_export_json, runs)

        # Suggestions (slower)
        print("5. Suggesting cards (basic, no combos)...")
        results["suggest_basic"] = run_multiple_times(self.benchmark_suggest_basic, runs)

        print("6. Suggesting cards (with combo detection)...")
        results["suggest_with_combos"] = run_multiple_times(self.benchmark_suggest_with_combos, runs)

        print("7. Suggesting cards (with LLM explanations)...")
        results["suggest_with_explanations"] = run_multiple_times(
            self.benchmark_suggest_with_explanations,
            min(runs, 3),  # Fewer runs for LLM (slower)
        )

        return results

    def print_results(self, results):
        """Print benchmark results in a formatted table."""
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)
        print(f"{'Operation':<35} {'Mean':<12} {'Median':<12} {'Min':<12} {'Max':<12}")
        print("-" * 70)

        for name, stats in results.items():
            display_name = name.replace("_", " ").title()
            print(
                f"{display_name:<35} "
                f"{stats['mean']:>8.2f} ms  "
                f"{stats['median']:>8.2f} ms  "
                f"{stats['min']:>8.2f} ms  "
                f"{stats['max']:>8.2f} ms",
            )

        print("=" * 70)

        # Summary
        print("\nPERFORMANCE SUMMARY:")
        print("  Fast operations (<100ms): validate, analyze, export")
        print("  Medium operations (100-1000ms): suggest basic, suggest with combos")
        print("  Slow operations (>1000ms): suggest with LLM explanations")

        # Identify bottlenecks
        slowest = max(results.items(), key=lambda x: x[1]["mean"])
        print(f"\n  Slowest operation: {slowest[0]} ({slowest[1]['mean']:.2f}ms)")

        # Performance targets
        print("\nPERFORMANCE TARGETS:")
        suggest_basic = results.get("suggest_basic", {}).get("mean", 0)
        suggest_combos = results.get("suggest_with_combos", {}).get("mean", 0)
        suggest_llm = results.get("suggest_with_explanations", {}).get("mean", 0)

        print(f"  Current (basic): {suggest_basic:.0f}ms → Target: {suggest_basic * 0.4:.0f}ms (2.5x faster)")
        print(f"  Current (combos): {suggest_combos:.0f}ms → Target: {suggest_combos * 0.4:.0f}ms (2.5x faster)")
        print(f"  Current (LLM): {suggest_llm:.0f}ms → Target: {suggest_llm * 0.5:.0f}ms (2x faster)")

        print("\nOPTIMIZATION OPPORTUNITIES:")
        print("  1. Add caching for combo searches (high impact)")
        print("  2. Batch database queries (medium impact)")
        print("  3. Async LLM explanations (high impact)")
        print("  4. Cache RAG search results (medium impact)")
        print("=" * 70)


def main():
    """Run performance benchmarks."""
    benchmark = PerformanceBenchmark()

    try:
        results = benchmark.run_all_benchmarks(runs=5)
        benchmark.print_results(results)

        # Save results to file
        import json

        output_file = Path("benchmark_results.json")
        with output_file.open("w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n✅ Benchmark complete!")
    return 0


if __name__ == "__main__":
    exit(main())
