# MTG Card App - Data Layer Setup

## Overview

This project demonstrates a clean, modular architecture for building an MTG combo finder application. The data layer has been successfully implemented with:

- **Scryfall API integration** for fetching card data
- **Local JSON storage** for caching cards and combos  
- **Layered architecture** for modularity and testability
- **Dependency injection** via Manager Registry
- **Free-tier compatible** - no paid services required

## Architecture

```
mtg_card_app/
├── domain/
│   └── entities/          # Core business entities (Card, Combo)
├── interfaces/
│   └── scryfall/          # External API integrations
├── managers/
│   ├── db/
│   │   ├── manager.py     # Database coordination
│   │   └── services/      # CRUD operations (Card, Combo)
│   └── card_data/
│       └── manager.py     # Card fetching & caching logic
└── core/
    ├── manager_registry.py # Dependency injection
    └── interactor.py       # Application orchestration
```

### Layers Explained

1. **Domain Layer** (`domain/entities/`)
   - Pure business logic and entities
   - No dependencies on external systems
   - `Card`: Represents an MTG card with pricing, types, abilities
   - `Combo`: Represents a card combination with metadata

2. **Interface Layer** (`interfaces/scryfall/`)
   - External integrations
   - `ScryfallClient`: API client with rate limiting
   - Easy to swap for different data sources

3. **Service Layer** (`managers/db/services/`)
   - `BaseService`: Abstract CRUD interface
   - `CardService`: Card storage operations
   - `ComboService`: Combo storage operations
   - Currently uses JSON files (can swap to SQL/NoSQL later)

4. **Manager Layer** (`managers/`)
   - `DatabaseManager`: Coordinates all database services
   - `CardDataManager`: Orchestrates card fetching + caching
   - Business logic for data operations

5. **Core Layer** (`core/`)
   - `ManagerRegistry`: Service locator pattern for DI
   - `Interactor`: High-level use case orchestration
   - Entry point for application workflows

## Running the Demo

The `examples/data_layer_demo.py` demonstrates the complete architecture:

```bash
# Run the demo
python -m examples.data_layer_demo
```

### What the Demo Does

1. ✅ Initializes the entire architecture stack
2. ✅ Fetches sample MTG cards from Scryfall API
3. ✅ Stores cards in local JSON cache
4. ✅ Creates a famous combo (Isochron Scepter + Dramatic Reversal)
5. ✅ Searches for budget cards
6. ✅ Shows system statistics

### Expected Output

```
MTG Card App - Data Layer Architecture Demo
======================================================================

1. Initial System Stats
----------------------------------------------------------------------
Total cards in database: 0
Total combos in database: 0

2. Fetching Sample Cards from Scryfall
----------------------------------------------------------------------
Importing famous MTG combo pieces and staples...
Import Results:
  - Total: 11
  - Successful: 11
  - Failed: 0
  - Skipped (already exist): 0

3. Fetching Individual Cards
----------------------------------------------------------------------
Card: Sol Ring (2ED) - Artifact - $1.50
  Type: Artifact
  CMC: 1.0
  Colors: Colorless
  Price (USD): $1.50
  Text: {T}: Add {C}{C}...

4. Creating a Famous Combo
----------------------------------------------------------------------
Created combo: Dramatic Scepter (Infinite Mana): Isochron Scepter + Dramatic Reversal (infinite_mana) - $3.25
  Cards: ['Isochron Scepter', 'Dramatic Reversal']
  Total Price: $3.25
  Color Identity: []
  Description: Imprint Dramatic Reversal on Isochron Scepter...

5. Finding Budget Cards
----------------------------------------------------------------------
Found 10 cards under $5:
  - Sol Ring: $1.50
  - Lightning Bolt: $0.50
  - Counterspell: $0.25
  ...

6. Final System Stats
----------------------------------------------------------------------
Total cards in database: 11
Total combos in database: 1
Infinite combos: 1
Scryfall API requests made: 11
```

## Data Storage

The application stores data in JSON files (free, portable, version-controllable):

```
data/
├── cards.json   # All fetched MTG cards with pricing
└── combos.json  # User-created and discovered combos
```

### Card Data Structure

```json
{
  "cards": {
    "card-uuid-here": {
      "id": "uuid",
      "name": "Sol Ring",
      "mana_cost": "{1}",
      "cmc": 1.0,
      "type_line": "Artifact",
      "oracle_text": "{T}: Add {C}{C}.",
      "colors": [],
      "prices": {
        "usd": 1.50,
        "usd_foil": 3.00
      }
      ...
    }
  }
}
```

## Next Steps

Now that the data layer is complete, the next phases are:

### Phase 2: RAG Integration
- Add ChromaDB for vector storage
- Create embeddings for card text
- Implement semantic card search
- Enable "find similar combos" functionality

### Phase 3: LLM Integration  
- Set up Ollama with local LLaMA model (free)
- Create combo analysis service
- Auto-generate combo descriptions
- Detect card synergies using AI

### Phase 4: MCP Interface
- Build MCP server for natural language queries
- Enable queries like "find infinite mana combos under $50"
- Add conversational deck building

### Phase 5: Deck Builder
- Deck optimization algorithms
- Meta-game analysis
- Budget tracking
- Export to various formats

## Key Design Decisions

✅ **JSON Storage**: Simple, free, portable, version-controllable
✅ **Scryfall API**: Free, comprehensive, includes pricing
✅ **Modular Architecture**: Easy to test, swap components
✅ **Dependency Injection**: Via ManagerRegistry for flexibility
✅ **Layered Design**: Clear separation of concerns

## Architecture Benefits

1. **Testability**: Each layer can be tested independently
2. **Modularity**: Swap JSON for PostgreSQL? Just change the service
3. **Scalability**: Easy to add new managers/services
4. **Maintainability**: Clear responsibilities per layer
5. **Free-tier**: Uses only free resources (Scryfall + JSON)

## Questions or Next Steps?

The foundation is solid. We can now:
1. Add RAG for semantic search
2. Integrate LLM for combo analysis
3. Build out the MCP interface
4. Create the deck builder

Which would you like to tackle next?
