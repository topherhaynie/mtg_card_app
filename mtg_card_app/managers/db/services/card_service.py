"""Card service for database operations on Card entities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mtg_card_app.domain.entities import Card
from mtg_card_app.managers.db.services.base import BaseService


class CardService(BaseService[Card]):
    """Service for managing Card entities in the database.

    Initially uses JSON file storage for simplicity (free tier).
    Can be easily swapped for a real database later.
    """

    def __init__(self, storage_path: str = "data/cards.json"):
        """Initialize the card service.

        Args:
            storage_path: Path to JSON storage file

        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Ensure the storage file exists."""
        if not self.storage_path.exists():
            self._write_data({"cards": {}})

    def _read_data(self) -> Dict[str, Any]:
        """Read data from JSON storage."""
        with open(self.storage_path) as f:
            return json.load(f)

    def _write_data(self, data: Dict[str, Any]):
        """Write data to JSON storage."""
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create(self, entity: Card) -> Card:
        """Create a new card in storage."""
        data = self._read_data()

        # Update timestamps
        entity.created_at = datetime.now()
        entity.updated_at = datetime.now()

        # Store card
        data["cards"][entity.id] = entity.to_dict()
        self._write_data(data)

        return entity

    def get_by_id(self, entity_id: str) -> Optional[Card]:
        """Get a card by its Scryfall ID."""
        data = self._read_data()
        card_data = data["cards"].get(entity_id)

        if not card_data:
            return None

        # Reconstruct Card from stored data
        return Card(**card_data)

    def get_by_name(self, name: str) -> Optional[Card]:
        """Get a card by its name."""
        data = self._read_data()

        for card_data in data["cards"].values():
            if card_data.get("name") == name:
                return Card(**card_data)

        return None

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Card]:
        """Get all cards with pagination."""
        data = self._read_data()
        cards = [Card(**card_data) for card_data in data["cards"].values()]

        # Apply offset and limit
        start = offset
        end = offset + limit if limit else None

        return cards[start:end]

    def update(self, entity: Card) -> Card:
        """Update an existing card."""
        data = self._read_data()

        if entity.id not in data["cards"]:
            raise ValueError(f"Card with ID {entity.id} not found")

        # Update timestamp
        entity.updated_at = datetime.now()

        # Update card
        data["cards"][entity.id] = entity.to_dict()
        self._write_data(data)

        return entity

    def delete(self, entity_id: str) -> bool:
        """Delete a card by ID."""
        data = self._read_data()

        if entity_id in data["cards"]:
            del data["cards"][entity_id]
            self._write_data(data)
            return True

        return False

    def search(self, query: Dict[str, Any]) -> List[Card]:
        """Search for cards matching criteria.

        Args:
            query: Search criteria, e.g.:
                {"colors": ["U", "R"], "max_cmc": 3}
                {"type_line": "Creature"}
                {"oracle_text": "draw"}

        Returns:
            List of matching cards

        """
        data = self._read_data()
        results = []

        for card_data in data["cards"].values():
            card = Card(**card_data)
            matches = True

            # Check each query criterion
            for key, value in query.items():
                if key == "colors" and isinstance(value, list):
                    # Check if card has all specified colors
                    if not all(c in card.colors for c in value):
                        matches = False
                        break

                elif key == "max_cmc":
                    if card.cmc > value:
                        matches = False
                        break

                elif key == "min_cmc":
                    if card.cmc < value:
                        matches = False
                        break

                elif key == "type_line":
                    if value.lower() not in card.type_line.lower():
                        matches = False
                        break

                elif key == "oracle_text":
                    if (card.oracle_text and value.lower() not in card.oracle_text.lower()) or not card.oracle_text:
                        matches = False
                        break

                elif key == "max_price":
                    price = card.get_primary_price()
                    if not price or price > value:
                        matches = False
                        break

                # Direct attribute comparison
                elif not hasattr(card, key) or getattr(card, key) != value:
                    matches = False
                    break

            if matches:
                results.append(card)

        return results

    def exists(self, entity_id: str) -> bool:
        """Check if a card exists."""
        data = self._read_data()
        return entity_id in data["cards"]

    def count(self) -> int:
        """Count total number of cards."""
        data = self._read_data()
        return len(data["cards"])

    def bulk_create(self, cards: List[Card]) -> int:
        """Bulk insert multiple cards.

        Args:
            cards: List of Card entities

        Returns:
            Number of cards created

        """
        data = self._read_data()
        count = 0

        for card in cards:
            card.created_at = datetime.now()
            card.updated_at = datetime.now()
            data["cards"][card.id] = card.to_dict()
            count += 1

        self._write_data(data)
        return count

    def get_by_color_identity(self, colors: List[str]) -> List[Card]:
        """Get cards with specific color identity."""
        data = self._read_data()
        results = []

        for card_data in data["cards"].values():
            card = Card(**card_data)
            # Check if card's color identity matches exactly
            if set(card.color_identity) == set(colors):
                results.append(card)

        return results

    def get_budget_cards(self, max_price: float) -> List[Card]:
        """Get cards under a certain price."""
        return self.search({"max_price": max_price})
