# QueryOrchestrator → Interactor Migration Plan

**Date:** October 20, 2025  
**Strategy:** Option 2 - Complete deletion and migration

---

## Files to Update (9 total)

### Production Code (2 files)
1. ✅ `core/orchestrator.py` - DELETE entirely
2. ✅ `core/__init__.py` - Remove QueryOrchestrator exports if present

### Examples (2 files)  
3. ✅ `examples/orchestrator_demo.py` - Migrate to Interactor
4. ✅ `examples/combo_demo.py` - Migrate to Interactor

### Scripts (2 files)
5. ✅ `scripts/test_queries.py` - Migrate to Interactor
6. ✅ `scripts/validate_polish.py` - Migrate to Interactor

### Tests (3 files)
7. ✅ `tests/unit/core/test_orchestrator_protocol.py` - Migrate to test_interactor_queries.py
8. ✅ `tests/unit/core/test_orchestrator_filtering.py` - Migrate to test_interactor_filtering.py
9. ✅ `tests/unit/core/test_combo_detection.py` - Migrate to test_interactor_combos.py

---

## Migration Strategy

### Key Mapping: QueryOrchestrator → Interactor

| QueryOrchestrator Method | Interactor Method | Notes |
|-------------------------|------------------|-------|
| `answer_query(query)` | `answer_natural_language_query(query)` | Core query method |
| `find_combos(card, n)` | `find_combo_pieces(card, n)` | Combo discovery |
| `get_cache_stats()` | `registry.query_cache.get_stats()` | Direct cache access |

### Features NOT in Interactor (To Add)

1. **Filter Extraction** (`_extract_filters()`)
   - Decision: Add to Interactor as private helper
   - Reason: Useful for structured queries, MCP will need it

2. **Combo Query Building** (`_build_combo_query()`)
   - Decision: Keep in find_combo_pieces logic
   - Reason: Already integrated into semantic search

3. **No Results Handling** (`_handle_no_results()`)
   - Decision: Handle inline in query methods
   - Reason: Simple conditional, no need for separate method

---

## Step-by-Step Execution

### Phase 1: Enhance Interactor (Add Missing Features)
- [ ] Add `_extract_filters()` method to Interactor
- [ ] Integrate filter extraction into answer_natural_language_query
- [ ] Update RAG queries to use filters
- [ ] Test filter extraction

### Phase 2: Update Examples
- [ ] Update `orchestrator_demo.py` → Use Interactor
- [ ] Update `combo_demo.py` → Use Interactor  
- [ ] Run examples to verify functionality

### Phase 3: Update Scripts
- [ ] Update `test_queries.py` → Use Interactor
- [ ] Update `validate_polish.py` → Use Interactor
- [ ] Run scripts to verify functionality

### Phase 4: Update Tests
- [ ] Create `test_interactor_queries.py` from test_orchestrator_protocol.py
- [ ] Create `test_interactor_filtering.py` from test_orchestrator_filtering.py
- [ ] Create `test_interactor_combos.py` from test_combo_detection.py
- [ ] Run test suite to verify all passing

### Phase 5: Delete Orchestrator
- [ ] Delete `core/orchestrator.py`
- [ ] Delete old orchestrator test files
- [ ] Update `core/__init__.py` if needed
- [ ] Final test run

### Phase 6: Documentation
- [ ] Update README if mentions QueryOrchestrator
- [ ] Update architecture docs
- [ ] Create migration complete document

---

## Risk Mitigation

1. **Run tests after each phase**
   - Catch issues early
   - Don't proceed if tests fail

2. **Keep git history clean**
   - Commit after each successful phase
   - Easy to rollback if needed

3. **Validate examples actually work**
   - Don't just check for errors
   - Verify output quality

4. **Check for hidden dependencies**
   - Search codebase for "orchestrator" references
   - Check imports in all files

---

## Success Criteria

- ✅ All tests passing
- ✅ All examples run successfully
- ✅ All scripts run successfully
- ✅ `core/orchestrator.py` deleted
- ✅ No references to QueryOrchestrator in codebase
- ✅ Architecture documentation updated
- ✅ Clean git history with good commit messages

---

## Timeline Estimate

- Phase 1: 20 minutes (Add features to Interactor)
- Phase 2: 15 minutes (Update examples)
- Phase 3: 15 minutes (Update scripts)
- Phase 4: 30 minutes (Migrate tests)
- Phase 5: 5 minutes (Delete orchestrator)
- Phase 6: 10 minutes (Documentation)

**Total: ~90 minutes**

---

## Post-Migration Benefits

1. **Single source of truth** - All business logic in Interactor
2. **Clean architecture** - No bypass layers
3. **MCP ready** - Phase 4 calls Interactor directly
4. **Better testability** - One layer to test
5. **Easier maintenance** - Changes in one place
6. **Type safety** - Full type hints throughout
7. **Clearer API** - Obvious entry points

Let's proceed!
