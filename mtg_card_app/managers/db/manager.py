"""Database manager for coordinating database services."""

from pathlib import Path
from typing import Optional

from mtg_card_app.managers.db.services import CardService, ComboService


class DatabaseManager:
    """Manages all database services and coordinates data access.

    This class acts as a facade for the database layer, providing
    a single point of access to all database services.
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize the database manager.

        Args:
            data_dir: Directory for storing data files

        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize services
        self.card_service = CardService(
            storage_path=str(self.data_dir / "cards.json"),
        )
        self.combo_service = ComboService(
            storage_path=str(self.data_dir / "combos.json"),
        )

    def get_stats(self) -> dict:
        """Get statistics about the database.

        Returns:
            Dictionary with database statistics

        """
        return {
            "total_cards": self.card_service.count(),
            "total_combos": self.combo_service.count(),
            "infinite_combos": len(self.combo_service.get_infinite_combos()),
            "data_directory": str(self.data_dir.absolute()),
        }

    def clear_all_data(self):
        """Clear all data from the database. Use with caution!"""
        # Re-initialize services with empty data
        self.card_service._write_data({"cards": {}})
        self.combo_service._write_data({"combos": {}})

    def export_data(self, export_dir: Optional[str] = None) -> dict:
        """Export all data to a specified directory.

        Args:
            export_dir: Directory to export to (defaults to data_dir)

        Returns:
            Dictionary with export information

        """
        if export_dir is None:
            export_dir = self.data_dir
        else:
            export_dir = Path(export_dir)
            export_dir.mkdir(parents=True, exist_ok=True)

        # Copy current data files
        import shutil

        cards_src = self.data_dir / "cards.json"
        combos_src = self.data_dir / "combos.json"

        if cards_src.exists():
            shutil.copy(cards_src, export_dir / "cards.json")
        if combos_src.exists():
            shutil.copy(combos_src, export_dir / "combos.json")

        return {
            "exported_to": str(export_dir.absolute()),
            "files_exported": ["cards.json", "combos.json"],
        }
