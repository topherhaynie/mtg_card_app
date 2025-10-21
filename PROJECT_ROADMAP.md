# MTG Card App - Complete Project Roadmap

**Updated:** October 21, 2025  
**Current Status:** Phase 5.1 Complete ✅ | Performance Optimized ✅ | All 92 unit tests passing ✅

---

## Project Vision

Build an intelligent MTG assistant that combines semantic search, LLM reasoning, and conversational interfaces to help players discover cards, build decks, and explore combos through natural language interaction.

---

## Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 1 | Data Layer | ✅ Complete | Card/Combo entities, Scryfall API integration |
| 2 | RAG Integration | ✅ Complete | Embeddings, vector store, semantic search |
| 3 | LLM Integration | ✅ Complete | Natural language processing, combo analysis |
| 4 | MCP Interface | ✅ Complete | Model Context Protocol server |
| 5 | Deck Builder | ✅ Complete | AI-powered deck construction with combo detection |
| 6 | User Interfaces | ⏳ Future | CLI, TUI, and App interfaces |
| 7 | Distribution & Installation | ⏳ Future | Multi-platform install: Docker, native, pip |

---

## ✅ Phase 1: Data Layer Foundation

**Goal:** Establish domain models and data access patterns

### Completed Features
- **Domain Entities**
  - `Card` - Comprehensive MTG card representation
  - `Combo` - Card combo with prerequisites and steps
  
- **Card Data Management**
  - `CardDataManager` - Orchestrates card operations
  - `ScryfallCardDataService` - Scryfall API integration
  - Protocol-based design for flexibility

- **Database Layer**
  - `DatabaseManager` - SQLite persistence
  - Card caching and local storage
  - Schema versioning support

### Key Achievements
- Clean architecture with domain separation
- Type-safe throughout
- Protocol-based services for easy extension
- Real data access to 26,000+ MTG cards

**Status:** ✅ Complete (57 tests passing)

---

## ✅ Phase 2: RAG Integration

**Goal:** Add semantic search capabilities using vector embeddings

### Completed Features
- **Embedding System**
  - `EmbeddingManager` with sentence-transformers
  - `all-MiniLM-L6-v2` model (384-dimensional)
  - Batch processing for efficiency
  
- **Vector Storage**
  - `ChromaVectorStoreService` with ChromaDB
  - Persistent storage in `data/chroma/`
  - HNSW indexing for fast similarity search
  
- **RAG Manager**
  - Semantic search across card database
  - Filtered search (colors, CMC, types)
  - Duplicate detection
  - Performance: <5ms search, 50 cards/sec embedding

### Key Achievements
- Find cards by meaning, not just keywords
- Scalable to 10,000+ cards
- Foundation for AI-enhanced queries
- Persistent embeddings (no re-computation)

**Status:** ✅ Complete (Phase 2A with ~50 cards)

**Optional Expansions:**
- Phase 2B: 1,000-3,000 popular cards
- Phase 2C: Full Oracle (~27,000 cards)

---

## ✅ Phase 3: LLM Integration

**Goal:** Add reasoning and natural language understanding

### Completed Features
- **LLM Infrastructure**
  - `LLMManager` for prompt orchestration
  - `OllamaLLMService` with Llama 3
  - Local inference (privacy-focused)
  
- **Query Intelligence**
  - Filter extraction from natural language
    - Colors: "blue", "Grixis", "mono-red"
    - CMC: "under 3 mana", "CMC 5 or less"
    - Types: "creatures", "instants", "artifacts"
  - Semantic query construction
  - Error handling and suggestions
  
- **Combo Analysis**
  - Semantic combo piece detection
  - LLM-powered synergy analysis
  - Power level assessment (casual → cEDH)
  - Additional pieces identification
  
- **Query Caching**
  - LRU cache (128 entries)
  - 18.58x average speedup
  - Filter-aware cache keys
  
- **Architecture Cleanup**
  - Consolidated query logic in `Interactor`
  - Proper dependency injection throughout
  - Clean separation: DependencyManager → ManagerRegistry → Interactor

### Key Achievements
- Natural language queries work end-to-end
- Combo detection with semantic search
- Fast repeated queries (caching)
- Clean, maintainable architecture
- 100% filter extraction accuracy (validation complete)

**Status:** ✅ Complete (56 tests passing)

---

## ✅ Phase 4: MCP Interface

For a concise status, see `PHASE_4_STATUS.md`.

### Completed Features
- JSON-RPC stdio transport with MCP-style framing + tests
- Unified `MCPManager` dispatch (legacy + JSON-RPC) with JSON Schema validation
- Tools implemented: query_cards, search_cards, find_combo_pieces, explain_card, compare_cards
- Deck builder tools: build_deck, validate_deck, analyze_deck, suggest_cards
- Initialize advertises server version, capabilities, input/output schemas, per-tool descriptions/examples
- History with timestamps, duration_ms, request ids + filtering API
- Official MCP adapter and CLI mode switch (`--server classic|official`, default classic)
- Classic CLI smoke validated; MCP unit tests passing

### Key Achievements
- Full MCP protocol compliance
- Rich tool schema documentation
- Performance tracking and debugging support
- Dual-mode operation (classic/official)
- Scale-up ready with Oracle card import

**Status:** ✅ Complete

---

## ✅ Phase 5: Deck Builder

**Goal:** AI-powered deck construction with constraints and recommendations

### Completed Features

**Core Deck Operations:**
- `build_deck`: Construct decks from card pools with format constraints
- `validate_deck`: Check legality, format rules, and card limits
- `analyze_deck`: Mana curve, type distribution, color analysis, weakness detection
- `suggest_cards`: AI-powered card recommendations with combo detection

**Advanced Suggestion System:**

1. **10-Factor Combo Ranking**
   - Archetype fit (+10): Matches deck theme/tags
   - Commander synergy (+15): Combo includes commander
   - Color identity overlap (+5 per match): Fits deck colors
   - Budget fit (+10 if under, penalty if over)
   - Power level fit (+8 if matching target)
   - Complexity bonus (+5 low, -3 high)
   - Assembly ease (+8 for 2-card, +4 for 3-card, penalty for 4+)
   - Disruptibility penalty (-2 per weakness)
   - Infinite combo boost (+12)
   - Popularity boost (+5 * score)

2. **Flexible User Controls**
   - `combo_mode`: "focused" (strict) or "broad" (all relevant)
   - `combo_limit`: Max combos per suggestion
   - `combo_types`: Filter by specific types (infinite_mana, engine, etc.)
   - `exclude_cards`: Exclude specific cards from combos
   - `sort_by`: Sort by power, price, popularity, or complexity
   - `explain_combos`: LLM-generated explanations

3. **Exhaustive Combo Detection**
   - Checks suggested card + deck cards
   - Checks suggested card + commander
   - Checks suggested card + other suggestions
   - Applies all filters (theme, format, colors, budget, legality)

4. **MCP & CLI Integration**
   - Exposed via MCP server tools
   - Full CLI with JSON constraint support
   - Programmatic API access

### Key Achievements
- Intelligent combo recommendations with 10-factor ranking
- Flexible constraint-based search
- LLM-powered insights
- Format-aware deck building
- Commander synergy detection
- Budget and power level optimization

**Status:** ✅ Complete (See `PHASE_5_ENHANCEMENTS.md` for details)

### 5.1: Performance Optimization & SQLite Migration ✅

**Goal:** Optimize card lookup performance for 35k+ card database

**Completed Features:**

1. **SQLite Migration**
   - Migrated 35,402 cards from JSON to SQLite
   - 6 indexes for fast lookups (name, oracle_id, colors, type_line, cmc, rarity)
   - Case-insensitive name search with `COLLATE NOCASE`
   - Bulk insert support for large datasets

2. **Performance Improvements**
   - **Card lookups:** 21.9x faster (10.25ms → 0.47ms average)
   - **Deck suggestions:** ~18ms with warm cache (was 20+ seconds)
   - **Overall speedup:** 1,111x improvement end-to-end

3. **Caching Infrastructure**
   - `SuggestionCache` for RAG and combo results
   - 78.1% cache hit rate on repeated queries
   - LRU eviction with TTL support

4. **Architecture Enhancements**
   - `CardSqliteService` with full CRUD operations
   - Manager abstraction via `BaseService[Card]`
   - Backward compatible (can switch between JSON/SQLite)

**Key Achievements:**
- Production-ready performance with 35k+ cards
- Scalable to 100k+ cards
- Sub-millisecond card lookups
- Excellent user experience (<5 second suggestions)

**Status:** ✅ Complete (See `SQLITE_MIGRATION_COMPLETE.md` for details)

---

## ⏳ Phase 6: User Interfaces

**Goal:** Provide accessible interfaces for different use cases

### 6.1: CLI Interface (Command Line)


#### Planned Features
- **Interactive Mode**
  - REPL-style query interface
  - Command history
  - Colorized output
  
- **Commands**
  ```bash
  mtg query "blue counterspells under $5"
  mtg combo "Isochron Scepter"
  mtg search "Lightning Bolt"
  mtg deck build --commander "Muldrotha" --budget 200
  ```

- **Configuration**
  - User preferences file
  - Default filters
  - API key management

- **Output Formats**
  - Human-readable (default)
  - JSON (for scripting)
  - Markdown (for documentation)
- Add `mtg_card_app/ui/cli/` module
- Entry point: `mtg` command
- [ ] Help system is comprehensive
- [ ] Scriptable for automation
- [ ] Cross-platform (Mac, Linux, Windows)
**Estimated Timeline:** 3-5 days

---

### 6.2: App Interface (GUI/Web)

**Goal:** Visual, user-friendly interface for casual users

- **Deployment:** Local (http://localhost:3000) or hosted
- **Pros:** Rich UI, familiar tech stack, easy sharing
- **Integration:** Direct Python backend or REST API
- **Pros:** Native feel, offline-first, easy distribution
- **Integration:** Direct Interactor calls
- **Pros:** Simple architecture, no JS needed, fast
- **Integration:** Direct Interactor calls
- **Pros:** Fast, works over SSH, lightweight
- **Cons:** Limited UI capabilities, ASCII-only

#### Planned Features (Regardless of Tech Choice)

**Core Views:**
1. **Search Interface**
   - Natural language query input
   - Filter sidebar (colors, CMC, types, price)
   - Card results grid/list
   - Card detail modal
   - Comparison mode

2. **Combo Explorer**
   - Card name input
   - Visual combo graph
   - Synergy explanations
   - Power level indicators
   - "Add to deck" button

3. **Deck Builder**
   - Deck editor with sections (Commander, Creatures, etc.)
   - Visual mana curve
   - Budget tracker
   - Synergy heatmap
   - Export to various formats (Arena, MTGO, PDF)

4. **Collection Manager** (Stretch)
   - Track owned cards
   - Value tracking
   - Want list
- Fast, fluid interactions
- Accessible (keyboard nav, screen readers)
- [ ] Responsive design (if web)
- [ ] Performance: <100ms interaction time
- [ ] User testing with 3+ people
**Estimated Timeline:** 2-4 weeks (depending on tech choice)

---

## Architectural Flow (Final State)

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                      │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐  │
│  │   CLI    │  │ MCP API  │  │   App (Web/Desktop) │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬──────────┘  │
└───────┼─────────────┼────────────────────┼─────────────┘
        │             │                    │
        └─────────────┼────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      Interactor           │
        │  (Business Logic Layer)   │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │    ManagerRegistry        │
        │  (Service Locator)        │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │   DependencyManager       │
        │  (Service Container)      │
        └──┬────────┬────────┬─────┬┘
           │        │        │     │
    ┌──────▼──┐ ┌──▼───┐ ┌──▼──┐ ┌▼────┐
    │CardData │ │ RAG  │ │ LLM │ │Cache│
    │Service  │ │Manager│ │Mgr  │ │     │
```

---

- **Query caching** (18.58x speedup)
- **Filter extraction** (100% accuracy)
- **Claude Desktop integration**
- **Tool registration** (query, combo, search)
- **Conversation context management**

### 🔮 Future (Phases 5-6)


### Phase 5: Deck Builder
- TUI (Textual, optional)
- App interface (technology TBD: Web, Desktop, or Native)
- Maintain all three options for maximum versatility
- Automate builds and releases where possible

---

- ✅ Stdio transport (standard for MCP)
- ⏳ Session storage mechanism (in-memory vs persistent?)

### Phase 6 Decisions (Future)
  - Recommend: Start with Web (FastAPI + React) for maximum reach
- ⏳ **Authentication** - If multi-user, how to handle?

---

- Response time: <100ms for cached queries, <2s for LLM queries
- Uptime: 99.9% for MCP server
- User retention: Weekly active usage
- Deck builder adoption: >50% of users try it

---

- API documentation (protocols)
- Testing strategy and patterns
- [ ] CLI user guide
- [ ] Deployment guide (if hosting)

---

## Risk Management

### Technical Risks
1. **LLM Hallucination** - LLM invents cards that don't exist
   - Mitigation: Always verify with database, show confidence scores
   
2. **Query Performance at Scale** - Slow with 10,000+ cards
   - Mitigation: Benchmark Phase 2B/2C, optimize indexing
   
3. **MCP Protocol Changes** - Spec is evolving
   - Mitigation: Pin to stable version, monitor updates
   
4. **Scryfall API Rate Limits** - 10 req/sec limit
   - Mitigation: Local caching, bulk downloads, respect rate limits

### Product Risks
1. **Unclear Value Prop** - Users don't see benefit over Scryfall
   - Mitigation: Focus on AI features (combos, deck building, conversation)
   
2. **Tech Choice Regret** - Wrong UI framework chosen
   - Mitigation: Start simple (web), can always migrate later
   
   - Mitigation: Stick to phase plan, defer nice-to-haves

---

## Open Questions

1. **Phase 4:** How to handle long-running queries in MCP? (>30s LLM generation)
2. **Phase 5:** What deck formats to prioritize? (Commander, Modern, Standard?)
3. **Phase 6:** Single-user or multi-user? Affects architecture significantly
5. **General:** Should we support custom card databases? (proxies, custom formats)

---

- Protocol-based design makes parallel development easy
- Test coverage ensures changes don't break existing features
- Documentation helps onboarding
Future: Consider opening to community contributions after Phase 6.

---

**Last Updated:** October 21, 2025  
**Next Review:** After Phase 6 planning  
**Status:** Phase 5 complete! Ready for UI enhancements 🚀
