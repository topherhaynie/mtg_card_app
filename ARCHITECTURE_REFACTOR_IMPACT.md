# Architecture Refactor Impact Analysis

**Date:** October 20, 2025  
**Topic:** QueryOrchestrator Refactoring & Phase 4 MCP Integration

---

## Current Architecture State

### What We've Built (Phases 1-3)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DependencyManager                             │
│  - CardDataService, EmbeddingService, VectorStoreService         │
│  - LLMService, QueryCache ✅ JUST ADDED                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ManagerRegistry                               │
│  - DatabaseManager, CardDataManager, RAGManager                  │
│  - LLMManager, QueryCache ✅ JUST ADDED                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Interactor                                 │
│  Business Logic:                                                 │
│  - fetch_card(), create_combo(), find_combos_by_card()          │
│  - answer_natural_language_query() ✅ JUST ADDED                │
│  - find_combo_pieces() ✅ JUST ADDED                            │
└─────────────────────────────────────────────────────────────────┘
```

### The Architecture Drift Problem

**QueryOrchestrator** was created as a separate workflow coordinator that:
- ❌ Bypasses `Interactor` (business logic layer)
- ❌ Directly instantiates `LLMManager` (not injectable)
- ❌ Directly instantiates `QueryCache` (not injectable)
- ✅ Uses `ManagerRegistry` for RAG/CardData (partial compliance)

**Current Usage:**
- `examples/orchestrator_demo.py` - Demo script
- `examples/combo_demo.py` - Combo finding demo
- `scripts/test_queries.py` - Query validation script
- `scripts/validate_polish.py` - Filter & cache validation
- `tests/unit/core/test_orchestrator_protocol.py` - Unit tests
- `tests/unit/core/test_orchestrator_filtering.py` - Filter tests
- `tests/unit/core/test_combo_detection.py` - Combo tests

---

## Phase 4: MCP Integration Vision

### What is MCP (Model Context Protocol)?

MCP is a **standardized protocol for AI assistants** to interact with external tools/data sources.

### Planned MCP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP CLIENT (Claude, GPT, etc.)              │
│                   Sends: Natural Language Queries                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP SERVER                                 │
│              (mtg_card_app/interfaces/mcp/)                      │
│                                                                   │
│  Responsibilities:                                               │
│  - Parse MCP protocol requests                                   │
│  - Map to application methods                                    │
│  - Format responses in MCP protocol                              │
│  - Handle conversation context                                   │
│  - Manage session state                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WHAT DOES MCP CALL?                           │
│                                                                   │
│  Option A: Call Interactor ✅ CLEAN ARCHITECTURE                │
│    mcp_server.answer_query() → Interactor.answer_nl_query()     │
│                                                                   │
│  Option B: Call QueryOrchestrator ⚠️ ARCHITECTURE DRIFT         │
│    mcp_server.answer_query() → QueryOrchestrator.answer_query() │
│                                                                   │
│  Option C: Call Both 🤔 CONFUSION                               │
│    When to use which?                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Refactoring Options & Impact Analysis

### Option 1: Make QueryOrchestrator a Thin Facade (RECOMMENDED)

**Approach:**
- Keep `QueryOrchestrator` as a **compatibility layer**
- Delegate all logic to `Interactor` methods
- Mark as `@deprecated` with timeline for removal
- All existing code continues working unchanged

**Implementation:**
```python
class QueryOrchestrator:
    """DEPRECATED: Use Interactor directly. This class will be removed in v2.0."""
    
    def __init__(self, registry: ManagerRegistry = None, llm_manager: LLMManager = None):
        """Initialize orchestrator with backward compatibility."""
        self.registry = registry or ManagerRegistry.get_instance()
        self.interactor = Interactor(registry=self.registry)
        # Store llm_manager for backward compat but don't use it
        self._llm_manager = llm_manager
    
    def answer_query(self, user_query: str) -> str:
        """Delegate to Interactor.answer_natural_language_query()."""
        return self.interactor.answer_natural_language_query(user_query)
    
    def find_combos(self, card_name: str, n_results: int = 5) -> str:
        """Delegate to Interactor.find_combo_pieces()."""
        return self.interactor.find_combo_pieces(card_name, n_results)
```

**Impact:**
- ✅ **Zero breaking changes** - All existing code works
- ✅ **Tests keep passing** - No test modifications needed
- ✅ **Examples keep working** - Demo scripts unchanged
- ✅ **Scripts keep working** - Validation scripts unchanged
- ✅ **Clean MCP integration** - MCP calls Interactor, not deprecated code
- ✅ **Gradual migration** - Can update callers over time
- ⚠️ **Extra indirection** - One more method call (minimal overhead)

**MCP Integration:**
```python
# MCP Server (Phase 4)
class MTGCardMCPServer:
    def __init__(self):
        self.interactor = Interactor()  # Call clean architecture
    
    def handle_card_query(self, query: str):
        return self.interactor.answer_natural_language_query(query)
```

---

### Option 2: Delete QueryOrchestrator, Update All Callers

**Approach:**
- Delete `core/orchestrator.py` entirely
- Update all 6 files that use it to call `Interactor` instead
- Update all 3 test files to test `Interactor` instead

**Impact:**
- ✅ **Cleanest architecture** - No deprecated code
- ✅ **Best for long-term** - Single source of truth
- ❌ **Breaking change** - Requires updating 9 files
- ❌ **Risk of bugs** - Each update could introduce issues
- ❌ **More testing needed** - Must verify all examples/scripts still work
- ⚠️ **Historical value lost** - QueryOrchestrator has unique features:
  - `_extract_filters()` - LLM-based filter extraction
  - `_build_combo_query()` - Semantic query construction
  - `_handle_no_results()` - User-friendly error messages

**Files to Update:**
1. `examples/orchestrator_demo.py` - Change to use Interactor
2. `examples/combo_demo.py` - Change to use Interactor
3. `scripts/test_queries.py` - Change to use Interactor
4. `scripts/validate_polish.py` - Change to use Interactor
5. `tests/unit/core/test_orchestrator_protocol.py` - Rename/refactor to test_interactor_query.py
6. `tests/unit/core/test_orchestrator_filtering.py` - Move to test_interactor_filtering.py
7. `tests/unit/core/test_combo_detection.py` - Move to test_interactor_combos.py
8. Delete `core/orchestrator.py`
9. Update any imports in `__init__.py` or docs

---

### Option 3: Keep Both (NOT RECOMMENDED)

**Approach:**
- Keep `QueryOrchestrator` with its current implementation
- Keep `Interactor` query methods separate
- Let them diverge over time

**Impact:**
- ❌ **Confusing** - Two ways to do the same thing
- ❌ **Maintenance burden** - Must update both when adding features
- ❌ **Bug risk** - Features/fixes might only go in one
- ❌ **MCP confusion** - Which one should MCP call?
- ❌ **Testing duplication** - Need tests for both

---

## Recommendation: Option 1 (Thin Facade)

### Why This is Best

1. **Zero Risk Migration**
   - All existing code continues working
   - No test updates needed
   - No example updates needed
   - Scripts continue validating correctly

2. **Clean MCP Integration**
   - MCP Server calls `Interactor` directly (clean architecture)
   - No need to understand deprecated QueryOrchestrator
   - Single source of truth for business logic

3. **Preserves Orchestrator Features**
   - Filter extraction logic still accessible (temporarily)
   - Can extract these methods to utilities if valuable
   - Example: `LLMFilterExtractor` utility class

4. **Gradual Migration Path**
   - Mark QueryOrchestrator as deprecated
   - Update documentation to recommend Interactor
   - Remove in v2.0 after Phase 4-5 complete
   - Gives users time to migrate

5. **Minimal Code Changes**
   - ~20 lines in `orchestrator.py`
   - ~5 lines in docstrings (deprecation notices)
   - ~0 lines in tests/examples/scripts

### What Unique Features Should We Extract?

QueryOrchestrator has some valuable logic that Interactor doesn't have:

1. **`_extract_filters()`** - LLM-based filter extraction
   - Parses "blue cards under 3 mana" → `{colors: "U", max_cmc: 2}`
   - Could become `utils/llm_filter_extractor.py`
   - Interactor could use it via: `FilterExtractor.extract(query)`

2. **`_build_combo_query()`** - Semantic query construction
   - Analyzes card mechanics to build better search queries
   - Could become method in `Interactor` or utility

3. **`_handle_no_results()`** - User-friendly error messages
   - Already simple, can inline into Interactor

**Should we extract before refactoring?**
- **No, do it later** - Phase 3.5 (after architecture cleanup)
- First: Restore clean architecture (Interactor as business logic)
- Then: Extract valuable utilities if needed for features
- Keeps refactoring focused and lower risk

---

## Phase 4 MCP Integration Plan

### Step 1: Refactor QueryOrchestrator (This Session)
- Make it delegate to Interactor
- Mark as deprecated
- Zero breaking changes

### Step 2: Move Validation Scripts to Pytest (This Session)
- Create `tests/integration/test_filter_extraction.py`
- Create `tests/integration/test_query_caching.py`
- Create `tests/integration/test_semantic_queries.py`
- Keep scripts as simple runners

### Step 3: Build MCP Server (Phase 4)
- Create `mtg_card_app/interfaces/mcp/server.py`
- Implement MCP protocol handlers
- Map MCP methods to Interactor methods:
  - `get_card(name)` → `Interactor.fetch_card()`
  - `query_cards(query)` → `Interactor.answer_natural_language_query()`
  - `find_combos(card_name)` → `Interactor.find_combo_pieces()`
  - `create_combo(cards)` → `Interactor.create_combo()`
  - `get_budget_combos(max_price)` → `Interactor.get_budget_combos()`

### Step 4: Test MCP Integration
- Use Claude/Cursor to connect to MCP server
- Verify natural language queries work
- Test combo finding, card lookup, etc.

### Step 5: Deprecation Timeline
- Phase 4: MCP uses Interactor exclusively
- Phase 5: Update examples/scripts to use Interactor
- v2.0: Remove QueryOrchestrator entirely

---

## Questions for Discussion

1. **Thin facade vs. full deletion?**
   - I recommend thin facade for zero risk
   - Your preference?

2. **Extract filter logic now or later?**
   - I recommend later (Phase 3.5 cleanup)
   - Keeps current refactor focused
   - Your preference?

3. **MCP timeline?**
   - Start Phase 4 immediately after testing refactor?
   - Or polish/scale to 5,000-10,000 cards first?

4. **Testing strategy?**
   - Keep orchestrator tests as-is (testing facade)?
   - Or migrate to Interactor tests now?

5. **Backward compatibility commitment?**
   - Keep QueryOrchestrator until v2.0?
   - Or remove after Phase 4 is stable?

---

## Next Steps (Pending Your Input)

**If you choose Option 1 (Thin Facade):**
1. Refactor `orchestrator.py` to delegate to Interactor (~10 min)
2. Add deprecation warnings to docstrings (~5 min)
3. Run tests to verify zero breakage (~2 min)
4. Move to Phase 2: Testing refactor

**If you choose Option 2 (Delete Orchestrator):**
1. Update 9 files to use Interactor instead (~60 min)
2. Run all tests and validate examples (~30 min)
3. Higher risk, more thorough testing needed
4. Move to Phase 2: Testing refactor

**Either way, Phase 4 MCP will be clean:**
```python
# Clean, testable, single source of truth
mcp_server.query_cards(query) → Interactor.answer_natural_language_query(query)
```

---

## Summary

- ✅ **Architecture now clean**: LLM & Cache properly injectable
- ✅ **Interactor has query methods**: Business logic layer complete
- ⚠️ **QueryOrchestrator drift**: Needs refactoring or removal
- 🎯 **Recommendation**: Thin facade for zero-risk migration
- 🎯 **MCP Impact**: Will call Interactor directly (clean design)
- 🎯 **Timeline**: Refactor now → Testing cleanup → Phase 4 MCP

**Your decision: Which option do you prefer?**
