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

**Goal:** Build Model Context Protocol server for AI assistant integration

### Progress so far
- Protocol layer scaffolded and wired to the business logic:
  - `MCPManager` orchestrates request dispatch to `Interactor`.
  - Service abstraction `MCPService` with stdio implementation `StdioMCPService`.
  - Entry point `interfaces/mcp/__main__.py` runs the stdio server loop via `ManagerRegistry`.
- Core tools implemented in dispatch (backed by Interactor):
  - `query_cards` → `Interactor.answer_natural_language_query`
  - `find_combo_pieces` → `Interactor.find_combo_pieces`
  - `search_cards` → `Interactor.search_cards`
- Dependency injection cleanup completed:
  - `Interactor` refactored to require explicit dependencies; no registry lookups.
  - `ManagerRegistry` is the sole wiring hub; circular imports eliminated.
- Tests updated and expanded:
  - Unit tests for MCP manager + stdio service.
  - All unit tests pass across the repo (60 passed on Oct 21, 2025).

### What’s working now
- Basic stdio-based MCP loop that reads a single-line JSON request and returns a JSON response.
- Tool dispatch to Interactor with real functionality and coverage by tests.
- Clean architecture preserved (thin interface layer, business logic in Interactor).

### Planned Features

#### 4.1: MCP Server Foundation
- Implement full MCP protocol specification (handshake, capabilities, JSON-RPC framing)
- Server lifecycle management
- Connection handling (stdio transport) [basic loop implemented]
- Structured error handling and logging

#### 4.2: Tool Registration
**Core Tools:**
- `query_cards` - Natural language card search
  - Input: query string, filters (optional)
  - Output: Formatted card results with explanations
  
- `find_combo_pieces` - Discover card combos
  - Input: card name, result limit
  - Output: Synergy analysis with power levels
  
- `search_cards` - Direct card lookup
  - Input: card name or ID
  - Output: Full card details

**Advanced Tools:**
- `explain_card` - Detailed card analysis
- `compare_cards` - Side-by-side comparison
- `suggest_alternatives` - Budget/power level alternatives

### Next steps (Phase 4)
1. Adopt the official MCP Python library and protocol framing:
  - Handshake/capabilities, JSON-RPC over stdio, tool registration metadata.
  - Keep `MCPManager` as the thin adapter to Interactor.
2. Define JSON Schemas for tool inputs/outputs and add validation.
3. Add session/conversation context in the MCP layer (history, follow-ups, state).
4. Improve error contract: structured error objects, error codes, and user-facing messages.
5. Implement advanced tools: `explain_card`, `compare_cards`, `suggest_alternatives`.
6. Observability: configurable logging, request IDs, timing, and debug toggles.
7. Claude Desktop integration:
  - Add setup docs and example config to register the server.
  - Run smoke tests and record example transcripts.
8. E2E tests for MCP:
  - Golden-path JSON-RPC sessions per tool, error-path cases, and schema checks.
9. Performance sanity checks and small load test for tool calls (<100ms target where feasible).

#### 4.3: Conversation Context
- Session management
- Query history tracking
- Context-aware responses
- Follow-up question handling

#### 4.4: Claude Desktop Integration
- Register as MCP server
- Test in Claude Desktop
- Configuration documentation
- Example conversations

### Success Criteria
- [ ] MCP server starts and accepts connections (per official spec)
- [ ] All core tools registered and working (with JSON Schemas)
- [ ] Claude Desktop can call tools successfully
- [ ] Conversation context maintains state
- [ ] Error handling provides helpful feedback
- [ ] Documentation for setup and usage
- [x] Basic stdio loop present with working dispatch (tests passing)

### Technical Requirements
- Follow MCP spec: https://modelcontextprotocol.io/
- Use `mcp` Python package
- Integrate with existing `Interactor`
- Add MCP-specific tests
- Performance: <100ms tool invocation

**Estimated Timeline:** 2-3 days

---

## ⏳ Phase 5: Deck Builder

**Goal:** AI-powered deck construction with constraints and recommendations

### Planned Features

#### 5.1: Deck Structure
- Deck entity and validation
- Format constraints (Commander, Modern, Standard, etc.)
- Mana curve analysis
- Color identity checking

#### 5.2: AI Deck Generation
- Budget-constrained building
- Theme-based generation ("aristocrats", "voltron", "control")
- Commander synergies
- Automatic land calculation

#### 5.3: Deck Analysis
- Synergy scoring
- Missing piece identification
- Weakness detection
- Upgrade suggestions

#### 5.4: Deck Optimization
- Budget upgrades (replace cards with better alternatives)
- Power level tuning (casual → competitive)
- Combo integration
- Sideboard suggestions

### Success Criteria
- [ ] Generate complete deck from theme/commander
- [ ] Respect budget constraints
- [ ] Format-legal decks only
- [ ] Synergy scores > threshold
- [ ] Mana curve is playable
- [ ] Can suggest meaningful upgrades

**Estimated Timeline:** 1-2 weeks

---

## ⏳ Phase 6: User Interfaces

**Goal:** Provide accessible interfaces for different use cases

### 6.1: CLI Interface (Command Line)

**Goal:** Simple, scriptable interface for power users

#### Planned Features
- **Interactive Mode**
  - REPL-style query interface
  - Command history
  - Tab completion
  - Colorized output
  
- **Commands**
  ```bash
  mtg query "blue counterspells under $5"
  mtg combo "Isochron Scepter"
  mtg search "Lightning Bolt"
  mtg deck build --commander "Muldrotha" --budget 200
  mtg deck analyze my_deck.txt
  ```

- **Configuration**
  - User preferences file
  - Default filters
  - Output formatting options
  - API key management

- **Output Formats**
  - Human-readable (default)
  - JSON (for scripting)
  - Markdown (for documentation)
  - CSV (for spreadsheets)

#### Technical Approach
- Use `click` or `typer` for CLI framework
- Integrate with `Interactor` directly
- Add `mtg_card_app/ui/cli/` module
- Entry point: `mtg` command
- Install via `pip install -e .`

#### Success Criteria
- [ ] All core operations available via CLI
- [ ] Rich, readable output
- [ ] Tab completion works
- [ ] Help system is comprehensive
- [ ] Scriptable for automation
- [ ] Cross-platform (Mac, Linux, Windows)

**Estimated Timeline:** 3-5 days

---

### 6.2: App Interface (GUI/Web)

**Goal:** Visual, user-friendly interface for casual users

#### Technology Options (TBD)

**Option A: Web Application**
- **Frontend:** React/Next.js or Svelte
- **Backend:** FastAPI server wrapping Interactor
- **Deployment:** Local (http://localhost:3000) or hosted
- **Pros:** Rich UI, familiar tech stack, easy sharing
- **Cons:** More complex architecture, requires web server

**Option B: Desktop Application**
- **Framework:** Electron + React or Tauri + Svelte
- **Integration:** Direct Python backend or REST API
- **Pros:** Native feel, offline-first, easy distribution
- **Cons:** Larger bundle size, platform builds

**Option C: Native Desktop (Python)**
- **Framework:** PyQt6 or tkinter
- **Integration:** Direct Interactor calls
- **Pros:** Simple architecture, no JS needed, fast
- **Cons:** Less modern UI, harder styling

**Option D: Terminal UI (TUI)**
- **Framework:** Textual or Rich
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
   - Trade suggestions

**Design Principles:**
- Mobile-responsive (if web)
- Dark mode support
- Fast, fluid interactions
- Accessible (keyboard nav, screen readers)
- Beautiful card imagery

#### Success Criteria
- [ ] Technology choice made and documented
- [ ] Search interface functional
- [ ] Combo explorer working
- [ ] Deck builder basic functionality
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
    └─────────┘ └──────┘ └─────┘ └─────┘
```

---

## Current Status Summary

### ✅ Completed (Phases 1-3)
- **57 tests passing** (all core functionality)
- **Clean architecture** with proper dependency injection
- **Semantic search** with ChromaDB
- **Natural language queries** with Ollama LLM
- **Combo detection** with AI analysis
- **Query caching** (18.58x speedup)
- **Filter extraction** (100% accuracy)
- **~50 cards embedded** and searchable

### 🎯 Next Up (Phase 4)
- **MCP server implementation**
- **Claude Desktop integration**
- **Tool registration** (query, combo, search)
- **Conversation context management**

### 🔮 Future (Phases 5-6)

## 🔮 Future (Phases 5-7)

### Phase 5: Deck Builder
- AI-powered deck construction and recommendations

### Phase 6: User Interfaces (UI)
- CLI interface for power users (Typer/Click)
- TUI (Textual, optional)
- App interface (technology TBD: Web, Desktop, or Native)
- Modular UI architecture for easy extension

### Phase 7: Distribution & Installation
- Docker image for universal deployment
- Native installers (PyInstaller/Briefcase) for Windows, macOS, Linux
- pip install via PyPI for Python users
- Maintain all three options for maximum versatility
- Clear documentation for each install method
- Automate builds and releases where possible

---

## Decision Points

### Phase 4 Decisions (Immediate)
- ✅ Use official `mcp` Python package
- ✅ Stdio transport (standard for MCP)
- ⏳ Session storage mechanism (in-memory vs persistent?)
- ⏳ Rate limiting strategy (if needed)

### Phase 6 Decisions (Future)
- ⏳ **App technology choice** - Web vs Desktop vs Native vs TUI
  - Consider: development speed, maintainability, user base
  - Recommend: Start with Web (FastAPI + React) for maximum reach
- ⏳ **Hosting strategy** - Local-only vs cloud deployment
- ⏳ **Authentication** - If multi-user, how to handle?

---

## Success Metrics

### Technical Metrics
- Test coverage: >90% (currently ~95%)
- Response time: <100ms for cached queries, <2s for LLM queries
- Uptime: 99.9% for MCP server
- Memory usage: <500MB typical operation

### User Metrics (Post-Phase 6)
- Query success rate: >95% (user gets useful results)
- User retention: Weekly active usage
- Query diversity: Users exploring beyond basic searches
- Deck builder adoption: >50% of users try it

---

## Documentation Needs

### Current Docs ✅
- Architecture diagrams and flow
- API documentation (protocols)
- Testing strategy and patterns
- Setup and environment configuration

### Needed Docs (Phase 4+)
- [ ] MCP server setup guide
- [ ] Claude Desktop integration tutorial
- [ ] Example conversations and queries
- [ ] Tool usage reference
- [ ] CLI user guide
- [ ] App user guide (when ready)
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
   
3. **Scope Creep** - Features balloon beyond MVP
   - Mitigation: Stick to phase plan, defer nice-to-haves

---

## Open Questions

1. **Phase 4:** How to handle long-running queries in MCP? (>30s LLM generation)
2. **Phase 5:** What deck formats to prioritize? (Commander, Modern, Standard?)
3. **Phase 6:** Single-user or multi-user? Affects architecture significantly
4. **Phase 6:** Monetization strategy? (Free, freemium, paid?) Affects hosting decisions
5. **General:** Should we support custom card databases? (proxies, custom formats)

---

## Contributing

This is currently a solo project, but architecture supports collaboration:
- Protocol-based design makes parallel development easy
- Test coverage ensures changes don't break existing features
- Documentation helps onboarding

Future: Consider opening to community contributions after Phase 6.

---

**Last Updated:** October 20, 2025  
**Next Review:** After Phase 4 completion  
**Status:** Phase 3 complete, Phase 4 ready to start 🚀
