"""SQLite-based card service for database operations on Card entities."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from mtg_card_app.domain.entities import Card
from mtg_card_app.managers.db.services.base import BaseService


class CardSqliteService(BaseService[Card]):
    """Service for managing Card entities in SQLite database.

    Uses SQLite for efficient indexed lookups and filtering.
    Much faster than JSON for 30k+ cards.
    """

    def __init__(self, db_path: str = "data/cards.db"):
        """Initialize the card service.

        Args:
            db_path: Path to SQLite database file

        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    oracle_id TEXT,
                    mana_cost TEXT,
                    cmc REAL DEFAULT 0.0,
                    type_line TEXT,
                    oracle_text TEXT,
                    colors TEXT,  -- JSON array
                    color_identity TEXT,  -- JSON array
                    supertypes TEXT,  -- JSON array
                    card_types TEXT,  -- JSON array
                    subtypes TEXT,  -- JSON array
                    keywords TEXT,  -- JSON array
                    produced_mana TEXT,  -- JSON array
                    power TEXT,
                    toughness TEXT,
                    loyalty TEXT,
                    legalities TEXT,  -- JSON object
                    prices TEXT,  -- JSON object
                    image_uris TEXT,  -- JSON object
                    set_code TEXT,
                    set_name TEXT,
                    rarity TEXT,
                    reserved INTEGER DEFAULT 0,
                    edhrec_rank INTEGER,
                    raw_data TEXT,  -- JSON object
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # Create indexes for fast lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_name ON cards(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_oracle_id ON cards(oracle_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_colors ON cards(colors)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_type_line ON cards(type_line)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_cmc ON cards(cmc)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_card_rarity ON cards(rarity)")

            conn.commit()
        finally:
            conn.close()

    def _card_to_dict(self, card: Card) -> dict[str, Any]:
        """Convert Card to database-friendly dict."""
        return {
            "id": card.id,
            "name": card.name,
            "oracle_id": card.oracle_id,
            "mana_cost": card.mana_cost,
            "cmc": card.cmc,
            "type_line": card.type_line,
            "oracle_text": card.oracle_text,
            "colors": json.dumps(card.colors),
            "color_identity": json.dumps(card.color_identity),
            "supertypes": json.dumps(card.supertypes),
            "card_types": json.dumps(card.card_types),
            "subtypes": json.dumps(card.subtypes),
            "keywords": json.dumps(card.keywords),
            "produced_mana": json.dumps(card.produced_mana),
            "power": card.power,
            "toughness": card.toughness,
            "loyalty": card.loyalty,
            "legalities": json.dumps(card.legalities),
            "prices": json.dumps(card.prices),
            "image_uris": json.dumps(card.image_uris),
            "set_code": card.set_code,
            "set_name": card.set_name,
            "rarity": card.rarity,
            "reserved": 1 if card.reserved else 0,
            "edhrec_rank": card.edhrec_rank,
            "raw_data": json.dumps(card.raw_data),
            "created_at": card.created_at.isoformat() if card.created_at else None,
            "updated_at": card.updated_at.isoformat() if card.updated_at else None,
        }

    def _dict_to_card(self, row: sqlite3.Row | dict) -> Card:
        """Convert database row to Card entity."""
        return Card(
            id=row["id"],
            name=row["name"],
            oracle_id=row["oracle_id"],
            mana_cost=row["mana_cost"],
            cmc=row["cmc"],
            type_line=row["type_line"] or "",
            oracle_text=row["oracle_text"],
            colors=json.loads(row["colors"]) if row["colors"] else [],
            color_identity=json.loads(row["color_identity"]) if row["color_identity"] else [],
            supertypes=json.loads(row["supertypes"]) if row["supertypes"] else [],
            card_types=json.loads(row["card_types"]) if row["card_types"] else [],
            subtypes=json.loads(row["subtypes"]) if row["subtypes"] else [],
            keywords=json.loads(row["keywords"]) if row["keywords"] else [],
            produced_mana=json.loads(row["produced_mana"]) if row["produced_mana"] else [],
            power=row["power"],
            toughness=row["toughness"],
            loyalty=row["loyalty"],
            legalities=json.loads(row["legalities"]) if row["legalities"] else {},
            prices=json.loads(row["prices"]) if row["prices"] else {},
            image_uris=json.loads(row["image_uris"]) if row["image_uris"] else {},
            set_code=row["set_code"] or "",
            set_name=row["set_name"] or "",
            rarity=row["rarity"] or "",
            reserved=bool(row["reserved"]),
            edhrec_rank=row["edhrec_rank"],
            raw_data=json.loads(row["raw_data"]) if row["raw_data"] else {},
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )

    def create(self, entity: Card) -> Card:
        """Create a new card in storage."""
        conn = self._get_connection()
        try:
            # Update timestamps
            entity.created_at = datetime.now()
            entity.updated_at = datetime.now()

            data = self._card_to_dict(entity)

            conn.execute(
                """
                INSERT INTO cards VALUES (
                    :id, :name, :oracle_id, :mana_cost, :cmc, :type_line, :oracle_text,
                    :colors, :color_identity, :supertypes, :card_types, :subtypes,
                    :keywords, :produced_mana, :power, :toughness, :loyalty,
                    :legalities, :prices, :image_uris, :set_code, :set_name, :rarity,
                    :reserved, :edhrec_rank, :raw_data, :created_at, :updated_at
                )
            """,
                data,
            )

            conn.commit()
            return entity
        finally:
            conn.close()

    def get_by_id(self, entity_id: str) -> Card | None:
        """Get a card by its Scryfall ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM cards WHERE id = ?", (entity_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._dict_to_card(row)
        finally:
            conn.close()

    def get_by_name(self, name: str) -> Card | None:
        """Get a card by its name (case-insensitive)."""
        conn = self._get_connection()
        try:
            # Use COLLATE NOCASE for case-insensitive comparison
            cursor = conn.execute(
                "SELECT * FROM cards WHERE name = ? COLLATE NOCASE",
                (name,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._dict_to_card(row)
        finally:
            conn.close()

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[Card]:
        """Get all cards with pagination."""
        conn = self._get_connection()
        try:
            if limit:
                cursor = conn.execute("SELECT * FROM cards LIMIT ? OFFSET ?", (limit, offset))
            else:
                # No OFFSET if no LIMIT in SQLite
                cursor = conn.execute("SELECT * FROM cards")

            return [self._dict_to_card(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update(self, entity: Card) -> Card:
        """Update an existing card."""
        conn = self._get_connection()
        try:
            if not self.exists(entity.id):
                msg = f"Card with ID {entity.id} not found"
                raise ValueError(msg)

            # Update timestamp
            entity.updated_at = datetime.now()

            data = self._card_to_dict(entity)

            conn.execute(
                """
                UPDATE cards SET
                    name = :name,
                    oracle_id = :oracle_id,
                    mana_cost = :mana_cost,
                    cmc = :cmc,
                    type_line = :type_line,
                    oracle_text = :oracle_text,
                    colors = :colors,
                    color_identity = :color_identity,
                    supertypes = :supertypes,
                    card_types = :card_types,
                    subtypes = :subtypes,
                    keywords = :keywords,
                    produced_mana = :produced_mana,
                    power = :power,
                    toughness = :toughness,
                    loyalty = :loyalty,
                    legalities = :legalities,
                    prices = :prices,
                    image_uris = :image_uris,
                    set_code = :set_code,
                    set_name = :set_name,
                    rarity = :rarity,
                    reserved = :reserved,
                    edhrec_rank = :edhrec_rank,
                    raw_data = :raw_data,
                    updated_at = :updated_at
                WHERE id = :id
            """,
                data,
            )

            conn.commit()
            return entity
        finally:
            conn.close()

    def delete(self, entity_id: str) -> bool:
        """Delete a card by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM cards WHERE id = ?", (entity_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def search(self, query: dict[str, Any]) -> list[Card]:
        """Search for cards matching criteria."""
        conn = self._get_connection()
        try:
            where_clauses = []
            params = []

            # Build WHERE clause from query
            if "name" in query:
                where_clauses.append("name LIKE ?")
                params.append(f"%{query['name']}%")

            if "colors" in query:
                # Search for cards with specific colors
                colors = query["colors"] if isinstance(query["colors"], list) else [query["colors"]]
                for color in colors:
                    where_clauses.append("colors LIKE ?")
                    params.append(f'%"{color}"%')

            if "type_line" in query:
                where_clauses.append("type_line LIKE ?")
                params.append(f"%{query['type_line']}%")

            if "cmc" in query:
                where_clauses.append("cmc = ?")
                params.append(query["cmc"])

            if "rarity" in query:
                where_clauses.append("rarity = ?")
                params.append(query["rarity"])

            # Build and execute query
            sql = "SELECT * FROM cards"
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            cursor = conn.execute(sql, params)
            return [self._dict_to_card(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def exists(self, entity_id: str) -> bool:
        """Check if a card exists."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT 1 FROM cards WHERE id = ? LIMIT 1", (entity_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def count(self) -> int:
        """Count total number of cards."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM cards")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def bulk_create(self, cards: list[Card]) -> int:
        """Bulk insert cards efficiently."""
        conn = self._get_connection()
        try:
            inserted = 0
            for card in cards:
                # Update timestamps
                if not card.created_at:
                    card.created_at = datetime.now()
                if not card.updated_at:
                    card.updated_at = datetime.now()

                data = self._card_to_dict(card)

                try:
                    conn.execute(
                        """
                        INSERT INTO cards VALUES (
                            :id, :name, :oracle_id, :mana_cost, :cmc, :type_line, :oracle_text,
                            :colors, :color_identity, :supertypes, :card_types, :subtypes,
                            :keywords, :produced_mana, :power, :toughness, :loyalty,
                            :legalities, :prices, :image_uris, :set_code, :set_name, :rarity,
                            :reserved, :edhrec_rank, :raw_data, :created_at, :updated_at
                        )
                    """,
                        data,
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    # Card already exists, skip
                    pass

            conn.commit()
            return inserted
        finally:
            conn.close()

    def get_by_color_identity(self, colors: list[str]) -> list[Card]:
        """Get cards by color identity."""
        conn = self._get_connection()
        try:
            # Search for cards that contain all specified colors
            where_clauses = []
            params = []

            for color in colors:
                where_clauses.append("color_identity LIKE ?")
                params.append(f'%"{color}"%')

            sql = "SELECT * FROM cards"
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            cursor = conn.execute(sql, params)
            return [self._dict_to_card(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_budget_cards(self, max_price: float) -> list[Card]:
        """Get cards within a price budget."""
        # Note: This is a simple implementation. Prices are stored as JSON,
        # so we need to parse them. A more efficient approach would be to
        # have a separate prices table with proper indexing.
        all_cards = self.get_all()
        budget_cards = []

        for card in all_cards:
            if card.prices and "usd" in card.prices:
                price = card.prices["usd"]
                if price is not None and price <= max_price:
                    budget_cards.append(card)

        return budget_cards
