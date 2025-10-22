# MTG Card App - Architecture Flow

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / MCP CLIENT                        │
│                      (Natural Language Queries)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       INTERACTOR LAYER                           │
│                   (core/interactor.py)                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ High-Level Use Cases:                                     │  │
│  │  • fetch_card(name)                                       │  │
│  │  • create_combo(cards)                                    │  │
│  │  • find_combos_by_card(card)                             │  │
│  │  • get_budget_combos(max_price)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MANAGER REGISTRY                              │
│                (core/manager_registry.py)                        │
│                                                                   │
│         Dependency Injection & Service Location                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Database   │  │  Card Data   │  │  Scryfall    │         │
│  │   Manager    │  │   Manager    │  │   Client     │         │
│  └──────┬───────┘  └───────┬──────┘  └──────┬───────┘         │
└─────────┼───────────────────┼─────────────────┼─────────────────┘
          │                   │                 │
          ▼                   ▼                 ▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ DATABASE        │ │ CARD DATA        │ │ SCRYFALL        │
│ MANAGER         │ │ MANAGER          │ │ API             │
│                 │ │                  │ │                 │
│ Coordinates:    │ │ Orchestrates:    │ │ External API:   │
│ • CardService   │ │ • Caching        │ │ • Rate Limited  │
│ • ComboService  │ │ • Fetching       │ │ • Card Data     │
│                 │ │ • Price Updates  │ │ • Pricing       │
└────────┬────────┘ └─────────┬────────┘ └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│             (managers/db/services/)                          │
│                                                               │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CardSqliteService│  │ ComboService │  │ BaseService  │  │
│  │                  │  │              │  │  (Abstract)  │  │
│  │ CRUD for Cards   │  │ CRUD for     │  │              │  │
│  │ (SQLite)         │  │ Combo entities│  │ Interface    │  │
│  │                  │  │ (JSON)       │  │ for all      │  │
│  │ • create()       │  │ • create()   │  │ services     │  │
│  │ • get_by_id()    │  │ • search()   │  │              │  │
│  │ • get_by_name()  │  │ • get_budget │  │              │  │
│  │ • search()       │  │ • get_infin. │  │              │  │
│  │ • bulk_create()  │  │              │  │              │  │
│  └──────┬───────────┘  └──────┬───────┘  └──────────────┘  │
└─────────┼──────────────────────┼──────────────────────────────┘
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│                                                               │
│  ┌────────────────┐           ┌────────────────┐           │
│  │  cards.db      │           │  combos.json   │           │
│  │  (SQLite)      │           │  (JSON)        │           │
│  │                │           │                │           │
│  │ • 35k+ cards   │           │ {              │           │
│  │ • 6 indexes    │           │   "combos": {  │           │
│  │ • <1ms lookups │           │     "id": {    │           │
│  │ • Case-        │           │       ...      │           │
│  │   insensitive  │           │     }          │           │
│  │   search       │           │   }            │           │
│  │                │           │ }              │           │
│  └────────────────┘           └────────────────┘           │
└─────────────────────────────────────────────────────────────┘
          ▲                              ▲
          │                              │
          └──────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                              │
│              (domain/entities/)                              │
│                                                               │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │  Card Entity           │  │  Combo Entity          │    │
│  │                        │  │                        │    │
│  │  Properties:           │  │  Properties:           │    │
│  │  • id, name            │  │  • id, name            │    │
│  │  • mana_cost, cmc      │  │  • card_ids[]          │    │
│  │  • type_line           │  │  • combo_types[]       │    │
│  │  • oracle_text         │  │  • total_price         │    │
│  │  • colors[]            │  │  • description         │    │
│  │  • prices{}            │  │  • prerequisites[]     │    │
│  │  • image_uris{}        │  │                        │    │
│  │                        │  │  Methods:              │    │
│  │  Methods:              │  │  • is_infinite()       │    │
│  │  • from_scryfall()     │  │  • is_budget()         │    │
│  │  • is_creature()       │  │  • calculate_price()   │    │
│  │  • get_price()         │  │                        │    │
│  └────────────────────────┘  └────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### Example 1: Fetching a Card

```
User -> fetch_card("Sol Ring")
  │
  ├─> Interactor.fetch_card()
  │    │
  │    ├─> ManagerRegistry.card_data_manager
  │    │    │
  │    │    ├─> CardDataManager.get_card()
  │    │    │    │
  │    │    │    ├─> CardService.get_by_name() [Check cache]
  │    │    │    │    ├─> NOT FOUND
  │    │    │    │
  │    │    │    ├─> ScryfallClient.get_card_by_name() [Fetch from API]
  │    │    │    │    └─> Returns raw Scryfall JSON
  │    │    │    │
  │    │    │    ├─> Card.from_scryfall() [Convert to entity]
  │    │    │    │
  │    │    │    └─> CardService.create() [Cache for next time]
  │    │    │
  │    │    └─> Returns Card entity
  │    │
  │    └─> Returns Card to user
```

### Example 2: Creating a Combo

```
User -> create_combo(["Card A", "Card B"])
  │
  ├─> Interactor.create_combo()
  │    │
  │    ├─> Fetch each card (see Example 1)
  │    │
  │    ├─> Create Combo entity
  │    │    ├─> Set card_ids
  │    │    ├─> Calculate total price
  │    │    └─> Determine color identity
  │    │
  │    ├─> ManagerRegistry.db_manager
  │    │    │
  │    │    └─> ComboService.create()
  │    │         └─> Writes to combos.json
  │    │
  │    └─> Returns created Combo
```

### Example 3: Searching Budget Combos

```
User -> get_budget_combos(max_price=50.0)
  │
  ├─> Interactor.get_budget_combos()
  │    │
  │    ├─> ManagerRegistry.db_manager
  │    │    │
  │    │    └─> ComboService.search({"max_price": 50.0})
  │    │         │
  │    │         ├─> Read combos.json
  │    │         ├─> Filter by total_price <= 50.0
  │    │         └─> Return matching Combo entities
  │    │
  │    └─> Returns List[Combo]
```

## Dependency Flow

```
┌─────────────┐
│ Interactor  │ (Uses)
└──────┬──────┘
       │
       ├──> ManagerRegistry (Gets from)
       │     │
       │     ├──> DatabaseManager
       │     │     └──> CardService, ComboService
       │     │
       │     ├──> CardDataManager
       │     │     ├──> CardService
       │     │     └──> ScryfallClient
       │     │
       │     └──> ScryfallClient
       │
       └──> Card, Combo entities
```

## Benefits of This Architecture

1. **Testability**
   - Each layer can be unit tested independently
   - Mock dependencies via ManagerRegistry
   
2. **Swappable Components**
   - Replace JSON storage with PostgreSQL? Just swap CardService
   - Replace Scryfall with MTGJSON? Just swap ScryfallClient
   
3. **Clear Boundaries**
   - Domain entities have no infrastructure dependencies
   - Services only know about storage
   - Managers orchestrate business logic
   
4. **Dependency Injection**
   - ManagerRegistry provides central DI
   - Easy to configure different environments
   
5. **Scalability**
   - Add new managers/services without changing existing code
   - Add new entity types following same patterns

## Future Additions to Architecture

```
┌──────────────────────┐
│ RAG Manager          │ (Coming in Phase 2)
│                      │
│ • VectorStore        │ <- ChromaDB for embeddings
│ • EmbeddingService   │ <- Sentence transformers
│ • SemanticSearch     │ <- Find similar combos
└──────────────────────┘

┌──────────────────────┐
│ LLM Manager          │ (Coming in Phase 3)
│                      │
│ • OllamaClient       │ <- Local LLaMA model
│ • ComboAnalyzer      │ <- Analyze synergies
│ • DescriptionGen     │ <- Generate descriptions
└──────────────────────┘

┌──────────────────────┐
│ MCP Server           │ (Coming in Phase 4)
│                      │
│ • NaturalLangParser  │ <- Parse user queries
│ • ConversationMgr    │ <- Track context
│ • ResponseFormatter  │ <- Format results
└──────────────────────┘
```
