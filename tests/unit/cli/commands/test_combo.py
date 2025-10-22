"""Tests for the CLI combo command."""

from unittest.mock import Mock, patch

from mtg_card_app.ui.cli.commands.combo import combo


class TestComboFindCommand:
    """Test suite for the combo find subcommand."""

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_find_basic(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test basic combo find functionality."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combo_pieces.return_value = [
            {
                "name": "Dramatic Reversal",
                "oracle_text": "Untap all nonland permanents you control.",
            },
            {
                "name": "Isochron Scepter",
                "oracle_text": "Imprint — When Isochron Scepter enters the battlefield...",
            },
        ]
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["find", "Isochron Scepter"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.find_combo_pieces.assert_called_once_with(
            "Isochron Scepter",
            n_results=5,
        )
        assert "Dramatic Reversal" in result.output
        assert "Isochron Scepter" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_find_with_limit(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test combo find with custom limit."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combo_pieces.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["find", "Test Card", "--limit", "10"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.find_combo_pieces.assert_called_once_with("Test Card", n_results=10)

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_find_no_results(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test combo find with no results."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combo_pieces.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["find", "Nonexistent Card"])

        # Verify
        assert result.exit_code == 0
        assert "No combo pieces found" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_find_exception_handling(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo find error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combo_pieces.side_effect = Exception("Database error")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["find", "Test Card"])

        # Verify error handling
        assert result.exit_code == 0  # Click doesn't exit with error by default
        assert "Error:" in result.output
        assert "Database error" in result.output


class TestComboSearchCommand:
    """Test suite for the combo search subcommand."""

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_search_basic(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test basic combo search functionality."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combos_by_card.return_value = [
            {
                "name": "Thoracle Win",
                "cards": ["Thassa's Oracle", "Demonic Consultation"],
                "description": "Win the game by drawing your entire deck",
            },
        ]
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["search", "Thassa's Oracle"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.find_combos_by_card.assert_called_once_with("Thassa's Oracle")
        assert "Thoracle Win" in result.output
        assert "Demonic Consultation" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_search_no_results(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo search with no results."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combos_by_card.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["search", "Nonexistent Card"])

        # Verify
        assert result.exit_code == 0
        assert "No combos found" in result.output
        assert "mtg combo find" in result.output  # Suggests alternative

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_search_exception_handling(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo search error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.find_combos_by_card.side_effect = Exception("Search failed")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["search", "Test Card"])

        # Verify error handling
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "Search failed" in result.output


class TestComboBudgetCommand:
    """Test suite for the combo budget subcommand."""

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_budget_basic(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test basic combo budget functionality."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.get_budget_combos.return_value = [
            {
                "name": "Budget Combo",
                "cards": ["Card A", "Card B"],
                "total_price": 25.50,
            },
        ]
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["budget", "50"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.get_budget_combos.assert_called_once_with(max_price=50.0)
        assert "Budget Combo" in result.output
        assert "$25.50" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_budget_with_limit(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo budget with custom limit."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        # Return more combos than default limit
        mock_interactor.get_budget_combos.return_value = [
            {"name": f"Combo {i}", "cards": ["Card A"], "total_price": 10.0} for i in range(20)
        ]
        mock_interactor_class.return_value = mock_interactor

        # Run command with limit 5
        result = cli_runner.invoke(combo, ["budget", "100", "--limit", "5"])

        # Verify
        assert result.exit_code == 0
        # Should only display 5 combos even though 20 were returned
        # Count "Combo 0" through "Combo 4" (numbered combos only, not header)
        assert "Combo 4" in result.output
        assert "Combo 5" not in result.output  # Should be limited

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_budget_no_results(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo budget with no results."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.get_budget_combos.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["budget", "10"])

        # Verify
        assert result.exit_code == 0
        assert "No combos found under $10" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_budget_exception_handling(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo budget error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.get_budget_combos.side_effect = Exception("Price lookup failed")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["budget", "100"])

        # Verify error handling
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "Price lookup failed" in result.output


class TestComboCreateCommand:
    """Test suite for the combo create subcommand."""

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_basic(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test basic combo creation."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.return_value = {"success": True}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["create", "Card A", "Card B"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.create_combo.assert_called_once()
        call_args = mock_interactor.create_combo.call_args
        assert call_args[1]["card_names"] == ["Card A", "Card B"]
        assert "Created combo" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_with_name(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo creation with custom name."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.return_value = {"success": True}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(
            combo,
            ["create", "Card A", "Card B", "--name", "My Custom Combo"],
        )

        # Verify
        assert result.exit_code == 0
        call_args = mock_interactor.create_combo.call_args
        assert call_args[1]["combo_name"] == "My Custom Combo"
        assert "My Custom Combo" in result.output

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_with_description(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo creation with description."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.return_value = {"success": True}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(
            combo,
            ["create", "Card A", "Card B", "--description", "This combo wins the game"],
        )

        # Verify
        assert result.exit_code == 0
        call_args = mock_interactor.create_combo.call_args
        assert call_args[1]["description"] == "This combo wins the game"

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_default_name(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo creation with auto-generated name."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.return_value = {"success": True}
        mock_interactor_class.return_value = mock_interactor

        # Run command without name
        result = cli_runner.invoke(combo, ["create", "Card A", "Card B"])

        # Verify default name was generated
        assert result.exit_code == 0
        call_args = mock_interactor.create_combo.call_args
        assert "Card A + Card B Combo" in call_args[1]["combo_name"]

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_multiple_cards(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo creation with multiple cards."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.return_value = {"success": True}
        mock_interactor_class.return_value = mock_interactor

        # Run command with 3 cards
        result = cli_runner.invoke(combo, ["create", "Card A", "Card B", "Card C"])

        # Verify
        assert result.exit_code == 0
        call_args = mock_interactor.create_combo.call_args
        assert call_args[1]["card_names"] == ["Card A", "Card B", "Card C"]

    @patch("mtg_card_app.ui.cli.commands.combo.Interactor")
    @patch("mtg_card_app.ui.cli.commands.combo.ManagerRegistry")
    def test_combo_create_exception_handling(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test combo create error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_combo.side_effect = Exception("Creation failed")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(combo, ["create", "Card A", "Card B"])

        # Verify error handling
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "Creation failed" in result.output
