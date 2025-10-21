#!/usr/bin/env python3
"""Quick test of CardSqliteService to verify it works before migration."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mtg_card_app.domain.entities import Card
from mtg_card_app.managers.db.services.card_sqlite_service import CardSqliteService


def test_sqlite_service():
    """Test basic CRUD operations."""
    test_db = "data/test_cards.db"

    # Clean up any existing test db
    Path(test_db).unlink(missing_ok=True)

    print("🔧 Testing CardSqliteService...")
    print("=" * 70)

    # Initialize service
    print("\n1. Creating service and database...")
    service = CardSqliteService(db_path=test_db)
    print("✅ Database created")

    # Create test card
    print("\n2. Creating test card...")
    test_card = Card(
        id="test-001",
        name="Lightning Bolt",
        mana_cost="{R}",
        cmc=1.0,
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        colors=["R"],
        color_identity=["R"],
        rarity="common",
    )
    service.create(test_card)
    print(f"✅ Created card: {test_card.name}")

    # Get by name
    print("\n3. Retrieving by name...")
    retrieved = service.get_by_name("Lightning Bolt")
    assert retrieved is not None
    assert retrieved.id == "test-001"
    print(f"✅ Retrieved: {retrieved.name} (id={retrieved.id})")

    # Get by ID
    print("\n4. Retrieving by ID...")
    by_id = service.get_by_id("test-001")
    assert by_id is not None
    assert by_id.name == "Lightning Bolt"
    print(f"✅ Retrieved: {by_id.name}")

    # Bulk create
    print("\n5. Bulk creating multiple cards...")
    bulk_cards = [
        Card(
            id="test-002",
            name="Counterspell",
            mana_cost="{U}{U}",
            cmc=2.0,
            type_line="Instant",
            colors=["U"],
            color_identity=["U"],
            rarity="common",
        ),
        Card(
            id="test-003",
            name="Dark Ritual",
            mana_cost="{B}",
            cmc=1.0,
            type_line="Instant",
            colors=["B"],
            color_identity=["B"],
            rarity="common",
        ),
        Card(
            id="test-004",
            name="Giant Growth",
            mana_cost="{G}",
            cmc=1.0,
            type_line="Instant",
            colors=["G"],
            color_identity=["G"],
            rarity="common",
        ),
    ]
    inserted = service.bulk_create(bulk_cards)
    print(f"✅ Inserted {inserted} cards")

    # Count
    print("\n6. Counting cards...")
    total = service.count()
    assert total == 4
    print(f"✅ Total cards: {total}")

    # Search by color
    print("\n7. Searching by color (red)...")
    red_cards = service.search({"colors": ["R"]})
    assert len(red_cards) == 1
    assert red_cards[0].name == "Lightning Bolt"
    print(f"✅ Found {len(red_cards)} red card(s)")

    # List all
    print("\n8. Listing all cards...")
    all_cards = service.get_all()
    assert len(all_cards) == 4
    for card in all_cards:
        print(f"   - {card.name}")
    print(f"✅ Listed {len(all_cards)} cards")

    # Cleanup
    print("\n9. Cleaning up test database...")
    Path(test_db).unlink()
    print("✅ Test database deleted")

    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSQLite service is working correctly.")
    print("Ready to run migration: python scripts/migrate_cards_to_sqlite.py")


if __name__ == "__main__":
    test_sqlite_service()
