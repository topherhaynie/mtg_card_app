"""Deck entity for MTG deck builder."""


class Deck:
    def __init__(
        self,
        format: str,
        cards: list[str],
        sections: dict[str, list[str]] | None = None,
        commander: str | None = None,
        metadata: dict | None = None,
    ):
        """Args:
        format: Deck format (e.g., 'Commander', 'Modern')
        cards: List of card names or IDs
        sections: Optional dict of deck sections (e.g., {'creatures': [...], 'spells': [...]})
        commander: Optional commander card name/ID (for Commander)
        metadata: Optional dict for extra info (budget, theme, etc.)

        """
        self.format = format
        self.cards = cards
        self.sections = sections or {}
        self.commander = commander
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "cards": self.cards,
            "sections": self.sections,
            "commander": self.commander,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Deck":
        return cls(
            format=data.get("format", ""),
            cards=data.get("cards", []),
            sections=data.get("sections", {}),
            commander=data.get("commander"),
            metadata=data.get("metadata", {}),
        )
