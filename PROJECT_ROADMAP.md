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
| 6 | CLI & Infrastructure | 📋 Planning | Conversational CLI, LLM providers, Installation |
| 7 | Web UI | 📋 Future | Local web interface with chat + quick actions |

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

## 📋 Phase 6: CLI Interface & Infrastructure

**Goal:** Conversational CLI with LLM provider flexibility and easy installation

For detailed planning, see `docs/phases/PHASE_6_PLAN_V2.md`.

### Overview

**Primary Interface:** Conversational chat mode (like talking to Claude)  
**Secondary Interface:** Direct commands for power users/scripting  
**LLM Providers:** Ollama, OpenAI, Anthropic, Gemini, Groq  
**Installation:** Docker (instant), pip/pipx (5 min), native packages (5 min)

### Three Parallel Development Tracks

**Track 1: CLI Interface (Week 1-2)**
- Interactive chat mode (REPL with streaming responses)
- Direct commands (search, combo, deck, config, system)
- Rich terminal formatting (colors, tables, progress bars)
- Multiple output formats (human, JSON, markdown)

**Track 2: LLM Provider Abstraction (Week 1-2)**
- Support 5+ providers (Ollama, OpenAI, Anthropic, Gemini, Groq)
- Provider protocol for easy extension
- Configuration system (`~/.mtg/config.toml`)
- Free tier options (Ollama local, Gemini, Groq)

**Track 3: Installation & Setup (Week 2-3)**
- Pre-computed data bundle (~100 MB: SQLite + ChromaDB embeddings)
- Docker image with everything pre-installed
- pip/pipx package with setup wizard
- Native installers (.dmg, .deb, .rpm, .exe)
- Incremental updates for new cards

### Key Features

**Conversational Mode:**
```bash
$ mtg
> show me blue counterspells under $5
> what combos work with Thoracle?
> build a Muldrotha deck with $200 budget
```

**Direct Commands:**
```bash
mtg search "Lightning Bolt"
mtg combo find "Isochron Scepter" --limit 5
mtg deck build --commander "Muldrotha" --budget 200
mtg deck suggest my_deck.txt --theme "graveyard" --explain-combos
mtg config set llm.provider openai
mtg stats
```

**Setup Wizard:**
```bash
mtg setup
# 1. Download pre-computed data (100 MB)
# 2. Choose LLM provider (Ollama, OpenAI, etc.)
# 3. Test connection
# ✓ Ready to use in 2-5 minutes
```

### Success Criteria
- [ ] ✅ Conversational chat works smoothly
- [ ] ✅ All Interactor methods exposed via CLI
- [ ] ✅ Multiple LLM providers working
- [ ] ✅ Installation <5 minutes
- [ ] ✅ Beautiful, colorized output
- [ ] ✅ Comprehensive help text
- [ ] ✅ Cross-platform (macOS, Linux, Windows)

**Estimated Timeline:** 2-3 weeks

---

## 📋 Phase 7: Web UI

**Goal:** Local web interface mirroring CLI's conversational-first design

For detailed planning, see `docs/phases/PHASE_7_PLAN.md`.

### Overview

**Primary Interface:** Chat interface (like Claude web UI)  
**Secondary Interface:** Quick action buttons  
**Hosting:** Local-only at `localhost:3000` or `mtg.local:3000`  
**Tech Stack:** FastAPI backend + React frontend + Tailwind + shadcn/ui

### Core Features

**Chat Interface:**
- Text input with streaming LLM responses
- Conversation history
- Inline card previews with action buttons
- Markdown rendering

**Quick Action Buttons:**
- Search Cards
- Find Combos
- Build Deck
- Analyze Deck
- System Stats

**Card Display:**
- Grid/list views
- Detail modal
- Lazy-loaded images
- Add to deck, find combos

**Deck Builder:**
- Drag-and-drop editor
- Visual mana curve
- Budget tracker
- AI-powered suggestions
- Export to moxfield/arena/json

**Settings Panel:**
- LLM provider selection
- API key management
- Light/dark theme
- Cache settings

### Implementation

**Backend (FastAPI):**
- REST API for cards, combos, decks
- WebSocket for streaming chat
- Wraps existing Interactor

**Frontend (React):**
- Vite + TypeScript
- Tailwind CSS + shadcn/ui components
- Responsive design (mobile/tablet/desktop)

**Startup:**
```bash
mtg web
# Opens http://localhost:3000 in browser
# Backend runs on http://localhost:8000 (proxied)
```

### Success Criteria
- [ ] ✅ Chat interface works smoothly
- [ ] ✅ Streaming responses feel instant
- [ ] ✅ All Interactor methods accessible
- [ ] ✅ Beautiful card display
- [ ] ✅ Intuitive deck builder
- [ ] ✅ Responsive on all devices
- [ ] ✅ Dark mode support
- [ ] ✅ <100ms UI interactions

**Estimated Timeline:** 3-4 weeks

---

## Architectural Flow (Phase 7 Complete)

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interfaces                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐  │
│  │   CLI    │  │ MCP API  │  │  Web UI (localhost:3000)     │  │
│  │  (Chat+  │  │ (Claude) │  │  • Chat Interface            │  │
│  │Commands) │  │          │  │  • Quick Actions             │  │
│  └────┬─────┘  └────┬─────┘  │  • Deck Builder              │  │
│       │             │         └──────────┬───────────────────┘  │
└───────┼─────────────┼────────────────────┼──────────────────────┘
        │             │                    │
        └─────────────┼────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      Interactor           │
        │  (Business Logic Layer)   │
        │  • Card Operations        │
        │  • Combo Operations       │
        │  • Deck Operations        │
        │  • Query Orchestration    │
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
        └──┬─────┬──────┬──────┬───┬┘
           │     │      │      │   │
    ┌──────▼─┐ ┌─▼───┐ ┌▼───┐ ┌▼──▼┐
    │CardData│ │ RAG │ │LLM │ │Deck│
    │Manager │ │ Mgr │ │Mgr │ │Mgr │
    │        │ │     │ │    │ │    │
    │SQLite  │ │Chroma│ │Multi│ │   │
    │35k cards│ │DB  │ │Prov│ │   │
    └────────┘ └─────┘ └────┘ └────┘
```

---

- **Query caching** (18.58x speedup)
- **Filter extraction** (100% accuracy)
- **Claude Desktop integration**
- **Tool registration** (query, combo, search)
- **Conversation context management**

---

## 🔮 Future Enhancements

### Phase 6.1: Windows Support
- Native Windows installer (.exe)
- PowerShell setup script
- Windows Terminal formatting

### Phase 7.1: Advanced Web Features
- Multi-user support with authentication
- Collection manager (track owned cards)
- Visual combo graph (interactive)
- Price alerts and tracking

### Phase 7.2: Mobile & Offline
- Progressive Web App (PWA)
- Offline mode with service workers
- Mobile-optimized UI

### Phase 7.3: Desktop App
- Electron wrapper for native desktop
- Auto-updates
- System tray integration

### Phase 8: Community Features
- Share decks publicly
- Deck ratings and comments
- Popular deck library
- Community combo database

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

1. **Phase 6:** Which LLM provider should be default? (Ollama for privacy vs Gemini for speed)
2. **Phase 6:** Support Windows in initial release or Phase 6.1?
3. **Phase 7:** Multi-user support in Phase 7 or defer to 7.1?
4. **Phase 7:** PWA/offline mode in Phase 7 or defer to 7.2?
5. **General:** Should we support custom card databases? (proxies, custom formats)

---

- Protocol-based design makes parallel development easy
- Test coverage ensures changes don't break existing features
- Documentation helps onboarding
Future: Consider opening to community contributions after Phase 6.

---

**Last Updated:** October 21, 2025  
**Next Review:** After Phase 6 implementation  
**Status:** Phase 5.1 complete! Planning Phase 6 (CLI) and Phase 7 (Web UI) 🚀
