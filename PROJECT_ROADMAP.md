# MTG Card App - Complete Project Roadmap

**Updated:** October 21, 2025  
**Current Status:** Phase 4 In Progress 🚧 | All unit tests passing ✅

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
| 4 | MCP Interface | 🚧 In Progress | Model Context Protocol server |
| 5 | Deck Builder | ⏳ Future | AI-powered deck construction |
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

## 🚧 Phase 4: MCP Interface (In Progress)

For a concise status, see `PHASE_4_STATUS.md`.

### Completed in Phase 4 so far
- JSON-RPC stdio transport with MCP-style framing + tests
- Unified `MCPManager` dispatch (legacy + JSON-RPC) with JSON Schema validation
- Tools implemented: query_cards, search_cards, find_combo_pieces, explain_card, compare_cards
- initialize now advertises server version, capabilities, input schemas, and output schemas (e.g., for search_cards)
- History with timestamps, duration_ms, and request ids (legacy ids generated) + filtering API (tool, since, id, error_only)
- Official MCP adapter and CLI mode switch (`--server classic|official`, default classic)
- Classic CLI smoke validated (initialize + search_cards); MCP unit tests green (13)

### Remaining for Phase 4 completion
- Initialize polish: per-tool descriptions/examples; finalize capability fields
- Optional output validation toggle (enforce outputSchema at runtime)
- Align legacy error shape with JSON-RPC error objects
- Observability knobs (log level, history limits)
- E2E JSON-RPC tests per tool; performance notes
- Scale-up: import Oracle (unique) cards and vectorize full set

### Backlog / Nice-to-Have
- Claude Desktop integration guide, config, and smoke test (not required for Phase 4 completion)

### Scale-up steps (pre-Phase 5)
1) Import oracle_cards bulk from Scryfall to local DB (see `scripts/import_oracle_cards.py`)
2) Vectorize all cards (see `scripts/vectorize_cards.py`)
3) Verify RAG queries and performance at full scale

**ETA to finish Phase 4:** ~1–2 short work sessions

---

## ⏳ Phase 5: Deck Builder

**Goal:** AI-powered deck construction with constraints and recommendations

- Format constraints (Commander, Modern, Standard, etc.)
- Mana curve analysis
- Theme-based generation ("aristocrats", "voltron", "control")
- Commander synergies
- Missing piece identification
- Weakness detection
- Power level tuning (casual → competitive)
- Combo integration
- [ ] Synergy scores > threshold
- [ ] Mana curve is playable
- [ ] Can suggest meaningful upgrades
**Estimated Timeline:** 1-2 weeks

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

**Last Updated:** October 20, 2025  
**Next Review:** After Phase 4 completion  
**Status:** Phase 3 complete, Phase 4 ready to start 🚀
