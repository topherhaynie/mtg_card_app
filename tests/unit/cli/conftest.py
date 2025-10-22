"""Pytest fixtures for CLI tests."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI test runner.

    Returns:
        CliRunner instance for testing Click commands

    """
    return CliRunner()


@pytest.fixture
def mock_interactor() -> Mock:
    """Create a mock Interactor with common return values.

    Returns:
        Mock: Mock Interactor instance with preset responses

    """
    mock = Mock()

    # Create a mock Card object with spec to limit attributes
    mock_card = Mock(
        spec=[
            "name",
            "mana_cost",
            "type_line",
            "oracle_text",
            "power",
            "toughness",
            "loyalty",
            "price_usd",
            "set_name",
            "rarity",
            "artist",
        ]
    )
    mock_card.name = "Lightning Bolt"
    mock_card.mana_cost = "{R}"
    mock_card.type_line = "Instant"
    mock_card.oracle_text = "Lightning Bolt deals 3 damage to any target."
    mock_card.power = None
    mock_card.toughness = None
    mock_card.loyalty = None
    mock_card.price_usd = "1.00"
    mock_card.set_name = "Alpha"
    mock_card.rarity = "common"
    mock_card.artist = "Christopher Rush"

    # Mock fetch_card to return the mock card object
    mock.fetch_card.return_value = mock_card

    # Search operations
    mock.search_cards.return_value = [
        {
            "name": "Lightning Bolt",
            "mana_cost": "{R}",
            "type_line": "Instant",
            "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        },
        {
            "name": "Shock",
            "mana_cost": "{R}",
            "type_line": "Instant",
            "oracle_text": "Shock deals 2 damage to any target.",
        },
    ]

    # Combo operations
    mock.find_combos.return_value = [
        {
            "name": "Thassa's Oracle + Demonic Consultation",
            "cards": ["Thassa's Oracle", "Demonic Consultation"],
            "colors": ["U", "B"],
            "description": "Win the game by exiling your library",
            "steps": [
                "Cast Demonic Consultation naming a card not in your deck",
                "Exile your entire library",
                "Cast Thassa's Oracle",
                "Win when ETB trigger resolves with 0 cards in library",
            ],
            "power_level": 10,
            "estimated_price": 25.00,
        },
    ]

    mock.search_combos.return_value = [
        {
            "name": "Isochron Scepter + Dramatic Reversal",
            "cards": ["Isochron Scepter", "Dramatic Reversal"],
            "colors": ["U"],
            "description": "Infinite mana with artifacts/creatures",
        },
    ]

    # Deck operations
    mock.build_deck.return_value = {
        "name": "Muldrotha Graveyard Value",
        "commander": "Muldrotha, the Gravetide",
        "format": "commander",
        "cards": [{"name": "Sol Ring", "quantity": 1}] * 99,
        "total_cards": 100,
        "avg_cmc": 3.2,
        "colors": ["U", "B", "G"],
        "estimated_price": 428.50,
    }

    mock.validate_deck.return_value = {
        "is_legal": True,
        "format": "commander",
        "errors": [],
        "warnings": [
            "Average CMC (3.8) is high - consider more 1-2 drops",
            "Low land count (32) - recommend 36-38",
        ],
    }

    mock.analyze_deck.return_value = {
        "total_cards": 100,
        "avg_cmc": 3.2,
        "color_distribution": {"U": 32, "B": 28, "G": 35, "C": 5},
        "type_distribution": {
            "Creature": 30,
            "Instant": 12,
            "Sorcery": 10,
            "Artifact": 10,
            "Enchantment": 8,
            "Planeswalker": 2,
            "Land": 38,
        },
        "mana_curve": {0: 8, 1: 8, 2: 18, 3: 24, 4: 18, 5: 12, 6: 12},
        "synergy_score": 8.5,
        "power_level": 7,
        "estimated_price": 428.50,
    }

    mock.suggest_deck_improvements.return_value = {
        "additions": [
            {
                "card": "Skirk Prospector",
                "price": 0.50,
                "reason": "Mana acceleration for goblin tokens",
            },
            {
                "card": "Goblin Chieftain",
                "price": 2.00,
                "reason": "Haste enabler for all goblins",
            },
        ],
        "removals": [
            {
                "card": "Goblin Shortcutter",
                "reason": "Too slow, minimal impact",
            },
            {
                "card": "Raging Goblin",
                "reason": "Vanilla 1/1, better options exist",
            },
        ],
        "total_cost": 23.99,
    }

    # System operations
    mock.get_system_stats.return_value = {
        "database": {
            "total_cards": 35402,
            "total_combos": 1247,
            "total_embeddings": 35402,
        },
        "cache": {
            "enabled": True,
            "hit_rate": 78.3,
            "entries": 247,
            "max_size": 1000,
            "size_mb": 12.4,
        },
        "llm": {
            "provider": "ollama",
            "model": "llama3",
            "status": "connected",
        },
        "card_data": {
            "total_cards": 35402,
        },
        "rag": {
            "status": "active",
        },
        "db": {
            "type": "sqlite",
        },
        "performance": {
            "avg_query_time_ms": 18,
            "deck_suggestion_time_ms": 18,
            "card_lookup_time_ms": 1,
        },
        "disk_usage": {
            "database_mb": 45.2,
            "embeddings_mb": 127.8,
            "cache_mb": 12.4,
            "total_mb": 185.4,
        },
    }

    return mock


@pytest.fixture
def mock_interactor_factory():
    """Provide a factory for creating mock Interactors with custom return values.

    Returns:
        Function that creates a mock Interactor with specified return values

    """

    def _create_mock(**kwargs) -> Mock:
        """Create a mock Interactor with custom return values.

        Args:
            **kwargs: Method names and their return values

        Returns:
            Mock Interactor instance

        """
        interactor = MagicMock()
        for method_name, return_value in kwargs.items():
            getattr(interactor, method_name).return_value = return_value
        return interactor

    return _create_mock


@pytest.fixture
def sample_deck() -> dict:
    """Provide sample deck data.

    Returns:
        Dictionary representing a Commander deck

    """
    return {
        "name": "Muldrotha Graveyard Value",
        "format": "commander",
        "commander": "Muldrotha, the Gravetide",
        "cards": [
            {"name": "Sol Ring", "quantity": 1},
            {"name": "Eternal Witness", "quantity": 1},
            {"name": "Sakura-Tribe Elder", "quantity": 1},
            # ... 96 more cards
        ],
        "total_cards": 100,
    }


@pytest.fixture
def sample_combo() -> dict:
    """Provide sample combo data.

    Returns:
        Dictionary representing a combo

    """
    return {
        "name": "Thassa's Oracle + Demonic Consultation",
        "cards": ["Thassa's Oracle", "Demonic Consultation"],
        "colors": ["U", "B"],
        "color_identity": ["U", "B"],
        "description": "Win the game by exiling your library then resolving Thassa's Oracle with 0 cards",
        "steps": [
            "Cast Demonic Consultation naming a card not in your deck",
            "Exile your entire library",
            "Cast Thassa's Oracle",
            "ETB trigger resolves - you have 0 cards in library, you win",
        ],
        "power_level": 10,
        "estimated_price": 25.00,
        "tags": ["infinite", "win-con", "cEDH"],
    }
