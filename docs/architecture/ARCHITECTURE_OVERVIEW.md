# MTG Card App - Architecture Overview

**Last Updated:** October 21, 2025  
**Status:** Phase 5.1 Complete (SQLite Migration, 35k cards, Production Ready)  
**Purpose:** Complete architecture reference for Phase 6+ development

---

## Table of Contents

1. [Architecture Philosophy](#architecture-philosophy)
2. [Layer Overview](#layer-overview)
3. [Complete Component Inventory](#complete-component-inventory)
4. [Data Flow Patterns](#data-flow-patterns)
5. [Dependency Injection](#dependency-injection)
6. [Storage Architecture](#storage-architecture)
7. [Current Capabilities](#current-capabilities)
8. [Phase 6 Extension Points](#phase-6-extension-points)

---

## Architecture Philosophy

**Clean Architecture Principles:**
- **Domain-Driven Design:** Core entities (Card, Combo, Deck) have no infrastructure dependencies
- **Dependency Inversion:** High-level modules don't depend on low-level modules
- **Single Responsibility:** Each layer has one reason to change
- **Testability:** All dependencies injected, easily mockable

**Current State:** ✅ Architecture refactor complete (Phase 3.5)
- Interactor is the **single source of truth** for business logic
- ManagerRegistry provides dependency injection
- All services follow protocol-based design for easy swapping

---

## Layer Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                               │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ MCP Server   │  │ CLI          │  │ Web API      │          │
│  │ (Phase 4 ✅) │  │ (Phase 6 📋) │  │ (Phase 7 📋) │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                      Interactor                             │ │
│  │                                                             │ │
│  │  Single source of truth for all business logic:            │ │
│  │  • Card Operations (fetch, search, import, budget)         │ │
│  │  • Combo Operations (create, find, budget)                 │ │
│  │  • Deck Operations (build, validate, analyze, suggest)     │ │
│  │  • Query Operations (NL queries, semantic search)          │ │
│  │  • System Operations (stats, initialization)               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    DEPENDENCY INJECTION                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   ManagerRegistry                           │ │
│  │                                                             │ │
│  │  Service Locator Pattern:                                  │ │
│  │  • Lazy initialization of managers                         │ │
│  │  • Singleton instance                                      │ │
│  │  • Provides: interactor, mcp_manager,                      │ │
│  │              card_data_manager, rag_manager, llm_manager,  │ │
│  │              db_manager, deck_builder_manager              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  DependencyManager                          │ │
│  │                                                             │ │
│  │  Service Container:                                         │ │
│  │  • Creates service instances                               │ │
│  │  • Manages configuration (data_dir, etc.)                  │ │
│  │  • Allows service substitution for testing                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    MANAGER LAYER                                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ CardData     │  │ RAG          │  │ LLM          │          │
│  │ Manager      │  │ Manager      │  │ Manager      │          │
│  │              │  │              │  │              │          │
│  │ • Caching    │  │ • Embeddings │  │ • Prompts    │          │
│  │ • Fetching   │  │ • Semantic   │  │ • Generation │          │
│  │ • Prices     │  │   search     │  │ • Ollama     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Database     │  │ DeckBuilder  │  │ MCP          │          │
│  │ Manager      │  │ Manager      │  │ Manager      │          │
│  │              │  │              │  │              │          │
│  │ • Card       │  │ • Build      │  │ • Protocol   │          │
│  │   service    │  │ • Validate   │  │ • JSON-RPC   │          │
│  │ • Combo      │  │ • Analyze    │  │ • Tools      │          │
│  │   service    │  │ • Suggest    │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    SERVICE LAYER                                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ CardSqlite   │  │ ComboService │  │ Scryfall     │          │
│  │ Service      │  │ (JSON)       │  │ CardData     │          │
│  │              │  │              │  │ Service      │          │
│  │ • CRUD       │  │ • CRUD       │  │              │          │
│  │ • Indexes    │  │ • Search     │  │ • Fetch      │          │
│  │ • Bulk ops   │  │ • Filter     │  │ • Rate limit │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Sentence     │  │ Chroma       │  │ Ollama       │          │
│  │ Transformer  │  │ VectorStore  │  │ LLM          │          │
│  │ Embedding    │  │ Service      │  │ Service      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    STORAGE & EXTERNAL                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ cards.db     │  │ combos.json  │  │ chroma/      │          │
│  │ (SQLite)     │  │              │  │ (ChromaDB)   │          │
│  │              │  │              │  │              │          │
│  │ • 35,402     │  │ • Custom     │  │ • Card       │          │
│  │   cards      │  │   combos     │  │   embeddings │          │
│  │ • 6 indexes  │  │ • Searchable │  │ • HNSW index │          │
│  │ • <1ms       │  │              │  │ • <5ms       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ Scryfall API │  │ Ollama       │                             │
│  │ (External)   │  │ (Local)      │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Component Inventory

### Core (Business Logic)

**`core/interactor.py`** - ✅ **Single Source of Truth**
- All business logic methods (16 public methods)
- Coordinates between managers
- No direct service dependencies
- Fully tested (169 unit tests passing)

**`core/manager_registry.py`** - Service Locator
- Lazy initialization of all managers
- Singleton pattern
- Properties: `interactor`, `card_data_manager`, `rag_manager`, `llm_manager`, `db_manager`, `deck_builder_manager`, `mcp_manager`

**`core/dependency_manager.py`** - Service Container
- Creates service instances with configuration
- Allows service substitution for testing
- Manages: card_data_service, embedding_service, vector_store_service, llm_service, query_cache

### Managers (Orchestration)

**`managers/card_data/manager.py`** - CardDataManager
- Coordinates card fetching and caching
- Methods: `get_card()`, `search_cards()`, `import_cards()`, `get_budget_cards()`, `refresh_prices()`
- Uses: CardService (SQLite), ScryfallCardDataService

**`managers/rag/manager.py`** - RAGManager
- Semantic search using vector embeddings
- Methods: `add_card()`, `search_similar()`, `update_card()`, `delete_card()`, `get_stats()`
- Uses: EmbeddingService (SentenceTransformers), VectorStoreService (ChromaDB)
- Performance: <5ms search, 50 cards/sec embedding

**`managers/llm/manager.py`** - LLMManager
- LLM prompt orchestration
- Methods: `generate()`, `generate_stream()`, `get_stats()`
- Uses: LLMService (Ollama)
- Current: Llama3 model, local inference

**`managers/db/manager.py`** - DatabaseManager
- Database coordination
- Properties: `card_service`, `combo_service`
- Initializes services with data directory

**`managers/deck/manager.py`** - DeckBuilderManager
- Deck construction and analysis
- Methods: `build_deck()`, `validate_deck()`, `analyze_deck()`, `suggest_cards()`, `export_deck()`
- Advanced: 10-factor combo ranking, LLM explanations

**`interfaces/mcp/manager.py`** - MCPManager
- MCP protocol server
- Methods: Tool registration, request handling, JSON-RPC dispatch
- Wraps Interactor for external access

### Services (Implementation)

**Card Data:**
- `managers/db/services/card_sqlite_service.py` - SQLite CRUD (production)
- `managers/db/services/card_service.py` - JSON CRUD (legacy)
- `managers/card_data/services/scryfall_service.py` - Scryfall API client

**Combo Data:**
- `managers/db/services/combo_service.py` - JSON CRUD with advanced search

**RAG:**
- `managers/rag/services/embedding_service.py` - SentenceTransformer embeddings
- `managers/rag/services/chroma_service.py` - ChromaDB vector store

**LLM:**
- `managers/llm/services/ollama_service.py` - Ollama client

**MCP:**
- `interfaces/mcp/services/stdio_service.py` - Stdio transport
- `interfaces/mcp/services/jsonrpc_service.py` - JSON-RPC protocol

### Domain Entities

**`domain/entities/card.py`** - Card Entity
- Properties: id, name, mana_cost, cmc, type_line, oracle_text, colors, prices, etc.
- Methods: `from_scryfall()`, `is_creature()`, `get_primary_price()`, `to_dict()`
- No infrastructure dependencies

**`domain/entities/combo.py`** - Combo Entity
- Properties: id, name, card_ids, card_names, total_price, combo_types, tags, etc.
- Methods: `is_infinite()`, `is_budget()`, `calculate_total_price()`, `to_dict()`
- Enums: ComboType (infinite_mana, infinite_damage, etc.)

**`domain/entities/deck.py`** - Deck Entity
- Properties: format, cards, commander, sections, metadata
- Methods: `to_dict()`, `from_dict()`

### Utilities

**`utils/query_cache.py`** - QueryCache
- LRU cache for query results
- 18.58x average speedup on repeated queries
- Methods: `get()`, `set()`, `clear()`, `stats()`

**`utils/suggestion_cache.py`** - SuggestionCache
- Caches RAG and combo results for deck suggestions
- 78.1% hit rate
- Significantly faster deck building

---

## Data Flow Patterns

### Pattern 1: Natural Language Query

```
User: "show me blue counterspells under $5"
  │
  ├─> CLI/MCP/Web → Interactor.answer_natural_language_query()
  │
  ├─> Interactor._extract_filters(query)
  │    └─> LLMManager.generate() → {colors: "U", max_cmc: ...}
  │
  ├─> RAGManager.search_similar(query, filters=...)
  │    ├─> EmbeddingService.embed(query) → [0.23, -0.45, ...]
  │    └─> VectorStoreService.search(embedding, filters) → [(card_id, score), ...]
  │
  ├─> CardDataManager.get_card_by_id(card_id) for each result
  │    └─> CardSqliteService.get_by_id(card_id) → Card entity
  │
  └─> LLMManager.generate(formatting_prompt) → Formatted response
```

### Pattern 2: Combo Discovery

```
User: "find combos with Isochron Scepter"
  │
  ├─> CLI/MCP/Web → Interactor.find_combo_pieces()
  │
  ├─> CardDataManager.get_card("Isochron Scepter")
  │    └─> CardSqliteService.get_by_name() → Card entity
  │
  ├─> Interactor._build_combo_query(card)
  │    └─> Analyzes oracle text, type line, mechanics
  │
  ├─> RAGManager.search_similar(combo_query)
  │    └─> Returns semantically similar cards
  │
  ├─> CardDataManager.get_card_by_id() for each result
  │
  └─> LLMManager.generate(combo_analysis_prompt)
       └─> Explains synergies, power level, requirements
```

### Pattern 3: Deck Building with AI Suggestions

```
User: "suggest cards for my Muldrotha deck"
  │
  ├─> CLI/MCP/Web → Interactor.suggest_cards(deck, constraints)
  │
  ├─> DeckBuilderManager.suggest_cards(deck, constraints)
  │    │
  │    ├─> RAGManager.search_similar(theme_query)
  │    │    └─> Returns relevant cards based on theme
  │    │
  │    ├─> For each suggestion:
  │    │    ├─> Check synergy with deck colors
  │    │    ├─> Check budget constraints
  │    │    └─> Find combos with deck cards + commander
  │    │         └─> DatabaseManager.combo_service.search(...)
  │    │
  │    ├─> Rank combos (10-factor algorithm):
  │    │    • Archetype fit, commander synergy, color overlap
  │    │    • Budget fit, power level, complexity
  │    │    • Assembly ease, disruptibility, infinite boost
  │    │    • Popularity
  │    │
  │    └─> (Optional) LLMManager.generate(explanation_prompt)
  │         └─> Generate human-readable combo explanations
  │
  └─> Returns sorted suggestions with combo data
```

---

## Dependency Injection

### How It Works

```python
# 1. Application startup
registry = ManagerRegistry.get_instance()

# 2. Registry lazily creates managers on first access
card_data_manager = registry.card_data_manager  # Created here
rag_manager = registry.rag_manager              # Created here
llm_manager = registry.llm_manager              # Created here

# 3. Registry creates Interactor with all dependencies
interactor = registry.interactor  # Gets all managers above

# 4. Interfaces use Interactor
mcp_server = registry.mcp_manager  # Gets interactor
```

### Testing with Dependency Injection

```python
# Unit test: Mock specific service
def test_fetch_card():
    # Create mock service
    mock_card_service = Mock(spec=CardService)
    mock_card_service.get_by_name.return_value = test_card
    
    # Inject mock
    deps = DependencyManager(card_service=mock_card_service)
    registry = ManagerRegistry(dependencies=deps)
    interactor = registry.interactor
    
    # Test
    result = interactor.fetch_card("Test Card")
    assert result == test_card
```

### Service Substitution

```python
# Use SQLite (production)
deps = DependencyManager(
    data_dir="data",
    card_service_type="sqlite"  # Default
)

# Use JSON (testing/legacy)
deps = DependencyManager(
    data_dir="test_data",
    card_service_type="json"
)

# Use custom implementation
deps = DependencyManager(
    card_data_service=CustomScryfallService()
)
```

---

## Storage Architecture

### SQLite Database (cards.db)

**Schema:**
```sql
CREATE TABLE cards (
    id TEXT PRIMARY KEY,
    oracle_id TEXT,
    name TEXT NOT NULL COLLATE NOCASE,
    mana_cost TEXT,
    cmc REAL,
    type_line TEXT,
    oracle_text TEXT,
    colors TEXT,          -- JSON array
    color_identity TEXT,  -- JSON array
    power TEXT,
    toughness TEXT,
    prices TEXT,          -- JSON object
    image_uris TEXT,      -- JSON object
    legalities TEXT,      -- JSON object
    rarity TEXT,
    set_code TEXT,
    collector_number TEXT,
    layout TEXT,
    -- ... more fields
);

-- 6 indexes for performance
CREATE INDEX idx_cards_name ON cards(name COLLATE NOCASE);
CREATE INDEX idx_cards_oracle_id ON cards(oracle_id);
CREATE INDEX idx_cards_colors ON cards(colors);
CREATE INDEX idx_cards_type_line ON cards(type_line);
CREATE INDEX idx_cards_cmc ON cards(cmc);
CREATE INDEX idx_cards_rarity ON cards(rarity);
```

**Performance:**
- 35,402 cards
- <1ms lookups (average 0.47ms)
- Case-insensitive search
- Bulk insert support (100 cards/sec)

### JSON Storage (combos.json)

**Schema:**
```json
{
  "combos": {
    "combo_id_1": {
      "id": "combo_id_1",
      "name": "Dramatic Scepter",
      "card_ids": ["card_uuid_1", "card_uuid_2"],
      "card_names": ["Isochron Scepter", "Dramatic Reversal"],
      "combo_types": ["infinite_mana"],
      "description": "Infinite mana combo...",
      "total_price_usd": 25.50,
      "colors_required": ["U"],
      "prerequisites": [...],
      "steps": [...]
    }
  }
}
```

**Why JSON for combos:**
- Flexible schema (combo structure evolves)
- Small dataset (<1000 combos expected)
- Easy manual editing
- Fast enough for current scale

### Vector Database (chroma/)

**Storage:**
- ChromaDB persistent storage
- HNSW index for fast similarity search
- 384-dimensional embeddings (all-MiniLM-L6-v2)
- ~40 KB per card (includes index overhead)

**Performance:**
- <5ms similarity search
- Scales to 100k+ cards
- Automatic persistence

---

## Current Capabilities

### Interactor Public Methods (16 total)

**Card Operations (6):**
1. `fetch_card(name)` - Get single card by name
2. `search_cards(query, use_scryfall)` - Search with Scryfall syntax
3. `import_cards(card_names)` - Bulk import from Scryfall
4. `get_budget_cards(max_price)` - Find cards under price
5. `answer_natural_language_query(query)` - RAG + LLM query answering
6. `find_combo_pieces(card_name, n_results)` - Semantic combo discovery

**Combo Operations (3):**
7. `create_combo(card_names, name, description)` - Manual combo creation
8. `find_combos_by_card(card_name)` - Find existing combos with card
9. `get_budget_combos(max_price)` - Find combos under price

**Deck Operations (5):**
10. `build_deck(format, card_pool, commander, constraints, metadata)` - Construct deck
11. `validate_deck(deck)` - Check format legality
12. `analyze_deck(deck)` - Mana curve, type distribution, weaknesses
13. `suggest_cards(deck, constraints)` - AI-powered suggestions with combos
14. `export_deck(deck, format)` - Export to text/json/moxfield/mtgo/arena/archidekt

**System Operations (2):**
15. `get_system_stats()` - Card count, cache stats, service info
16. `initialize_with_sample_data()` - Load test data

### MCP Tools (Phase 4)

All Interactor methods exposed via MCP protocol:
- `query_cards` → answer_natural_language_query
- `search_cards` → search_cards
- `find_combo_pieces` → find_combo_pieces
- `build_deck` → build_deck
- `validate_deck` → validate_deck
- `analyze_deck` → analyze_deck
- `suggest_cards` → suggest_cards

---

## Phase 6 Extension Points

### Where to Add CLI Commands

**New CLI module structure:**
```
mtg_card_app/ui/cli/
├── main.py           # Entry point, router
├── chat.py           # Interactive chat mode
├── commands/
│   ├── search.py     # mtg search → Interactor.search_cards()
│   ├── card.py       # mtg card → Interactor.fetch_card()
│   ├── combo.py      # mtg combo find → Interactor.find_combo_pieces()
│   ├── deck.py       # mtg deck * → Interactor deck methods
│   ├── import.py     # mtg import → Interactor.import_cards()
│   ├── config.py     # mtg config → Read/write config.toml
│   └── stats.py      # mtg stats → Interactor.get_system_stats()
└── formatters/
    ├── card.py       # Format Card entities
    ├── combo.py      # Format Combo entities
    └── deck.py       # Format Deck entities
```

**Pattern:**
```python
# cli/commands/search.py
import click
from mtg_card_app.core.manager_registry import ManagerRegistry

@click.command()
@click.argument('query')
@click.option('--format', default='human', help='Output format')
def search(query, format):
    """Search for cards."""
    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor
    
    # Call Interactor method
    results = interactor.search_cards(query)
    
    # Format output
    if format == 'json':
        click.echo(json.dumps([c.to_dict() for c in results]))
    else:
        # Rich formatting
        for card in results:
            display_card(card)
```

### Where to Add LLM Providers

**New LLM provider structure:**
```
mtg_card_app/managers/llm/services/
├── base.py              # LLMService protocol
├── ollama_service.py    # Existing Ollama implementation
├── openai_service.py    # New: OpenAI provider
├── anthropic_service.py # New: Anthropic provider
├── gemini_service.py    # New: Google Gemini provider
└── groq_service.py      # New: Groq provider
```

**Pattern:**
```python
# llm/services/openai_service.py
from mtg_card_app.managers.llm.services.base import LLMService

class OpenAILLMService(LLMService):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
```

**Configuration:**
```toml
# ~/.mtg/config.toml
[llm]
provider = "openai"  # or "ollama", "anthropic", "gemini", "groq"

[llm.openai]
api_key = "${OPENAI_API_KEY}"
model = "gpt-4o-mini"

[llm.anthropic]
api_key = "${ANTHROPIC_API_KEY}"
model = "claude-3-5-sonnet-20241022"
```

### Where to Add Web API

**New web module structure:**
```
mtg_card_app/ui/web/
├── backend/
│   ├── app.py        # FastAPI app
│   ├── routes/
│   │   ├── cards.py  # GET /api/cards → Interactor methods
│   │   ├── combos.py # GET /api/combos → Interactor methods
│   │   ├── decks.py  # POST /api/decks → Interactor methods
│   │   └── chat.py   # WS /api/chat → Interactor.answer_nl_query()
│   └── middleware/
│       └── cors.py
└── frontend/
    └── (React app)
```

**Pattern:**
```python
# web/backend/routes/cards.py
from fastapi import APIRouter
from mtg_card_app.core.manager_registry import ManagerRegistry

router = APIRouter()

@router.get("/cards/{card_name}")
def get_card(card_name: str):
    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor
    
    card = interactor.fetch_card(card_name)
    return card.to_dict() if card else {"error": "Not found"}
```

---

## Key Architectural Decisions

### ✅ Completed Refactors

1. **Phase 3.5: Query Consolidation** (Oct 20, 2025)
   - Moved all query logic from QueryOrchestrator to Interactor
   - Interactor is now single source of truth for business logic
   - QueryOrchestrator removed (was causing architecture drift)

2. **Phase 5.1: SQLite Migration** (Oct 21, 2025)
   - Migrated from JSON to SQLite for card storage
   - 21.9x performance improvement (10.25ms → 0.47ms)
   - Kept JSON for combos (flexible schema, small dataset)

3. **Phase 4: MCP Integration** (Oct 2025)
   - MCP server wraps Interactor (clean architecture)
   - JSON-RPC protocol with schema validation
   - All Interactor methods exposed as tools

### 🎯 Design Patterns Used

- **Service Locator:** ManagerRegistry for accessing managers
- **Dependency Injection:** DependencyManager for service creation
- **Protocol-Oriented:** Services follow protocols for easy swapping
- **Repository Pattern:** Services encapsulate data access
- **Facade Pattern:** Managers simplify complex service interactions
- **Strategy Pattern:** Multiple LLM/storage implementations

---

## Performance Metrics

**Card Operations:**
- Card lookup: <1ms (SQLite indexed)
- Card search: <5ms (with indexes)
- Bulk import: 100 cards/sec

**Semantic Search:**
- Embedding generation: 20ms per card
- Similarity search: <5ms (ChromaDB HNSW)
- RAG query end-to-end: <100ms (warm cache)

**LLM Operations:**
- Ollama (local): 5-10s per query
- Query with cache hit: <1ms (18.58x speedup)

**Deck Operations:**
- Deck analysis: <50ms
- Deck suggestions (warm cache): ~18ms
- Deck suggestions (cold): 2-5s (depending on combos)

---

## Testing Strategy

**Unit Tests:** 169 passing
- Each manager tested in isolation
- Services mocked using protocols
- 100% coverage of Interactor public methods

**Integration Tests:** 18 passing
- End-to-end workflows
- Real services (test database)
- MCP protocol validation

**E2E Tests:** Available but slow (~30s each)
- Real Ollama LLM
- Real Scryfall API
- Marked with `@pytest.mark.e2e`

---

## Summary

**Current State:**
- ✅ Clean architecture with clear layers
- ✅ 35,402 cards in production database
- ✅ All business logic in Interactor (16 public methods)
- ✅ Dependency injection for testability
- ✅ Protocol-based services for flexibility
- ✅ MCP server for external access
- ✅ Performance optimized (<1ms card lookups)

**Ready for Phase 6:**
- All Interactor methods documented
- Clear extension points for CLI, LLM providers, Web UI
- Architecture supports parallel development (3 tracks)
- No technical debt blocking progress

**Next Steps:**
1. Implement CLI commands (wrap Interactor methods)
2. Add LLM provider abstraction (protocol-based)
3. Create installation system (Docker, pip, native)

---

**Document Status:** ✅ Complete and Current  
**Last Verified:** October 21, 2025  
**Confidence:** High - Reflects actual implemented code
