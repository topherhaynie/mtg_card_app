"""Combo entity representing a card combination."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComboType(Enum):
    """Types of combos in MTG."""

    INFINITE_MANA = "infinite_mana"
    INFINITE_DRAW = "infinite_draw"
    INFINITE_DAMAGE = "infinite_damage"
    INFINITE_LIFE = "infinite_life"
    INFINITE_TOKENS = "infinite_tokens"
    INFINITE_MILL = "infinite_mill"
    LOCK = "lock"
    ONE_SHOT = "one_shot"
    ENGINE = "engine"
    SYNERGY = "synergy"
    OTHER = "other"


@dataclass
class Combo:
    """Represents a combination of cards that work together synergistically.

    A combo can range from simple 2-card interactions to complex multi-card engines.
    """

    # Core identifiers
    id: Optional[str] = None  # UUID generated for storage
    name: str = ""

    # Cards in the combo
    card_ids: List[str] = field(default_factory=list)  # Scryfall IDs
    card_names: List[str] = field(default_factory=list)  # For quick reference

    # Combo characteristics
    combo_types: List[ComboType] = field(default_factory=list)
    description: str = ""  # How the combo works
    steps: List[str] = field(default_factory=list)  # Step-by-step execution

    # Requirements and conditions
    prerequisites: List[str] = field(default_factory=list)  # What needs to be in place
    mana_required: Optional[str] = None  # Total mana needed to execute
    colors_required: List[str] = field(default_factory=list)  # Color identity

    # Combo metrics
    card_count: int = 0  # Number of cards in combo
    complexity: str = "medium"  # low, medium, high
    consistency: Optional[float] = None  # 0.0-1.0 how reliable it is

    # Pricing
    total_price_usd: Optional[float] = None
    price_per_card: Dict[str, float] = field(default_factory=dict)  # {card_id: price}

    # Format legality
    legal_formats: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)  # searchable tags
    popularity_score: Optional[float] = None  # How popular/well-known
    competitive_viability: Optional[str] = None  # casual, fringe, tier2, tier1

    # AI-generated insights
    llm_analysis: Optional[str] = None  # LLM's analysis of the combo
    weaknesses: List[str] = field(default_factory=list)  # What disrupts it
    strengths: List[str] = field(default_factory=list)  # Why it's good

    # Timestamps
    discovered_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Raw data for reference
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize computed fields."""
        if not self.card_count and self.card_ids:
            self.card_count = len(self.card_ids)

        if not self.discovered_at:
            self.discovered_at = datetime.now()

        if not self.updated_at:
            self.updated_at = datetime.now()

    def calculate_total_price(self, card_prices: Dict[str, float]) -> float:
        """Calculate total price of the combo.

        Args:
            card_prices: Dictionary mapping card_id to price

        Returns:
            Total price in USD

        """
        total = 0.0
        self.price_per_card = {}

        for card_id in self.card_ids:
            price = card_prices.get(card_id, 0.0)
            if price:
                self.price_per_card[card_id] = price
                total += price

        self.total_price_usd = total if total > 0 else None
        return total

    def is_budget_friendly(self, threshold: float = 50.0) -> bool:
        """Check if combo is within budget threshold."""
        if self.total_price_usd is None:
            return False
        return self.total_price_usd <= threshold

    def is_infinite(self) -> bool:
        """Check if this is an infinite combo."""
        infinite_types = {
            ComboType.INFINITE_MANA,
            ComboType.INFINITE_DRAW,
            ComboType.INFINITE_DAMAGE,
            ComboType.INFINITE_LIFE,
            ComboType.INFINITE_TOKENS,
            ComboType.INFINITE_MILL,
        }
        return any(ct in infinite_types for ct in self.combo_types)

    def get_color_identity(self) -> List[str]:
        """Get the combined color identity of all cards."""
        return sorted(list(set(self.colors_required)))

    def add_card(self, card_id: str, card_name: str):
        """Add a card to the combo."""
        if card_id not in self.card_ids:
            self.card_ids.append(card_id)
            self.card_names.append(card_name)
            self.card_count = len(self.card_ids)
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert combo to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "card_ids": self.card_ids,
            "card_names": self.card_names,
            "combo_types": [ct.value for ct in self.combo_types],
            "description": self.description,
            "steps": self.steps,
            "prerequisites": self.prerequisites,
            "mana_required": self.mana_required,
            "colors_required": self.colors_required,
            "card_count": self.card_count,
            "complexity": self.complexity,
            "total_price_usd": self.total_price_usd,
            "legal_formats": self.legal_formats,
            "tags": self.tags,
            "llm_analysis": self.llm_analysis,
            "weaknesses": self.weaknesses,
            "strengths": self.strengths,
        }

    def __str__(self) -> str:
        """String representation of the combo."""
        cards_str = " + ".join(self.card_names[:3])
        if len(self.card_names) > 3:
            cards_str += f" + {len(self.card_names) - 3} more"

        price_str = f"${self.total_price_usd:.2f}" if self.total_price_usd else "N/A"
        types_str = ", ".join([ct.value for ct in self.combo_types[:2]])

        return f"{self.name or 'Unnamed Combo'}: {cards_str} ({types_str}) - {price_str}"
