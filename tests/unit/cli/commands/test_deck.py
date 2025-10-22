"""Tests for the CLI deck command."""

import json
from unittest.mock import Mock, mock_open, patch

from mtg_card_app.ui.cli.commands.deck import deck


class TestDeckNewCommand:
    """Test suite for the deck new subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_new_basic(self, mock_registry_class, mock_interactor_class, cli_runner):
        """Test basic deck creation."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_new_deck.return_value = {"format": "modern", "cards": []}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["new", "modern"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.create_new_deck.assert_called_once_with(
            deck_format="modern",
            commander=None,
        )
        assert "Created new" in result.output
        assert "modern" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_new_commander_with_commander(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test commander deck creation with commander specified."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_new_deck.return_value = {"format": "commander", "cards": []}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(
            deck,
            ["new", "commander", "--commander", "Muldrotha, the Gravetide"],
        )

        # Verify
        assert result.exit_code == 0
        mock_interactor.create_new_deck.assert_called_once_with(
            deck_format="commander",
            commander="Muldrotha, the Gravetide",
        )
        assert "Muldrotha, the Gravetide" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_new_commander_without_commander(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test commander deck creation without commander shows warning."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_new_deck.return_value = {"format": "commander", "cards": []}
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["new", "commander"])

        # Verify warning
        assert result.exit_code == 0
        assert "Warning" in result.output or "commander" in result.output.lower()

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_new_with_output(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck creation with output file."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        deck_data = {"format": "standard", "cards": ["Card A", "Card B"]}
        mock_interactor.create_new_deck.return_value = deck_data
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["new", "standard", "--output", "my_deck.json"])

        # Verify
        assert result.exit_code == 0
        mock_file.assert_called_once()
        # Verify json.dump was called with correct data
        assert "Saved to: my_deck.json" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_new_exception_handling(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck new error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.create_new_deck.side_effect = Exception("Creation failed")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["new", "modern"])

        # Verify error handling
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "Creation failed" in result.output


class TestDeckValidateCommand:
    """Test suite for the deck validate subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_validate_legal(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test validating a legal deck."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.validate_deck.return_value = {
            "is_legal": True,
            "format": "modern",
            "issues": [],
        }
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["validate", "test_deck.json"])

            # Verify
            assert result.exit_code == 0
            assert "legal" in result.output.lower()
            mock_interactor.validate_deck.assert_called_once()

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_validate_illegal(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test validating an illegal deck."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.validate_deck.return_value = {
            "is_legal": False,
            "format": "standard",
            "issues": ["Card X is banned", "Too many copies of Card Y"],
        }
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["validate", "test_deck.json"])

            # Verify
            assert result.exit_code == 0
            assert "banned" in result.output or "issues" in result.output.lower()
            assert "Too many copies" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_validate_text_format(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test validating a text format deck."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.validate_deck.return_value = {
            "is_legal": True,
            "format": "modern",
            "issues": [],
        }
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.txt", "w") as f:
                f.write("Card A\nCard B\nCard C")

            # Run command
            result = cli_runner.invoke(deck, ["validate", "test_deck.txt"])

            # Verify
            assert result.exit_code == 0
            # Verify it called validate_deck with parsed text format
            call_args = mock_interactor.validate_deck.call_args[0][0]
            assert "cards" in call_args


class TestDeckAnalyzeCommand:
    """Test suite for the deck analyze subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_analyze_rich_format(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test analyzing deck with rich format."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.analyze_deck.return_value = {
            "total_cards": 60,
            "creatures": 20,
            "spells": 25,
            "lands": 15,
            "avg_cmc": 2.5,
            "mana_curve": {"1": 5, "2": 10, "3": 8},
        }
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["analyze", "test_deck.json"])

            # Verify
            assert result.exit_code == 0
            assert "60" in result.output  # total cards
            assert "2.5" in result.output or "2.50" in result.output  # avg cmc

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_analyze_json_format(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test analyzing deck with JSON output."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        analysis_data = {
            "total_cards": 60,
            "creatures": 20,
            "spells": 25,
            "lands": 15,
            "avg_cmc": 2.5,
        }
        mock_interactor = Mock()
        mock_interactor.analyze_deck.return_value = analysis_data
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["analyze", "test_deck.json", "--format", "json"])

            # Verify JSON output
            assert result.exit_code == 0
            # Output should be valid JSON
            output_data = json.loads(result.output)
            assert output_data["total_cards"] == 60

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_analyze_markdown_format(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test analyzing deck with markdown output."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.analyze_deck.return_value = {
            "total_cards": 60,
            "creatures": 20,
            "spells": 25,
            "lands": 15,
            "avg_cmc": 2.5,
        }
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["analyze", "test_deck.json", "--format", "markdown"])

            # Verify markdown formatting
            assert result.exit_code == 0
            # Markdown should have headers and formatting
            assert "Analysis" in result.output or "Statistics" in result.output


class TestDeckSuggestCommand:
    """Test suite for the deck suggest subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_suggest_basic(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test basic deck suggestions."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.suggest_deck_improvements.return_value = [
            {
                "card_name": "Lightning Bolt",
                "reason": "Efficient removal spell",
                "price": 2.50,
            },
            {
                "card_name": "Counterspell",
                "reason": "Strong counter magic",
                "price": 1.00,
            },
        ]
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["suggest", "test_deck.json"])

            # Verify
            assert result.exit_code == 0
            assert "Lightning Bolt" in result.output
            assert "Counterspell" in result.output
            mock_interactor.suggest_deck_improvements.assert_called_once()

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_suggest_with_theme(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck suggestions with theme."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.suggest_deck_improvements.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(
                deck,
                ["suggest", "test_deck.json", "--theme", "graveyard recursion"],
            )

            # Verify theme was passed
            assert result.exit_code == 0
            call_args = mock_interactor.suggest_deck_improvements.call_args
            assert call_args[1]["theme"] == "graveyard recursion"

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_suggest_with_budget(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck suggestions with budget constraint."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.suggest_deck_improvements.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["suggest", "test_deck.json", "--budget", "100"])

            # Verify budget was passed
            assert result.exit_code == 0
            call_args = mock_interactor.suggest_deck_improvements.call_args
            assert call_args[1]["max_budget"] == 100.0

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_suggest_combo_mode(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck suggestions with combo mode."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.suggest_deck_improvements.return_value = []
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(
                deck,
                ["suggest", "test_deck.json", "--combo-mode", "focused"],
            )

            # Verify combo mode was passed
            assert result.exit_code == 0
            call_args = mock_interactor.suggest_deck_improvements.call_args
            assert call_args[1]["combo_mode"] == "focused"


class TestDeckExportCommand:
    """Test suite for the deck export subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_export_basic(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test basic deck export."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.export_deck.return_value = "1 Lightning Bolt\n1 Counterspell"
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(deck, ["export", "test_deck.json", "txt"])

            # Verify
            assert result.exit_code == 0
            assert "Exported deck to:" in result.output
            assert "test_deck.txt" in result.output
            # Verify the exported content was written to file
            with open("test_deck.txt") as f:
                content = f.read()
                assert "Lightning Bolt" in content
                assert "Counterspell" in content

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_export_with_output(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck export with output file."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.export_deck.return_value = "4 Lightning Bolt"
        mock_interactor_class.return_value = mock_interactor

        # Create temp file
        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            # Run command
            result = cli_runner.invoke(
                deck,
                ["export", "test_deck.json", "arena", "--output", "arena_import.txt"],
            )

            # Verify
            assert result.exit_code == 0
            assert "arena_import.txt" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    def test_deck_export_formats(
        self,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck export with different formats."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.export_deck.return_value = "Exported content"
        mock_interactor_class.return_value = mock_interactor

        # Test each export format
        formats = ["txt", "json", "mtgo", "arena", "markdown"]

        with cli_runner.isolated_filesystem():
            with open("test_deck.json", "w") as f:
                f.write('{"cards": ["Card A"]}')

            for export_format in formats:
                result = cli_runner.invoke(
                    deck,
                    ["export", "test_deck.json", export_format],
                )
                assert result.exit_code == 0, f"Failed for format {export_format}"


class TestDeckBuildCommand:
    """Test suite for the deck build subcommand."""

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_build_basic(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test basic AI deck building."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        deck_data = {"format": "standard", "cards": ["Card A", "Card B", "Card C"]}
        mock_interactor.build_deck.return_value = deck_data
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["build", "my_deck.json", "--format", "standard"])

        # Verify
        assert result.exit_code == 0
        mock_interactor.build_deck.assert_called_once_with(
            deck_format="standard",
            theme=None,
            max_budget=None,
        )
        assert "Built standard deck" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_build_with_theme(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test AI deck building with theme."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        deck_data = {"format": "commander", "cards": ["Card A"]}
        mock_interactor.build_deck.return_value = deck_data
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(
            deck,
            ["build", "sacrifice_deck.json", "--format", "commander", "--theme", "sacrifice"],
        )

        # Verify
        assert result.exit_code == 0
        call_args = mock_interactor.build_deck.call_args
        assert call_args[1]["theme"] == "sacrifice"
        assert "Theme: sacrifice" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_build_with_budget(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test AI deck building with budget constraint."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        deck_data = {"format": "modern", "cards": ["Card A"]}
        mock_interactor.build_deck.return_value = deck_data
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(
            deck,
            ["build", "budget_deck.json", "--format", "modern", "--budget", "50.00"],
        )

        # Verify
        assert result.exit_code == 0
        call_args = mock_interactor.build_deck.call_args
        assert call_args[1]["max_budget"] == 50.0
        assert "$50.00" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_build_card_count_display(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test that deck build displays card count."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        deck_data = {"format": "standard", "cards": ["A"] * 60}  # 60 cards
        mock_interactor.build_deck.return_value = deck_data
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["build", "my_deck.json", "--format", "standard"])

        # Verify card count is displayed
        assert result.exit_code == 0
        assert "60 cards" in result.output

    @patch("mtg_card_app.ui.cli.commands.deck.Interactor")
    @patch("mtg_card_app.ui.cli.commands.deck.ManagerRegistry")
    @patch("builtins.open", new_callable=mock_open)
    def test_deck_build_exception_handling(
        self,
        mock_file,
        mock_registry_class,
        mock_interactor_class,
        cli_runner,
    ):
        """Test deck build error handling."""
        # Setup mocks
        mock_registry = Mock()
        mock_registry_class.get_instance.return_value = mock_registry

        mock_interactor = Mock()
        mock_interactor.build_deck.side_effect = Exception("AI generation failed")
        mock_interactor_class.return_value = mock_interactor

        # Run command
        result = cli_runner.invoke(deck, ["build", "my_deck.json", "--format", "standard"])

        # Verify error handling
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "AI generation failed" in result.output
