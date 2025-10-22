"""Unit tests for Interactor combo management methods.

These are TRUE unit tests with mocked dependencies.
"""

from unittest.mock import Mock

import pytest

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities import Card, Combo


class TestCreateCombo:
    """Test the create_combo method."""

    def test_create_combo_fetches_all_cards(self) -> None:
        """Test that create_combo fetches each card by name."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
            color_identity=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Test Combo",
            description="",
            card_ids=["card1"],
            card_names=["Test Card"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        card_names = ["Card 1", "Card 2", "Card 3"]
        interactor.create_combo(card_names)

        # Should fetch each card
        assert mock_card_manager.get_card.call_count == 3

    def test_create_combo_raises_on_no_valid_cards(self) -> None:
        """Test that create_combo raises error when no cards found."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = None

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        with pytest.raises(ValueError, match="No valid cards found"):
            interactor.create_combo(["Nonexistent Card"])

    def test_create_combo_skips_missing_cards(self) -> None:
        """Test that create_combo continues when some cards not found."""

        def get_card_side_effect(name):
            if name == "Missing Card":
                return None
            return Card(
                id=name.lower().replace(" ", "_"),
                name=name,
                type_line="Instant",
                oracle_text="Test",
                cmc=2,
                colors=["U"],
                color_identity=["U"],
            )

        mock_card_manager = Mock()
        mock_card_manager.get_card.side_effect = get_card_side_effect

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Test Combo",
            description="",
            card_ids=["found_1", "found_2"],
            card_names=["Found 1", "Found 2"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.create_combo(["Found 1", "Missing Card", "Found 2"])

        # Should create combo with 2 cards
        assert mock_db_manager.combo_service.create.called

    def test_create_combo_generates_name_if_not_provided(self) -> None:
        """Test that combo gets auto-generated name."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
            color_identity=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Test Card + Test Card",
            description="",
            card_ids=["card1", "card1"],
            card_names=["Test Card", "Test Card"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.create_combo(["Test Card", "Test Card"])

        # Name should be auto-generated
        call_args = mock_db_manager.combo_service.create.call_args[0][0]
        assert "+" in call_args.name or call_args.name != ""

    def test_create_combo_uses_provided_name(self) -> None:
        """Test that combo uses custom name when provided."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
            color_identity=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Custom Combo Name",
            description="",
            card_ids=["card1"],
            card_names=["Test Card"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.create_combo(["Test Card"], name="Custom Combo Name")

        # Should use provided name
        call_args = mock_db_manager.combo_service.create.call_args[0][0]
        assert call_args.name == "Custom Combo Name"

    def test_create_combo_stores_in_database(self) -> None:
        """Test that combo is saved to database."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
            color_identity=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Test Combo",
            description="",
            card_ids=["card1"],
            card_names=["Test Card"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.create_combo(["Test Card"])

        # Should call combo service create
        mock_db_manager.combo_service.create.assert_called_once()

    def test_create_combo_calculates_color_identity(self) -> None:
        """Test that combo calculates color identity from cards."""

        def get_card_side_effect(name):
            colors = {"Blue Card": ["U"], "Red Card": ["R"], "Green Card": ["G"]}
            return Card(
                id=name.lower().replace(" ", "_"),
                name=name,
                type_line="Instant",
                oracle_text="Test",
                cmc=2,
                colors=colors.get(name, []),
                color_identity=colors.get(name, []),
            )

        mock_card_manager = Mock()
        mock_card_manager.get_card.side_effect = get_card_side_effect

        mock_db_manager = Mock()
        mock_db_manager.combo_service.create.return_value = Combo(
            id="combo1",
            name="Test Combo",
            description="",
            card_ids=["blue_card", "red_card"],
            card_names=["Blue Card", "Red Card"],
            colors_required=["R", "U"],
        )

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.create_combo(["Blue Card", "Red Card"])

        # Combo entity passed to create should have colors_required set
        call_args = mock_db_manager.combo_service.create.call_args[0][0]
        assert "U" in call_args.colors_required or "R" in call_args.colors_required


class TestFindCombosByCard:
    """Test the find_combos_by_card method."""

    def test_find_combos_by_card_fetches_card_first(self) -> None:
        """Test that method fetches card before searching combos."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_by_card_id.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        interactor.find_combos_by_card("Test Card")

        # Should fetch card first
        mock_card_manager.get_card.assert_called_once_with("Test Card")

    def test_find_combos_by_card_returns_empty_for_missing_card(self) -> None:
        """Test that method returns empty list when card not found."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = None

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
        )

        result = interactor.find_combos_by_card("Nonexistent Card")

        # Should return empty list
        assert result == []

    def test_find_combos_by_card_queries_by_card_id(self) -> None:
        """Test that method queries combos by card ID."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card123",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_by_card_id.return_value = []

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        interactor.find_combos_by_card("Test Card")

        # Should query by card ID
        mock_db_manager.combo_service.get_by_card_id.assert_called_once_with("card123")

    def test_find_combos_by_card_returns_combo_list(self) -> None:
        """Test that method returns list of combos."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="card1",
            name="Test Card",
            type_line="Instant",
            oracle_text="Test",
            cmc=2,
            colors=["U"],
        )

        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_by_card_id.return_value = [
            Combo(
                id="combo1",
                name="Combo 1",
                description="",
                card_ids=["card1", "card2"],
                card_names=["Test Card", "Other Card"],
            ),
            Combo(
                id="combo2",
                name="Combo 2",
                description="",
                card_ids=["card1", "card3"],
                card_names=["Test Card", "Third Card"],
            ),
        ]

        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.find_combos_by_card("Test Card")

        # Should return list of combos
        assert len(result) == 2
        assert all(isinstance(combo, Combo) for combo in result)


class TestGetBudgetCombos:
    """Test the get_budget_combos method."""

    def test_get_budget_combos_delegates_to_service(self) -> None:
        """Test that method delegates to combo service."""
        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_budget_combos.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        interactor.get_budget_combos(10.0)

        # Should call service with max_price
        mock_db_manager.combo_service.get_budget_combos.assert_called_once_with(10.0)

    def test_get_budget_combos_returns_combo_list(self) -> None:
        """Test that method returns list of combos."""
        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_budget_combos.return_value = [
            Combo(
                id="combo1",
                name="Budget Combo",
                description="",
                card_ids=["card1", "card2"],
                card_names=["Cheap Card 1", "Cheap Card 2"],
                total_price_usd=5.0,
            ),
        ]

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.get_budget_combos(10.0)

        # Should return list of combos
        assert len(result) == 1
        assert isinstance(result[0], Combo)

    def test_get_budget_combos_handles_empty_results(self) -> None:
        """Test that method handles no combos under price."""
        mock_db_manager = Mock()
        mock_db_manager.combo_service.get_budget_combos.return_value = []

        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=Mock(),
            db_manager=mock_db_manager,
        )

        result = interactor.get_budget_combos(0.01)

        # Should return empty list
        assert result == []
