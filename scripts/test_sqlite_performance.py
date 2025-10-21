#!/usr/bin/env python3
"""Test SQLite performance vs JSON for card lookups."""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.managers.db.services.card_service import CardService
from mtg_card_app.managers.db.services.card_sqlite_service import CardSqliteService


def test_lookup_performance():
    """Compare lookup performance between JSON and SQLite."""
    # Test cards to lookup
    test_cards = [
        "Lightning Bolt",
        "Counterspell",
        "Dark Ritual",
        "Giant Growth",
        "Black Lotus",
        "Mox Sapphire",
        "Ancestral Recall",
        "Time Walk",
        "Sol Ring",
        "Brainstorm",
    ]

    print("=" * 70)
    print("CARD LOOKUP PERFORMANCE TEST")
    print("=" * 70)

    # Test JSON service
    print("\n📄 Testing JSON Service...")
    json_service = CardService(storage_path="data/cards.json.bak")

    json_times = []
    for card_name in test_cards:
        start = time.perf_counter()
        card = json_service.get_by_name(card_name)
        elapsed = time.perf_counter() - start
        json_times.append(elapsed * 1000)  # Convert to ms
        status = "✅" if card else "❌"
        print(f"  {status} {card_name}: {elapsed * 1000:.2f}ms")

    json_avg = sum(json_times) / len(json_times)

    # Test SQLite service
    print("\n🗄️  Testing SQLite Service...")
    sqlite_service = CardSqliteService(db_path="data/cards.db")

    sqlite_times = []
    for card_name in test_cards:
        start = time.perf_counter()
        card = sqlite_service.get_by_name(card_name)
        elapsed = time.perf_counter() - start
        sqlite_times.append(elapsed * 1000)  # Convert to ms
        status = "✅" if card else "❌"
        print(f"  {status} {card_name}: {elapsed * 1000:.2f}ms")

    sqlite_avg = sum(sqlite_times) / len(sqlite_times)

    # Results
    speedup = json_avg / sqlite_avg if sqlite_avg > 0 else 0

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"JSON average:    {json_avg:.2f}ms")
    print(f"SQLite average:  {sqlite_avg:.2f}ms")
    print(f"Speedup:         {speedup:.1f}x faster")
    print("=" * 70)

    if speedup > 10:
        print("\n🚀 MASSIVE IMPROVEMENT! SQLite is significantly faster!")
    elif speedup > 5:
        print("\n✅ Great improvement! SQLite is much faster!")
    elif speedup > 2:
        print("\n👍 Good improvement! SQLite is faster!")
    else:
        print("\n⚠️  Modest improvement. May need further optimization.")


if __name__ == "__main__":
    test_lookup_performance()
