"""
Deck Builder Module

This module provides functionality for building and managing MTG decks.
"""

__all__ = ["DeckBuilder", "create_deck", "add_card_to_deck"]


class DeckBuilder:
    """A class for building MTG decks."""
    
    def __init__(self, name="Untitled Deck"):
        """Initialize a new deck builder.
        
        Args:
            name: The name of the deck
        """
        self.name = name
        self.cards = []
    
    def add_card(self, card_name, quantity=1):
        """Add a card to the deck.
        
        Args:
            card_name: The name of the card to add
            quantity: The number of copies to add (default: 1)
        """
        self.cards.append({"name": card_name, "quantity": quantity})
        print(f"Added {quantity}x {card_name} to {self.name}")
    
    def list_cards(self):
        """List all cards in the deck."""
        if not self.cards:
            print(f"{self.name} is empty")
            return
        
        print(f"\n{self.name}:")
        print("-" * 40)
        total = 0
        for card in self.cards:
            print(f"{card['quantity']}x {card['name']}")
            total += card['quantity']
        print("-" * 40)
        print(f"Total cards: {total}")
    
    def get_card_count(self):
        """Get the total number of cards in the deck."""
        return sum(card['quantity'] for card in self.cards)


def create_deck(name):
    """Create a new deck.
    
    Args:
        name: The name of the deck
        
    Returns:
        DeckBuilder: A new deck builder instance
    """
    return DeckBuilder(name)


def add_card_to_deck(deck, card_name, quantity=1):
    """Add a card to a deck.
    
    Args:
        deck: The deck builder instance
        card_name: The name of the card to add
        quantity: The number of copies to add (default: 1)
    """
    deck.add_card(card_name, quantity)
