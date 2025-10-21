#!/usr/bin/env python3
"""Test suggestion performance with combos disabled."""

import time

from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck


def test_no_combos():
    """Test suggestion speed without combo detection."""
    print("=" * 70)
    print("TESTING: Suggestions WITHOUT Combo Detection")
    print("=" * 70)

    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor

    test_deck = Deck(
        format="Commander",
        cards=["Sol Ring", "Lightning Bolt", "Counterspell"],
        sections={},
        commander="Atraxa, Praetors' Voice",
        metadata={"theme": "control", "power": 7},
    )

    # Test WITHOUT combos
    print("\n1. Suggestion WITHOUT combo detection (combo_limit=0):")
    constraints_no_combo = {
        "theme": "control",
        "n_results": 10,
        "combo_mode": "focused",
        "combo_limit": 0,  # NO COMBOS
        "explain_combos": False,
    }

    start = time.time()
    results_no_combo = interactor.suggest_cards(test_deck, constraints_no_combo)
    time_no_combo = (time.time() - start) * 1000

    print(f"   Time: {time_no_combo:.2f}ms ({time_no_combo / 1000:.2f}s)")
    print(f"   Results: {len(results_no_combo)}")

    # Test WITH combos
    print("\n2. Suggestion WITH combo detection (combo_limit=3):")
    constraints_with_combo = {
        "theme": "control",
        "n_results": 10,
        "combo_mode": "focused",
        "combo_limit": 3,  # WITH COMBOS
        "explain_combos": False,
    }

    start = time.time()
    results_with_combo = interactor.suggest_cards(test_deck, constraints_with_combo)
    time_with_combo = (time.time() - start) * 1000

    print(f"   Time: {time_with_combo:.2f}ms ({time_with_combo / 1000:.2f}s)")
    print(f"   Results: {len(results_with_combo)}")

    # Analysis
    print(f"\n{'=' * 70}")
    print("ANALYSIS")
    print(f"{'=' * 70}")

    combo_overhead = time_with_combo - time_no_combo
    print(f"\nWithout combos: {time_no_combo:.2f}ms ({time_no_combo / 1000:.2f}s)")
    print(f"With combos:    {time_with_combo:.2f}ms ({time_with_combo / 1000:.2f}s)")
    print(f"\nCombo overhead: {combo_overhead:.2f}ms ({combo_overhead / 1000:.2f}s)")
    print(f"Percentage:     {combo_overhead / time_with_combo * 100:.1f}% of total time")

    if combo_overhead > time_with_combo * 0.9:
        print("\n🎯 CONFIRMED: Combo detection is the bottleneck!")
        print(f"   Combo searches account for {combo_overhead / 1000:.1f} seconds")
    elif time_no_combo > 1000:
        print(f"\n⚠️  WARNING: Even without combos, suggestions take {time_no_combo / 1000:.1f}s")
        print("   There's another issue beyond combo detection")
    else:
        print(f"\n✅ Without combos, performance is good ({time_no_combo:.0f}ms)")
        print("   Focus optimization efforts on combo detection")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    test_no_combos()
