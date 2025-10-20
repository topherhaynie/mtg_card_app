"""Card entity representing an MTG card."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Card:
    """Represents a Magic: The Gathering card.

    This entity contains all relevant information needed for combo detection,
    deck building, and pricing.
    """

    # Core identifiers
    id: str  # Scryfall ID
    name: str
    oracle_id: Optional[str] = None

    # Card characteristics
    mana_cost: Optional[str] = None
    cmc: float = 0.0  # Converted mana cost
    type_line: str = ""
    oracle_text: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    color_identity: List[str] = field(default_factory=list)

    # Card types for combo detection
    supertypes: List[str] = field(default_factory=list)
    card_types: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)

    # Card abilities and mechanics
    keywords: List[str] = field(default_factory=list)
    produced_mana: List[str] = field(default_factory=list)

    # Power/Toughness for creatures
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None

    # Legality and formats
    legalities: Dict[str, str] = field(default_factory=dict)

    # Pricing information
    prices: Dict[str, Optional[float]] = field(default_factory=dict)  # {currency: price}

    # Image and metadata
    image_uris: Dict[str, str] = field(default_factory=dict)
    set_code: str = ""
    set_name: str = ""
    rarity: str = ""

    # Additional metadata
    reserved: bool = False
    edhrec_rank: Optional[int] = None

    # Raw Scryfall data for reference
    raw_data: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_scryfall(cls, data: Dict[str, Any]) -> "Card":
        """Create a Card instance from Scryfall API data.

        Args:
            data: Raw JSON data from Scryfall API

        Returns:
            Card instance

        """
        # Parse type line
        type_line = data.get("type_line", "")
        supertypes, card_types, subtypes = cls._parse_type_line(type_line)

        # Extract pricing
        prices = {}
        price_data = data.get("prices", {})
        for currency in ["usd", "usd_foil", "eur", "tix"]:
            price_str = price_data.get(currency)
            prices[currency] = float(price_str) if price_str else None

        return cls(
            id=data["id"],
            name=data["name"],
            oracle_id=data.get("oracle_id"),
            mana_cost=data.get("mana_cost"),
            cmc=data.get("cmc", 0.0),
            type_line=type_line,
            oracle_text=data.get("oracle_text"),
            colors=data.get("colors", []),
            color_identity=data.get("color_identity", []),
            supertypes=supertypes,
            card_types=card_types,
            subtypes=subtypes,
            keywords=data.get("keywords", []),
            produced_mana=data.get("produced_mana", []),
            power=data.get("power"),
            toughness=data.get("toughness"),
            loyalty=data.get("loyalty"),
            legalities=data.get("legalities", {}),
            prices=prices,
            image_uris=data.get("image_uris", {}),
            set_code=data.get("set", ""),
            set_name=data.get("set_name", ""),
            rarity=data.get("rarity", ""),
            reserved=data.get("reserved", False),
            edhrec_rank=data.get("edhrec_rank"),
            raw_data=data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @staticmethod
    def _parse_type_line(type_line: str) -> tuple[List[str], List[str], List[str]]:
        """Parse the type line into supertypes, types, and subtypes.

        Example: "Legendary Creature — Human Wizard"
        -> (["Legendary"], ["Creature"], ["Human", "Wizard"])
        """
        supertypes = []
        card_types = []
        subtypes = []

        # Split on "—" to separate main types from subtypes
        parts = type_line.split("—")
        main_part = parts[0].strip()
        subtype_part = parts[1].strip() if len(parts) > 1 else ""

        # Known supertypes in MTG
        known_supertypes = {"Legendary", "Basic", "Snow", "World"}
        # Known card types
        known_types = {
            "Artifact",
            "Creature",
            "Enchantment",
            "Instant",
            "Land",
            "Planeswalker",
            "Sorcery",
            "Tribal",
            "Battle",
        }

        # Parse main part
        for word in main_part.split():
            if word in known_supertypes:
                supertypes.append(word)
            elif word in known_types:
                card_types.append(word)

        # Parse subtypes
        if subtype_part:
            subtypes = subtype_part.split()

        return supertypes, card_types, subtypes

    def is_creature(self) -> bool:
        """Check if this card is a creature."""
        return "Creature" in self.card_types

    def is_instant_or_sorcery(self) -> bool:
        """Check if this card is an instant or sorcery."""
        return "Instant" in self.card_types or "Sorcery" in self.card_types

    def is_permanent(self) -> bool:
        """Check if this card is a permanent."""
        permanent_types = {"Artifact", "Creature", "Enchantment", "Land", "Planeswalker", "Battle"}
        return any(t in self.card_types for t in permanent_types)

    def get_primary_price(self) -> Optional[float]:
        """Get the primary USD price (non-foil if available, otherwise foil)."""
        return self.prices.get("usd") or self.prices.get("usd_foil")

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "oracle_id": self.oracle_id,
            "mana_cost": self.mana_cost,
            "cmc": self.cmc,
            "type_line": self.type_line,
            "oracle_text": self.oracle_text,
            "colors": self.colors,
            "color_identity": self.color_identity,
            "supertypes": self.supertypes,
            "card_types": self.card_types,
            "subtypes": self.subtypes,
            "keywords": self.keywords,
            "power": self.power,
            "toughness": self.toughness,
            "prices": self.prices,
            "set_code": self.set_code,
            "rarity": self.rarity,
        }

    def __str__(self) -> str:
        """String representation of the card."""
        price = self.get_primary_price()
        price_str = f"${price:.2f}" if price else "N/A"
        return f"{self.name} ({self.set_code.upper()}) - {self.type_line} - {price_str}"
