"""
Basic tests for the MTG Card App package.

These tests verify that the package structure is correct and modules work.
"""

import sys
import pytest


def test_package_import():
    """Test that the package can be imported."""
    import mtg_card_app
    assert mtg_card_app.__version__ == "0.1.0"
    assert "deck_builder" in mtg_card_app.__all__
    assert "card_search" in mtg_card_app.__all__


def test_deck_builder_import():
    """Test that the deck_builder module can be imported."""
    from mtg_card_app.deck_builder import DeckBuilder, create_deck
    assert DeckBuilder is not None
    assert create_deck is not None


def test_card_search_import():
    """Test that the card_search module can be imported."""
    from mtg_card_app.card_search import CardSearch, search_by_name
    assert CardSearch is not None
    assert search_by_name is not None


def test_deck_builder_functionality():
    """Test basic deck builder functionality."""
    from mtg_card_app.deck_builder import DeckBuilder
    
    deck = DeckBuilder("Test Deck")
    assert deck.name == "Test Deck"
    assert deck.get_card_count() == 0
    
    deck.add_card("Test Card", 4)
    assert deck.get_card_count() == 4
    
    deck.add_card("Another Card", 2)
    assert deck.get_card_count() == 6


def test_card_search_functionality():
    """Test basic card search functionality."""
    from mtg_card_app.card_search import CardSearch
    
    searcher = CardSearch()
    
    # Test search by name
    results = searcher.search_by_name("bolt")
    assert len(results) == 1
    assert results[0]["name"] == "Lightning Bolt"
    
    # Test search by color
    red_cards = searcher.search_by_color("Red")
    assert len(red_cards) >= 1
    assert any(card["color"] == "Red" for card in red_cards)
    
    # Test search by type
    instants = searcher.search_by_type("Instant")
    assert len(instants) >= 1
    assert all("Instant" in card["type"] for card in instants)


def test_deck_builder_create_function():
    """Test the create_deck helper function."""
    from mtg_card_app.deck_builder import create_deck
    
    deck = create_deck("Helper Test Deck")
    assert deck.name == "Helper Test Deck"
    assert deck.get_card_count() == 0


def test_card_search_helper_functions():
    """Test the search helper functions."""
    from mtg_card_app.card_search import search_by_name, search_by_color
    
    # Test search by name helper
    results = search_by_name("Lightning")
    assert len(results) >= 1
    
    # Test search by color helper
    blue_cards = search_by_color("Blue")
    assert len(blue_cards) >= 1


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
