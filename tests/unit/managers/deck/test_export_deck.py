"""Tests for deck export functionality."""

import pytest

from mtg_card_app.domain.entities.deck import Deck
from mtg_card_app.managers.deck.manager import DeckBuilderManager


@pytest.fixture
def sample_deck():
    """Create a sample deck for testing."""
    return Deck(
        format="Commander",
        cards=[
            "Sol Ring",
            "Lightning Bolt",
            "Counterspell",
            "Path to Exile",
            "Swords to Plowshares",
        ],
        sections={
            "Ramp": ["Sol Ring"],
            "Removal": ["Lightning Bolt", "Path to Exile", "Swords to Plowshares"],
            "Control": ["Counterspell"],
        },
        commander="Atraxa, Praetors' Voice",
        metadata={"name": "Test Deck", "theme": "control"},
    )


def test_export_text(sample_deck):
    """Test exporting deck as plain text."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "text")

    assert "# Test Deck" in result
    assert "# Format: Commander" in result
    assert "# Commander: Atraxa, Praetors' Voice" in result
    assert "# Theme: control" in result
    assert "## Commander" in result
    assert "1 Atraxa, Praetors' Voice" in result
    assert "## Ramp" in result or "## Removal" in result or "## Control" in result


def test_export_json(sample_deck):
    """Test exporting deck as JSON."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "json")

    import json

    data = json.loads(result)
    assert data["format"] == "Commander"
    assert data["commander"] == "Atraxa, Praetors' Voice"
    assert len(data["cards"]) == 5
    assert data["metadata"]["name"] == "Test Deck"


def test_export_moxfield(sample_deck):
    """Test exporting deck in Moxfield format."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "moxfield")

    assert "Commander\n" in result
    assert "1 Atraxa, Praetors' Voice" in result
    # Should have section names
    lines = result.split("\n")
    sections = [line for line in lines if line and not line.startswith("1 ")]
    assert len(sections) > 0  # Has section headers


def test_export_mtgo(sample_deck):
    """Test exporting deck in MTGO format."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "mtgo")

    # Should have all cards including commander
    assert "1 Sol Ring" in result
    assert "1 Lightning Bolt" in result
    assert "1 Atraxa, Praetors' Voice" in result
    # No section headers in MTGO format
    lines = [line for line in result.split("\n") if line]
    assert all(line.startswith("1 ") for line in lines)


def test_export_arena(sample_deck):
    """Test exporting deck in Arena format."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "arena")

    # Should have all cards (may not have set codes without card data)
    assert "1 Sol Ring" in result or "Sol Ring" in result
    assert "1 Lightning Bolt" in result or "Lightning Bolt" in result


def test_export_archidekt(sample_deck):
    """Test exporting deck in Archidekt format."""
    manager = DeckBuilderManager()
    result = manager.export_deck(sample_deck, "archidekt")

    # Archidekt uses same format as Moxfield
    assert "Commander\n" in result
    assert "1 Atraxa, Praetors' Voice" in result


def test_export_invalid_format(sample_deck):
    """Test exporting with invalid format raises error."""
    manager = DeckBuilderManager()

    with pytest.raises(ValueError, match="Unsupported export format"):
        manager.export_deck(sample_deck, "invalid")


def test_export_deck_no_sections():
    """Test exporting deck without sections."""
    deck = Deck(
        format="Modern",
        cards=["Lightning Bolt", "Counterspell"],
        sections={},
        metadata={"name": "Simple Deck"},
    )

    manager = DeckBuilderManager()
    result = manager.export_deck(deck, "text")

    assert "# Simple Deck" in result
    assert "## Main Deck" in result
    assert "1 Lightning Bolt" in result


def test_export_deck_no_commander():
    """Test exporting deck without commander."""
    deck = Deck(
        format="Modern",
        cards=["Lightning Bolt", "Counterspell"],
        sections={},
        metadata={"name": "No Commander"},
    )

    manager = DeckBuilderManager()
    result = manager.export_deck(deck, "text")

    assert "# No Commander" in result
    assert "Commander:" not in result  # No commander section
