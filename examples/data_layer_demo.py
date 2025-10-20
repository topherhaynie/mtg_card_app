"""MTG Card App - Data Layer Setup and Demo

This example demonstrates the layered architecture of the MTG card app,
showing how the different components work together.
"""

import logging

from mtg_card_app.core import Interactor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Demonstrate the data layer architecture with Scryfall integration.

    This example shows:
    1. How the Interactor orchestrates workflows
    2. How ManagerRegistry handles dependency injection
    3. How CardDataManager fetches data from Scryfall
    4. How DatabaseManager stores data locally
    5. How to create and search for combos
    """
    print("=" * 70)
    print("MTG Card App - Data Layer Architecture Demo")
    print("=" * 70)
    print()

    # Initialize the interactor (this sets up the entire stack)
    interactor = Interactor()

    # ===== Step 1: System Stats =====
    print("1. Initial System Stats")
    print("-" * 70)
    stats = interactor.get_system_stats()
    print(f"Total cards in database: {stats['database']['total_cards']}")
    print(f"Total combos in database: {stats['database']['total_combos']}")
    print()

    # ===== Step 2: Initialize with Sample Data =====
    print("2. Fetching Sample Cards from Scryfall")
    print("-" * 70)
    print("Importing famous MTG combo pieces and staples...")
    import_stats = interactor.initialize_with_sample_data()
    print("Import Results:")
    print(f"  - Total: {import_stats['total']}")
    print(f"  - Successful: {import_stats['successful']}")
    print(f"  - Failed: {import_stats['failed']}")
    print(f"  - Skipped (already exist): {import_stats['skipped']}")
    if import_stats["errors"]:
        print(f"  - Errors: {import_stats['errors'][:3]}")  # Show first 3 errors
    print()

    # ===== Step 3: Fetch Individual Cards =====
    print("3. Fetching Individual Cards")
    print("-" * 70)

    # Fetch a card (will use cache if already imported)
    card = interactor.fetch_card("Sol Ring")
    if card:
        print(f"Card: {card}")
        print(f"  Type: {card.type_line}")
        print(f"  CMC: {card.cmc}")
        print(f"  Colors: {card.colors or 'Colorless'}")
        print(f"  Price (USD): ${card.get_primary_price() or 'N/A'}")
        if card.oracle_text:
            print(f"  Text: {card.oracle_text[:100]}...")
    print()

    # ===== Step 4: Create a Combo =====
    print("4. Creating a Famous Combo")
    print("-" * 70)

    # Create the famous Isochron Scepter + Dramatic Reversal infinite mana combo
    try:
        combo = interactor.create_combo(
            card_names=["Isochron Scepter", "Dramatic Reversal"],
            name="Dramatic Scepter (Infinite Mana)",
            description=(
                "Imprint Dramatic Reversal on Isochron Scepter. With 2+ mana worth of "
                "mana rocks/dorks, you can repeatedly activate the Scepter to untap them, "
                "generating infinite mana and infinite storm count."
            ),
        )
        print(f"Created combo: {combo}")
        print(f"  Cards: {combo.card_names}")
        print(f"  Total Price: ${combo.total_price_usd or 'N/A'}")
        print(f"  Color Identity: {combo.colors_required or 'Colorless'}")
        print(f"  Description: {combo.description}")
    except Exception as e:
        logger.error(f"Failed to create combo: {e}")
    print()

    # ===== Step 5: Find Budget Cards =====
    print("5. Finding Budget Cards")
    print("-" * 70)
    budget_cards = interactor.get_budget_cards(max_price=5.0)
    print(f"Found {len(budget_cards)} cards under $5:")
    for card in budget_cards[:5]:  # Show first 5
        price = card.get_primary_price()
        print(f"  - {card.name}: ${price:.2f}")
    print()

    # ===== Step 6: Final Stats =====
    print("6. Final System Stats")
    print("-" * 70)
    final_stats = interactor.get_system_stats()
    print(f"Total cards in database: {final_stats['database']['total_cards']}")
    print(f"Total combos in database: {final_stats['database']['total_combos']}")
    print(f"Infinite combos: {final_stats['database']['infinite_combos']}")
    print(f"Scryfall API requests made: {final_stats['card_data']['scryfall_requests']['total_requests']}")
    print()

    # ===== Architecture Summary =====
    print("=" * 70)
    print("Architecture Summary")
    print("=" * 70)
    print("""
This demo showcased the layered architecture:

1. **Interactor Layer** (core/interactor.py)
   - Orchestrates high-level workflows
   - Provides user-friendly API for use cases

2. **Manager Layer**
   - ManagerRegistry: Dependency injection and service location
   - CardDataManager: Card fetching and caching logic
   - DatabaseManager: Coordinates database services

3. **Service Layer** (managers/db/services/)
   - CardService: CRUD operations for cards
   - ComboService: CRUD operations for combos
   - BaseService: Abstract base with standard interface

4. **Interface Layer** (interfaces/scryfall/)
   - ScryfallClient: API client for fetching card data
   - Handles rate limiting and error handling

5. **Domain Layer** (domain/entities/)
   - Card: Entity representing MTG cards
   - Combo: Entity representing card combinations

Benefits of this architecture:
✓ Modular and testable
✓ Easy to swap implementations (e.g., JSON → SQL database)
✓ Clear separation of concerns
✓ Dependency injection via registry
✓ Free-tier compatible (JSON storage + Scryfall API)

Next steps:
- Add RAG for semantic card search
- Integrate LLM for combo analysis
- Build MCP interface for user interaction
- Add deck building functionality
    """)

    print("Demo complete!")


if __name__ == "__main__":
    main()
