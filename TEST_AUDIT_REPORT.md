# Unit Test Audit Report
**Date**: October 21, 2025  
**Total Tests**: 108

## Executive Summary

**Issues Found:**
1. **7 LLM-dependent combo tests** are EXTREMELY slow (~30s each = 3.5 minutes total)
2. **MCP interface tests** may be testing legacy/unused functionality
3. **Some tests** may not reflect current architecture after SQLite migration

---

## Test Breakdown by Category

### ✅ **Fast & Relevant Tests** (85 tests)

#### 1. **SQLite Service Tests** (16 tests) - `test_card_sqlite_service.py`
- ✅ **Status**: Critical & Up-to-date
- ⚡ **Speed**: Fast (database operations)
- 📝 **Tests**: CRUD operations, search, filtering, indexing
- **Verdict**: KEEP - These test our core data layer

#### 2. **Protocol Tests** (34 tests)
- `test_embedding_service_protocol.py` (9 tests)
- `test_vector_store_service_protocol.py` (14 tests)
- `test_llm_service_protocol.py` (4 tests) ⚠️ **May be slow if hitting Ollama**
- `test_card_data_service_protocol.py` (7 tests)
- ✅ **Status**: Important for architecture validation
- **Verdict**: REVIEW - Check if LLM protocol tests hit real Ollama

#### 3. **Query/Filter Tests** (9 tests)
- `test_interactor_queries.py` (2 tests)
- `test_interactor_filtering.py` (7 tests)
- ✅ **Status**: Testing actual user-facing features
- ⚡ **Speed**: Fast
- **Verdict**: KEEP - These test search/filter functionality

#### 4. **Deck Management Tests** (10 tests)
- `test_export_deck.py` (9 tests)
- `test_suggest_cards.py` (1 test)
- ✅ **Status**: Testing deck features
- **Verdict**: KEEP

---

### 🐌 **SLOW Tests** (7 tests - ~3.5 minutes)

#### **Combo Detection Tests** - `test_interactor_combos.py`
All 7 tests call real LLM (Ollama) which takes ~30 seconds each:

1. `test_find_combo_pieces_isochron_scepter` 🔴 **~30s**
2. `test_find_combo_pieces_dramatic_reversal` 🔴 **~30s**
3. `test_find_combo_pieces_thassas_oracle` 🔴 **~30s**
4. `test_find_combo_pieces_rhystic_study` 🔴 **~30s**
5. `test_find_combo_pieces_nonexistent_card` 🔴 **~30s**
6. `test_combo_response_quality` 🔴 **~30s**
7. `test_combo_with_limit` 🔴 **~30s**

**Problem**: These tests hit the real Ollama LLM service  
**Impact**: 7 tests × 30s = 3.5 minutes  
**Recommendation**: 
- **Option A**: Mark with `@pytest.mark.slow` and skip by default
- **Option B**: Mock the LLM service for unit tests
- **Option C**: Move to integration test suite

---

### ❓ **Questionable Tests** (16 tests)

#### **MCP Interface Tests** (16 tests)
These test the Model Context Protocol interface:

- `test_manager.py` (4 tests)
- `test_manager_validation.py` (3 tests)
- `test_manager_initialize.py` (1 test)
- `test_manager_tools.py` (4 tests)
- `test_jsonrpc_e2e.py` (6 tests) - **Includes combo test**
- `test_jsonrpc_stdio_content_length.py` (1 test)
- `test_deck_mcp_tools.py` (2 tests)
- `test_deck_builder_e2e.py` (4 tests)

**Questions:**
1. Are we actively using MCP interface? (Seems like infrastructure for Claude integration)
2. Are these integration tests disguised as unit tests?
3. Do we need this many MCP tests if it's not the primary interface?

**Recommendation**: Review if MCP is actively used, otherwise mark as integration tests

---

## Recommendations

### 🎯 **Immediate Actions**

1. **Mark Slow Tests**
   ```python
   @pytest.mark.slow
   def test_find_combo_pieces_isochron_scepter(self, interactor):
       ...
   ```
   Then run fast tests with: `pytest -m "not slow"`

2. **Mock LLM for Unit Tests**
   Create a `MockLLMService` that returns canned responses:
   ```python
   @pytest.fixture
   def mock_llm_service():
       class MockLLM:
           def generate_text(self, prompt):
               return "Mock combo analysis: Card synergizes well..."
       return MockLLM()
   ```

3. **Create Test Categories**
   ```ini
   # pytest.ini
   [pytest]
   markers =
       slow: marks tests as slow (deselect with '-m "not slow"')
       integration: marks tests as integration tests
       unit: marks tests as true unit tests (fast, isolated)
       mcp: marks tests for MCP interface
   ```

4. **Separate Integration Tests**
   Move slow/integration tests to `tests/integration/`

### 📊 **Test Execution Strategy**

**Fast CI/Development Loop** (~30 seconds):
```bash
pytest -m "not slow and not integration"
```

**Full Test Suite** (pre-commit, ~4-5 minutes):
```bash
pytest
```

**Integration Only** (optional):
```bash
pytest -m integration
```

---

## Current vs Ideal Test Distribution

### Current (108 tests)
- Fast unit tests: ~85 tests (78%)
- Slow LLM tests: 7 tests (6%)
- Questionable MCP: 16 tests (15%)

### Ideal (after refactoring)
- Fast unit tests: 85 tests (marked `@pytest.mark.unit`)
- Mocked combo tests: 7 tests (fast, marked `@pytest.mark.unit`)
- Integration tests: 16 tests (marked `@pytest.mark.integration`)
- Slow E2E tests: 7 tests (marked `@pytest.mark.slow`, optional)

---

## Conclusion

**Primary Issue**: 7 combo tests hitting real Ollama LLM causing 3.5-minute delay

**Solutions (pick one or combine)**:
1. ✅ **Quick Fix**: Mark with `@pytest.mark.slow` and skip by default
2. ✅ **Better Fix**: Mock LLM for unit tests, keep real LLM tests as integration
3. ✅ **Best Fix**: Do both - mock for CI, real for full test runs

**Time Savings**: 
- Current: ~4-5 minutes for full suite
- After fix: ~30-60 seconds for unit tests (90% reduction!)
- Full suite still available when needed
