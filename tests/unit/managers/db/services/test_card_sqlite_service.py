"""Unit tests for CardSqliteService."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from mtg_card_app.domain.entities import Card
from mtg_card_app.managers.db.services.card_sqlite_service import CardSqliteService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def service(temp_db):
    """Create a CardSqliteService with temporary database."""
    return CardSqliteService(db_path=temp_db)


@pytest.fixture
def sample_cards():
    """Create sample cards for testing."""
    return [
        Card(
            id="test-001",
            name="Lightning Bolt",
            mana_cost="{R}",
            cmc=1.0,
            type_line="Instant",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            colors=["R"],
            color_identity=["R"],
            rarity="common",
        ),
        Card(
            id="test-002",
            name="Counterspell",
            mana_cost="{U}{U}",
            cmc=2.0,
            type_line="Instant",
            oracle_text="Counter target spell.",
            colors=["U"],
            color_identity=["U"],
            rarity="common",
        ),
        Card(
            id="test-003",
            name="Sol Ring",
            mana_cost="{1}",
            cmc=1.0,
            type_line="Artifact",
            oracle_text="{T}: Add {C}{C}.",
            colors=[],
            color_identity=[],
            rarity="uncommon",
        ),
    ]


class TestCardSqliteService:
    """Test CardSqliteService CRUD operations."""

    def test_create_card(self, service, sample_cards):
        """Test creating a card."""
        card = sample_cards[0]
        service.create(card)

        # Verify card was created
        retrieved = service.get_by_id(card.id)
        assert retrieved is not None
        assert retrieved.id == card.id
        assert retrieved.name == card.name
        assert retrieved.cmc == card.cmc

    def test_get_by_name(self, service, sample_cards):
        """Test retrieving card by name (case-insensitive)."""
        card = sample_cards[0]
        service.create(card)

        # Case-insensitive search should work
        retrieved = service.get_by_name("lightning bolt")
        assert retrieved is not None
        assert retrieved.id == card.id
        assert retrieved.name == card.name

        # Exact case should also work
        retrieved2 = service.get_by_name("Lightning Bolt")
        assert retrieved2 is not None
        assert retrieved2.id == card.id

    def test_get_by_name_not_found(self, service):
        """Test retrieving non-existent card returns None."""
        result = service.get_by_name("Nonexistent Card")
        assert result is None

    def test_bulk_create(self, service, sample_cards):
        """Test bulk creating multiple cards."""
        inserted = service.bulk_create(sample_cards)
        assert inserted == 3

        # Verify all cards were inserted
        assert service.count() == 3

        # Verify each card can be retrieved
        for card in sample_cards:
            retrieved = service.get_by_id(card.id)
            assert retrieved is not None
            assert retrieved.name == card.name

    def test_bulk_create_handles_duplicates(self, service, sample_cards):
        """Test bulk create skips duplicates."""
        # Insert once
        inserted1 = service.bulk_create(sample_cards)
        assert inserted1 == 3

        # Insert again - should skip duplicates
        inserted2 = service.bulk_create(sample_cards)
        assert inserted2 == 0

        # Total should still be 3
        assert service.count() == 3

    def test_search_by_colors(self, service, sample_cards):
        """Test searching by colors."""
        service.bulk_create(sample_cards)

        # Search for red cards
        red_cards = service.search({"colors": ["R"]})
        assert len(red_cards) == 1
        assert red_cards[0].name == "Lightning Bolt"

        # Search for colorless cards
        colorless = service.search({"colors": []})
        assert len(colorless) >= 1
        assert any(c.name == "Sol Ring" for c in colorless)

    def test_search_by_type(self, service, sample_cards):
        """Test searching by type."""
        service.bulk_create(sample_cards)

        # Search for instants
        instants = service.search({"type_line": "Instant"})
        assert len(instants) == 2
        names = {c.name for c in instants}
        assert "Lightning Bolt" in names
        assert "Counterspell" in names

    def test_search_by_cmc(self, service, sample_cards):
        """Test searching by converted mana cost."""
        service.bulk_create(sample_cards)

        # Search for 1 CMC cards
        cmc1 = service.search({"cmc": 1.0})
        assert len(cmc1) == 2
        names = {c.name for c in cmc1}
        assert "Lightning Bolt" in names
        assert "Sol Ring" in names

    def test_search_by_rarity(self, service, sample_cards):
        """Test searching by rarity."""
        service.bulk_create(sample_cards)

        # Search for common cards
        commons = service.search({"rarity": "common"})
        assert len(commons) == 2

        # Search for uncommon cards
        uncommons = service.search({"rarity": "uncommon"})
        assert len(uncommons) == 1
        assert uncommons[0].name == "Sol Ring"

    def test_search_multiple_criteria(self, service, sample_cards):
        """Test searching with multiple criteria."""
        service.bulk_create(sample_cards)

        # Search for 1 CMC common cards
        results = service.search({"cmc": 1.0, "rarity": "common"})
        assert len(results) == 1
        assert results[0].name == "Lightning Bolt"

    def test_update_card(self, service, sample_cards):
        """Test updating a card."""
        card = sample_cards[0]
        service.create(card)

        # Update card
        card.oracle_text = "Updated text"
        updated = service.update(card)
        assert updated.oracle_text == "Updated text"

        # Verify update persisted
        retrieved = service.get_by_id(card.id)
        assert retrieved is not None
        assert retrieved.oracle_text == "Updated text"

    def test_delete_card(self, service, sample_cards):
        """Test deleting a card."""
        card = sample_cards[0]
        service.create(card)

        # Verify card exists
        assert service.exists(card.id)

        # Delete card
        service.delete(card.id)

        # Verify card no longer exists
        assert not service.exists(card.id)
        assert service.get_by_id(card.id) is None

    def test_count(self, service, sample_cards):
        """Test counting cards."""
        assert service.count() == 0

        service.bulk_create(sample_cards)
        assert service.count() == 3

        service.delete(sample_cards[0].id)
        assert service.count() == 2

    def test_get_all(self, service, sample_cards):
        """Test getting all cards."""
        service.bulk_create(sample_cards)

        all_cards = service.get_all()
        assert len(all_cards) == 3

        # Verify all expected cards are present
        names = {c.name for c in all_cards}
        assert "Lightning Bolt" in names
        assert "Counterspell" in names
        assert "Sol Ring" in names

    def test_get_all_with_limit(self, service, sample_cards):
        """Test pagination with limit."""
        service.bulk_create(sample_cards)

        # Get first 2 cards
        page1 = service.get_all(limit=2, offset=0)
        assert len(page1) == 2

        # Get next card
        page2 = service.get_all(limit=2, offset=2)
        assert len(page2) == 1

    def test_preserves_json_fields(self, service):
        """Test that JSON fields (colors, keywords, etc.) are preserved."""
        card = Card(
            id="test-json",
            name="Complex Card",
            colors=["U", "R"],
            color_identity=["U", "R", "G"],
            keywords=["Flying", "Haste"],
            supertypes=["Legendary"],
            card_types=["Creature"],
            subtypes=["Dragon", "Wizard"],
        )

        service.create(card)
        retrieved = service.get_by_id(card.id)

        assert retrieved is not None
        assert retrieved.colors == ["U", "R"]
        assert retrieved.color_identity == ["U", "R", "G"]
        assert retrieved.keywords == ["Flying", "Haste"]
        assert retrieved.supertypes == ["Legendary"]
        assert retrieved.card_types == ["Creature"]
        assert retrieved.subtypes == ["Dragon", "Wizard"]
