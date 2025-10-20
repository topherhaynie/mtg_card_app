"""
Card Search Module

This module provides functionality for searching MTG cards.
"""

__all__ = ["CardSearch", "search_by_name", "search_by_color"]


class CardSearch:
    """A class for searching MTG cards."""
    
    # Mock database of cards for demonstration
    MOCK_CARDS = [
        {"name": "Lightning Bolt", "color": "Red", "type": "Instant", "cmc": 1},
        {"name": "Counterspell", "color": "Blue", "type": "Instant", "cmc": 2},
        {"name": "Dark Ritual", "color": "Black", "type": "Instant", "cmc": 1},
        {"name": "Giant Growth", "color": "Green", "type": "Instant", "cmc": 1},
        {"name": "Swords to Plowshares", "color": "White", "type": "Instant", "cmc": 1},
        {"name": "Black Lotus", "color": "Colorless", "type": "Artifact", "cmc": 0},
        {"name": "Island", "color": "Blue", "type": "Basic Land", "cmc": 0},
        {"name": "Mountain", "color": "Red", "type": "Basic Land", "cmc": 0},
        {"name": "Swamp", "color": "Black", "type": "Basic Land", "cmc": 0},
        {"name": "Forest", "color": "Green", "type": "Basic Land", "cmc": 0},
        {"name": "Plains", "color": "White", "type": "Basic Land", "cmc": 0},
    ]
    
    def __init__(self):
        """Initialize the card search."""
        self.cards = self.MOCK_CARDS
    
    def search_by_name(self, query):
        """Search for cards by name.
        
        Args:
            query: The search query (partial or full card name)
            
        Returns:
            list: List of matching cards
        """
        query_lower = query.lower()
        return [
            card for card in self.cards
            if query_lower in card["name"].lower()
        ]
    
    def search_by_color(self, color):
        """Search for cards by color.
        
        Args:
            color: The color to search for
            
        Returns:
            list: List of matching cards
        """
        color_lower = color.lower()
        return [
            card for card in self.cards
            if color_lower in card["color"].lower()
        ]
    
    def search_by_type(self, card_type):
        """Search for cards by type.
        
        Args:
            card_type: The card type to search for
            
        Returns:
            list: List of matching cards
        """
        type_lower = card_type.lower()
        return [
            card for card in self.cards
            if type_lower in card["type"].lower()
        ]
    
    def print_results(self, results):
        """Print search results in a formatted way.
        
        Args:
            results: List of card dictionaries to print
        """
        if not results:
            print("No cards found")
            return
        
        print(f"\nFound {len(results)} card(s):")
        print("-" * 60)
        for card in results:
            print(f"{card['name']:<30} {card['color']:<12} {card['type']:<15} CMC: {card['cmc']}")
        print("-" * 60)


def search_by_name(query):
    """Search for cards by name.
    
    Args:
        query: The search query
        
    Returns:
        list: List of matching cards
    """
    searcher = CardSearch()
    return searcher.search_by_name(query)


def search_by_color(color):
    """Search for cards by color.
    
    Args:
        color: The color to search for
        
    Returns:
        list: List of matching cards
    """
    searcher = CardSearch()
    return searcher.search_by_color(color)
