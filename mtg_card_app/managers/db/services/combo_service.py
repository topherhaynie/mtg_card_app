"""Combo service for database operations on Combo entities."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mtg_card_app.domain.entities import Combo, ComboType
from mtg_card_app.managers.db.services.base import BaseService


class ComboService(BaseService[Combo]):
    """Service for managing Combo entities in the database.

    Uses JSON file storage for simplicity (free tier).
    """

    def __init__(self, storage_path: str = "data/combos.json"):
        """Initialize the combo service.

        Args:
            storage_path: Path to JSON storage file

        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Ensure the storage file exists."""
        if not self.storage_path.exists():
            self._write_data({"combos": {}})

    def _read_data(self) -> Dict[str, Any]:
        """Read data from JSON storage."""
        with open(self.storage_path) as f:
            return json.load(f)

    def _write_data(self, data: Dict[str, Any]):
        """Write data to JSON storage."""
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create(self, entity: Combo) -> Combo:
        """Create a new combo in storage."""
        data = self._read_data()

        # Generate ID if not present
        if not entity.id:
            entity.id = str(uuid.uuid4())

        # Update timestamps
        entity.discovered_at = datetime.now()
        entity.updated_at = datetime.now()

        # Store combo
        data["combos"][entity.id] = entity.to_dict()
        self._write_data(data)

        return entity

    def get_by_id(self, entity_id: str) -> Optional[Combo]:
        """Get a combo by its ID."""
        data = self._read_data()
        combo_data = data["combos"].get(entity_id)

        if not combo_data:
            return None

        # Convert combo_types back to enum
        if "combo_types" in combo_data:
            combo_data["combo_types"] = [ComboType(ct) for ct in combo_data["combo_types"]]

        return Combo(**combo_data)

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Combo]:
        """Get all combos with pagination."""
        data = self._read_data()
        combos = []

        for combo_data in data["combos"].values():
            # Convert combo_types back to enum
            if "combo_types" in combo_data:
                combo_data["combo_types"] = [ComboType(ct) for ct in combo_data["combo_types"]]
            combos.append(Combo(**combo_data))

        # Apply offset and limit
        start = offset
        end = offset + limit if limit else None

        return combos[start:end]

    def update(self, entity: Combo) -> Combo:
        """Update an existing combo."""
        data = self._read_data()

        if not entity.id or entity.id not in data["combos"]:
            raise ValueError(f"Combo with ID {entity.id} not found")

        # Update timestamp
        entity.updated_at = datetime.now()

        # Update combo
        data["combos"][entity.id] = entity.to_dict()
        self._write_data(data)

        return entity

    def delete(self, entity_id: str) -> bool:
        """Delete a combo by ID."""
        data = self._read_data()

        if entity_id in data["combos"]:
            del data["combos"][entity_id]
            self._write_data(data)
            return True

        return False

    def search(self, query: Dict[str, Any]) -> List[Combo]:
        """Search for combos matching criteria.

        Args:
            query: Search criteria, e.g.:
                {"max_price": 50.0}
                {"combo_types": ["infinite_mana"]}
                {"card_count": 2}
                {"colors": ["U", "R"]}

        """
        data = self._read_data()
        results = []

        for combo_data in data["combos"].values():
            # Convert combo_types back to enum
            if "combo_types" in combo_data:
                combo_data["combo_types"] = [ComboType(ct) for ct in combo_data["combo_types"]]

            combo = Combo(**combo_data)
            matches = True

            # Check each query criterion
            for key, value in query.items():
                if key == "max_price":
                    if not combo.total_price_usd or combo.total_price_usd > value:
                        matches = False
                        break

                elif key == "min_price":
                    if not combo.total_price_usd or combo.total_price_usd < value:
                        matches = False
                        break

                elif key == "combo_types" and isinstance(value, list):
                    # Check if combo has any of the specified types
                    type_values = [ComboType(v) if isinstance(v, str) else v for v in value]
                    if not any(ct in combo.combo_types for ct in type_values):
                        matches = False
                        break

                elif key == "colors" and isinstance(value, list):
                    # Check if combo uses only specified colors
                    if not all(c in value for c in combo.colors_required):
                        matches = False
                        break

                elif key == "card_count":
                    if combo.card_count != value:
                        matches = False
                        break

                elif key == "max_card_count":
                    if combo.card_count > value:
                        matches = False
                        break

                elif key == "tags" and isinstance(value, list):
                    # Check if combo has all specified tags
                    if not all(tag in combo.tags for tag in value):
                        matches = False
                        break

                # Direct attribute comparison
                elif not hasattr(combo, key) or getattr(combo, key) != value:
                    matches = False
                    break

            if matches:
                results.append(combo)

        return results

    def exists(self, entity_id: str) -> bool:
        """Check if a combo exists."""
        data = self._read_data()
        return entity_id in data["combos"]

    def count(self) -> int:
        """Count total number of combos."""
        data = self._read_data()
        return len(data["combos"])

    def get_infinite_combos(self) -> List[Combo]:
        """Get all infinite combos."""
        data = self._read_data()
        results = []

        for combo_data in data["combos"].values():
            if "combo_types" in combo_data:
                combo_data["combo_types"] = [ComboType(ct) for ct in combo_data["combo_types"]]

            combo = Combo(**combo_data)
            if combo.is_infinite():
                results.append(combo)

        return results

    def get_budget_combos(self, max_price: float) -> List[Combo]:
        """Get combos under a certain total price."""
        return self.search({"max_price": max_price})

    def get_by_card_id(self, card_id: str) -> List[Combo]:
        """Get all combos containing a specific card."""
        data = self._read_data()
        results = []

        for combo_data in data["combos"].values():
            if card_id in combo_data.get("card_ids", []):
                if "combo_types" in combo_data:
                    combo_data["combo_types"] = [ComboType(ct) for ct in combo_data["combo_types"]]
                results.append(Combo(**combo_data))

        return results
