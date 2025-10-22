# MTG Card App - Complete Project Roadmap

**Updated:** October 21, 2025  
**Current Status:** Phase 6 Tracks 1 & 2 Complete ✅ | 186 Tests Passing ✅ | Ready for Production ✅

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
| 6 | CLI & Infrastructure | ✅ Tracks 1-2 Complete | **Conversational CLI ✅, LLM providers ✅, Installation 📋** |
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

## ✅ Phase 6: CLI Interface & Infrastructure

**Goal:** Conversational CLI with LLM provider flexibility and easy installation

**Status:** Tracks 1 & 2 COMPLETE ✅ | Track 3 IN PLANNING 📋

For detailed planning, see:
- `docs/phases/PHASE_6_PLAN_V2.md` - Original plan
- `docs/phases/PHASE_6_TRACK_1_SUMMARY.md` - CLI implementation
- `docs/phases/PHASE_6_TRACK_2_SUMMARY.md` - LLM provider system

### Overview

**Primary Interface:** Conversational chat mode (like talking to Claude) ✅  
**Secondary Interface:** Direct commands for power users/scripting ✅  
**LLM Providers:** Ollama, OpenAI, Anthropic, Gemini, Groq ✅  
**Installation:** Docker 📋, pip/pipx (works from source) ✅, native packages 📋

### Three Parallel Development Tracks

#### ✅ Track 1: CLI Interface (COMPLETE)

**Implementation:**
- ✅ Interactive chat mode (Rich REPL with conversational UI)
- ✅ 11 direct commands (card, search, combo, deck, config, stats, setup, update)
- ✅ Rich terminal formatting (colors, tables, panels, progress bars)
- ✅ Multiple output formats (rich, text, JSON)

**Commands Implemented:**
```bash
mtg                    # Interactive chat mode (primary interface)
mtg card "name"        # Card details (rich/text/json)
mtg search "query"     # Natural language search
mtg combo find/search/budget/create  # Combo operations
mtg deck new/build/validate/analyze/suggest/export  # Deck operations
mtg config show/set/get/reset/providers  # Configuration management
mtg stats              # System statistics
mtg setup              # Interactive setup wizard (4 steps)
mtg update             # Download/update card database (with progress bars)
```

**Key Features:**
- Chat mode with conversation history and context
- Beautiful Rich terminal output with panels, tables, and progress bars
- Setup wizard with provider selection and data verification
- Update command with detailed progress (download, import, embeddings)
- Config system with TOML and environment variable support
- Multiple output formats for scripting

**Commits:**
- f7c4d5d - CLI framework and chat mode
- ab45138 - Card and search commands
- d367911 - Combo commands
- 9773e11 - Setup wizard (432 lines, 4-step process)
- d08a882, eade408 - Update command with progress bars (233 lines)

**Test Status:** CLI manually tested, all commands functional

#### ✅ Track 2: LLM Provider Abstraction (COMPLETE)

**Implementation:**
- ✅ 5 provider implementations (Ollama, OpenAI, Anthropic, Gemini, Groq)
- ✅ `LLMService` protocol for extensibility
- ✅ Configuration system (`~/.mtg/config.toml` + environment variables)
- ✅ Provider factory pattern
- ✅ Optional dependencies (install only what you need)
- ✅ Free tier options (Ollama local, Gemini, Groq)

**Architecture:**
```python
# Protocol-based service
class LLMService(Protocol):
    def generate(prompt: str) -> str: ...
    def generate_streaming(prompt: str) -> Iterator[str]: ...

# Provider implementations
- OllamaLLMService (local, free, always available)
- OpenAILLMService (optional: pip install [openai])
- AnthropicLLMService (optional: pip install [anthropic])
- GeminiLLMService (optional: pip install [gemini])
- GroqLLMService (optional: pip install [groq])

# Factory pattern
provider_factory.create_provider(config) -> LLMService
```

**Configuration:**
```toml
[llm]
provider = "ollama"
model = "llama3"
temperature = 0.7

[llm.openai]
api_key = "${OPENAI_API_KEY}"  # Environment variable expansion
```

**Test Status:** 50 unit tests (36 passing, 14 expected failures for optional deps)

#### 📋 Track 3: Installation & Setup (IN PLANNING)

**Remaining Work:**
- Docker image with pre-computed data (~100 MB: SQLite + ChromaDB)
- pip/pipx package improvements (currently works from source)
- Native installers (.dmg, .deb, .rpm, .exe)
- Pre-computed data bundle for faster setup
- Incremental updates for new cards
- CI/CD pipeline for releases

**Current Status:**
- ✅ Works from source with `pip install -e .`
- ✅ Setup wizard guides first-time configuration
- ✅ Update command downloads and processes data
- 📋 Package not yet published to PyPI
- 📋 Docker image not yet created
- 📋 Native installers not yet created

### Completed Features

**Conversational Mode:**
```bash
$ mtg
You: Show me blue counterspells under $5
Assistant: [Lists budget counters with prices and details]

You: What combos work with Thoracle?
Assistant: [Shows Thoracle + Consultation, Thoracle + Pact, etc.]

You: Build a Muldrotha deck with $200 budget
Assistant: [Generates optimized graveyard deck]
```

**Direct Commands:**
```bash
# Card operations
mtg card "Lightning Bolt"
mtg card "Sol Ring" --format json
mtg search "blue counterspells"

# Combo operations
mtg combo find "Isochron Scepter"
mtg combo search "Thoracle"
mtg combo budget 100
mtg combo create "Card A" "Card B"

# Deck operations
mtg deck new commander --commander "Muldrotha"
mtg deck build deck.txt --format commander --theme "graveyard"
mtg deck validate my_deck.json
mtg deck analyze my_deck.json
mtg deck suggest my_deck.json --budget 200 --combo-mode focused
mtg deck export my_deck.json arena

# Configuration
mtg config show
mtg config set llm.provider openai
mtg config providers

# System
mtg stats
mtg setup
mtg update
```

**Setup Wizard:**
```bash
$ mtg setup
# Step 1: Current configuration status
# Step 2: LLM provider selection (comparison table)
# Step 3: Data file verification
# Step 4: Connection testing
# ✓ Ready to use!
```

### Success Criteria

**Track 1 (CLI):**
- [x] ✅ Conversational chat works smoothly
- [x] ✅ All Interactor methods exposed via CLI
- [x] ✅ Beautiful, colorized output with Rich
- [x] ✅ Comprehensive help text
- [x] ✅ Progress bars for long operations
- [x] ✅ Interactive setup wizard
- [x] ✅ Data update command

**Track 2 (LLM Providers):**
- [x] ✅ Multiple LLM providers working (5 providers)
- [x] ✅ Provider protocol for extensibility
- [x] ✅ Configuration system (TOML + env vars)
- [x] ✅ Optional dependencies
- [x] ✅ Free tier options available
- [x] ✅ Provider comparison table
- [x] ✅ 50 unit tests (36 passing core tests)

**Track 3 (Installation) - IN PROGRESS:**
- [ ] 📋 Installation <5 minutes (currently ~10 min from source)
- [ ] 📋 Cross-platform packages (macOS, Linux, Windows)
- [ ] 📋 Docker image with pre-computed data
- [ ] 📋 pip/pipx package on PyPI
- [ ] 📋 Native installers

**Timeline:**
- Track 1: 2 weeks ✅ COMPLETE
- Track 2: 2 weeks ✅ COMPLETE  
- Track 3: Estimated 1-2 weeks 📋 NEXT

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
