#!/usr/bin/env python3
"""Build pre-computed data bundle for distribution.

This script creates a compressed data bundle containing:
- SQLite database (cards.db)
- ChromaDB embeddings (chroma/)
- Combos JSON (combos.json)
- Manifest with metadata (manifest.json)

The bundle enables fast setup (~30s download + 1-2min incremental update)
instead of full data initialization (~10 minutes).

Usage:
    python scripts/build_data_bundle.py [--output-dir dist]
"""

import argparse
import json
import logging
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_version() -> str:
    """Get the application version from pyproject.toml."""
    try:
        import tomli

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
            return data.get("project", {}).get("version", "0.1.0")
    except Exception as e:
        logger.warning("Could not read version from pyproject.toml: %s", e)
        return "0.1.0"


def build_bundle(output_dir: str = "dist", data_dir: str = "data") -> bool:
    """Build data bundle with SQLite DB + ChromaDB embeddings.

    Args:
        output_dir: Directory for output bundle
        data_dir: Directory containing source data

    Returns:
        True if successful, False otherwise

    """
    try:
        # Initialize services to get metadata
        from mtg_card_app.managers.db.manager import DatabaseManager
        from mtg_card_app.managers.rag.services.vector_store import ChromaVectorStoreService

        logger.info("Initializing services...")
        db_manager = DatabaseManager(data_dir=data_dir)
        vector_store = ChromaVectorStoreService(
            data_dir=f"{data_dir}/chroma",
            collection_name="mtg_cards",
        )

        # Prepare bundle directory
        output_path = Path(output_dir)
        bundle_dir = output_path / "data_bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Creating data bundle in %s", bundle_dir)

        # Export database
        logger.info("Exporting SQLite database...")
        db_export_path = bundle_dir / "cards.db"
        if not db_manager.card_service.export_to_path(str(db_export_path)):
            logger.error("Failed to export database")
            return False

        # Get database stats
        card_count = db_manager.card_service.count()
        last_update = db_manager.card_service.get_last_update_date()
        logger.info("Exported %d cards (last update: %s)", card_count, last_update)

        # Export embeddings
        logger.info("Exporting ChromaDB embeddings...")
        chroma_export_path = bundle_dir / "chroma"
        if not vector_store.export_embeddings(str(chroma_export_path)):
            logger.error("Failed to export embeddings")
            return False

        # Get embedding stats
        embedding_count = vector_store.get_embedding_count()
        logger.info("Exported %d embeddings", embedding_count)

        # Export combos (simple file copy)
        logger.info("Exporting combos...")
        combos_src = Path(data_dir) / "combos.json"
        if combos_src.exists():
            shutil.copy2(combos_src, bundle_dir / "combos.json")
            logger.info("Exported combos.json")
        else:
            logger.warning("combos.json not found, skipping")

        # Create manifest with metadata
        logger.info("Creating manifest...")
        manifest = {
            "version": get_version(),
            "build_date": datetime.now(timezone.utc).isoformat(),
            "last_card_date": last_update,
            "card_count": card_count,
            "embedding_count": embedding_count,
            "files": [
                "cards.db",
                "chroma/",
                "combos.json",
                "manifest.json",
            ],
            "instructions": {
                "extract": "Extract this bundle to your data directory",
                "update": "Run 'mtg-card-app update --since {last_card_date}' for latest cards",
            },
        }

        manifest_path = bundle_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info("Created manifest.json")

        # Create compressed tarball
        logger.info("Creating compressed tarball...")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        version = get_version().replace(".", "_")
        bundle_name = f"mtg-card-app-data-bundle-v{version}-{timestamp}.tar.xz"
        bundle_path = output_path / bundle_name

        with tarfile.open(bundle_path, "w:xz") as tar:
            tar.add(bundle_dir, arcname="data")

        # Get bundle size
        bundle_size_mb = bundle_path.stat().st_size / (1024 * 1024)
        logger.info("Created bundle: %s (%.2f MB)", bundle_name, bundle_size_mb)

        # Clean up temporary directory
        logger.info("Cleaning up temporary files...")
        shutil.rmtree(bundle_dir)

        # Print summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("Data Bundle Build Complete!")
        logger.info("=" * 60)
        logger.info("Bundle: %s", bundle_path)
        logger.info("Size: %.2f MB compressed", bundle_size_mb)
        logger.info("Cards: %d", card_count)
        logger.info("Embeddings: %d", embedding_count)
        logger.info("Last card date: %s", last_update)
        logger.info("")
        logger.info("Upload to GitHub Releases:")
        logger.info("  gh release create v%s %s", get_version(), bundle_path)
        logger.info("")

        return True

    except Exception:
        logger.exception("Error building data bundle")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build pre-computed data bundle for distribution",
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Output directory for bundle (default: dist)",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Source data directory (default: data)",
    )

    args = parser.parse_args()

    success = build_bundle(
        output_dir=args.output_dir,
        data_dir=args.data_dir,
    )

    if success:
        logger.info("✅ Bundle build successful!")
        return 0
    else:
        logger.error("❌ Bundle build failed!")
        return 1


if __name__ == "__main__":
    exit(main())
