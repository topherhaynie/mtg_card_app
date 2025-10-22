# Test Strategy Analysis: Unit vs Integration vs E2E

## Your Question: Are We Testing the Right Things?

**You're absolutely right to question this.** Let's analyze what each test is *actually* testing vs what it *should* be testing.

---

## Current Test Issues

### ❌ Problem: Tests in `tests/unit/` are NOT Unit Tests

**Location**: `tests/unit/core/test_interactor_*.py`

These are labeled as "unit tests" but they're actually **integration tests** because they:
1. Hit real Ollama LLM service (external dependency)
2. Hit real ChromaDB (database)
3. Hit real SQLite (database)
4. Test the full pipeline: Query → RAG → LLM → Response

**This violates the Single Responsibility Principle for testing.**

---

## Test Analysis by Category

### 1. ❌ **Filtering Tests** (`test_interactor_filtering.py`)

**Current Behavior:**
```python
def test_color_filtering_blue(self, interactor):
    response = interactor.answer_natural_language_query("Show me blue counterspells")
    assert "counterspell" in response.lower()
```

**What it's testing:** 
- ✅ LLM can understand "blue counterspells" 
- ✅ LLM can format a response
- ❌ NOT testing our filtering logic

**The Problem:**
The test name says "color_filtering" but it's actually testing:
1. LLM filter extraction (`_extract_filters()`)
2. RAG semantic search with filters
3. Card data retrieval
4. LLM response formatting

**What we SHOULD test:**

#### Unit Test (Fast):
```python
def test_extract_filters_blue_color():
    """Test that filter extraction identifies blue color."""
    interactor = Interactor(card_data=mock, rag=mock, llm=mock_llm)
    
    # Mock LLM to return expected filter
    mock_llm.generate.return_value = '{"colors": "U"}'
    
    filters = interactor._extract_filters("Show me blue counterspells")
    assert filters == {"colors": "U"}
    mock_llm.generate.assert_called_once()
```

#### Integration Test (Medium):
```python
@pytest.mark.integration
def test_filtering_pipeline_with_real_rag():
    """Test that filters are properly applied to RAG search."""
    # Use real RAG + real DB, but MOCK the LLM response
    filters = {"colors": "U"}
    results = rag_manager.search_similar("counterspells", filters=filters)
    
    # Verify all results match filter
    for card_id, score, metadata in results:
        card = db.get(card_id)
        assert "U" in card.colors
```

#### E2E Test (Slow):
```python
@pytest.mark.e2e
def test_blue_counterspell_query_end_to_end():
    """Test full query pipeline with real LLM."""
    # This one CAN hit the real LLM
    response = interactor.answer_natural_language_query("blue counterspells")
    assert isinstance(response, str)
    assert len(response) > 50
```

---

### 2. ❌ **Combo Tests** (`test_interactor_combos.py`)

**Current Behavior:**
```python
def test_find_combo_pieces_isochron_scepter(self, interactor):
    response = interactor.find_combo_pieces("Isochron Scepter")
    assert "synergy" in response.lower()
```

**What it's testing:**
- ✅ LLM can analyze combos
- ❌ NOT testing our combo detection logic
- ❌ NOT testing RAG similarity search
- ❌ NOT testing card retrieval

**The Problem:**
We're testing if **Ollama is smart**, not if **our code is correct**.

**What we SHOULD test:**

#### Unit Test (Fast):
```python
def test_find_combo_pieces_fetches_card():
    """Test that combo finder retrieves the base card."""
    mock_card_manager = Mock()
    mock_card_manager.get_card.return_value = Card(name="Isochron Scepter", ...)
    
    interactor = Interactor(card_data=mock_card_manager, rag=Mock(), llm=Mock())
    interactor.find_combo_pieces("Isochron Scepter")
    
    mock_card_manager.get_card.assert_called_once_with("Isochron Scepter")
```

#### Unit Test (Fast):
```python
def test_find_combo_pieces_searches_similar_cards():
    """Test that combo finder uses RAG to search similar cards."""
    mock_rag = Mock()
    mock_rag.search_similar.return_value = [("card1", 0.9, {}), ("card2", 0.8, {})]
    
    interactor = Interactor(card_data=Mock(), rag=mock_rag, llm=Mock())
    interactor.find_combo_pieces("Isochron Scepter")
    
    # Verify RAG was called with the card's text
    assert mock_rag.search_similar.called
```

#### Unit Test (Fast):
```python
def test_find_combo_pieces_sends_context_to_llm():
    """Test that combo finder provides proper context to LLM."""
    mock_llm = Mock()
    mock_llm.generate.return_value = "Dramatic Reversal synergizes well..."
    
    interactor = Interactor(card_data=mock_card, rag=mock_rag, llm=mock_llm)
    result = interactor.find_combo_pieces("Isochron Scepter")
    
    # Verify LLM was called with card context
    call_args = mock_llm.generate.call_args[0][0]
    assert "Isochron Scepter" in call_args
    assert "similar cards" in call_args
```

#### Integration Test (Medium):
```python
@pytest.mark.integration
def test_combo_detection_with_real_rag():
    """Test combo detection with real RAG, mocked LLM."""
    # Use real card DB + real RAG, mock only the LLM
    interactor = Interactor(
        card_data=real_card_manager,
        rag=real_rag_manager,
        llm=MockLLM(response="Mocked combo analysis")
    )
    
    result = interactor.find_combo_pieces("Isochron Scepter")
    assert "Mocked combo analysis" in result
```

#### E2E Test (Slow):
```python
@pytest.mark.e2e
def test_combo_detection_end_to_end():
    """Test full combo detection with real LLM."""
    # Only this one hits real Ollama
    result = interactor.find_combo_pieces("Isochron Scepter")
    assert isinstance(result, str)
    assert len(result) > 100
```

---

### 3. ❓ **Query Tests** (`test_interactor_queries.py`)

**Current Behavior:**
```python
def test_answer_natural_language_query_basic(self, interactor):
    response = interactor.answer_natural_language_query("List two green ramp spells")
    assert "green" in response.lower() or "ramp" in response.lower()
```

**Analysis:**
- These might be legitimately E2E tests
- They test the full natural language → answer pipeline
- **BUT** they should be in `tests/integration/` or `tests/e2e/`, NOT `tests/unit/`

---

## Recommended Test Structure

```
tests/
├── unit/                          # Fast tests, all mocked
│   ├── core/
│   │   ├── test_interactor_card_fetching.py       # Mock card_data_manager
│   │   ├── test_interactor_filter_extraction.py   # Mock LLM
│   │   ├── test_interactor_combo_logic.py         # Mock RAG + LLM
│   │   └── test_interactor_cache.py               # Mock query_cache
│   ├── managers/
│   │   ├── test_card_data_manager.py              # Mock Scryfall API
│   │   ├── test_rag_manager.py                    # Mock ChromaDB
│   │   └── test_llm_manager.py                    # Mock Ollama
│   └── services/
│       ├── test_sqlite_service.py                 # Real SQLite (in-memory)
│       └── test_embedding_service.py              # Real embeddings
│
├── integration/                   # Medium tests, some real deps
│   ├── test_rag_with_real_db.py                   # Real ChromaDB + SQLite
│   ├── test_filtering_pipeline.py                 # Real RAG, mock LLM
│   └── test_combo_detection_pipeline.py           # Real RAG, mock LLM
│
└── e2e/                          # Slow tests, all real deps
    ├── test_query_answering.py                    # Real LLM + RAG
    ├── test_combo_detection.py                    # Real LLM + RAG
    └── test_deck_building.py                      # Real everything
```

---

## Specific Recommendations

### 1. ✅ Keep Tests That Are Already Good

**These are already proper unit tests:**
- ✅ `test_card_sqlite_service.py` - Uses in-memory SQLite
- ✅ `test_embedding_service_protocol.py` - Tests real embedding logic
- ✅ `test_vector_store_service_protocol.py` - Tests real ChromaDB operations
- ✅ `test_export_deck.py` - Pure logic, no external deps
- ✅ MCP interface tests - Mock the interactor

### 2. ⚠️ Fix These Tests

**Move to `tests/integration/` or add mocking:**
- ⚠️ `test_interactor_filtering.py` - Should mock LLM
- ⚠️ `test_interactor_combos.py` - Should mock LLM
- ⚠️ `test_interactor_queries.py` - Should be in e2e/ OR mock LLM

### 3. 📝 Add Missing Unit Tests

**We need unit tests for:**
- `interactor._extract_filters()` - Test filter parsing logic
- `interactor.find_combo_pieces()` - Test workflow, not LLM output
- RAG search with filters - Test filter application
- Query caching - Test cache hit/miss logic

---

## Priority Actions

### 🎯 Phase 1: Separate Concerns (High Priority)

1. **Create proper unit tests** for `Interactor` methods with mocked LLM:
   ```python
   # tests/unit/core/test_interactor_unit.py
   @pytest.fixture
   def mock_llm():
       llm = Mock()
       llm.generate.return_value = '{"colors": "U"}'
       return llm
   
   def test_extract_filters_with_color(mock_llm):
       interactor = Interactor(card_data=Mock(), rag=Mock(), llm=mock_llm)
       filters = interactor._extract_filters("blue counterspells")
       assert filters.get("colors") == "U"
   ```

2. **Move slow tests** to `tests/e2e/`:
   ```bash
   mkdir -p tests/e2e
   mv tests/unit/core/test_interactor_filtering.py tests/e2e/
   mv tests/unit/core/test_interactor_combos.py tests/e2e/
   mv tests/unit/core/test_interactor_queries.py tests/e2e/
   ```

3. **Create integration tests** for the pipeline:
   ```python
   # tests/integration/test_filtering_pipeline.py
   @pytest.mark.integration
   def test_blue_filter_applied_to_rag_search():
       # Real RAG + DB, mocked LLM response
       ...
   ```

### 🎯 Phase 2: Add Test Markers (Medium Priority)

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Fast tests with all dependencies mocked",
    "integration: Medium tests with some real dependencies",
    "e2e: Slow tests with all real dependencies (LLM, DB, etc)",
]
```

Usage:
```bash
pytest -m unit           # Fast: ~5 seconds
pytest -m integration    # Medium: ~30 seconds
pytest -m e2e           # Slow: ~5 minutes
pytest                   # All tests
```

### 🎯 Phase 3: Mock LLM Responses (High Priority)

Create a mock LLM service:
```python
# tests/mocks/mock_llm_service.py
class MockLLMService:
    """Mock LLM that returns predictable responses for testing."""
    
    def __init__(self, responses: dict[str, str] = None):
        self.responses = responses or {}
        self.call_count = 0
    
    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        
        # Return canned response based on prompt keywords
        if "extract filter" in prompt.lower():
            if "blue" in prompt.lower():
                return '{"colors": "U"}'
            if "under 3 mana" in prompt.lower():
                return '{"max_cmc": 2}'
        
        if "combo" in prompt.lower():
            return "These cards create infinite mana when combined..."
        
        return "Default mock response"
```

---

## Summary: What Should We Test?

### ✅ Unit Tests (Fast - Seconds)
**Test OUR code logic, not external services:**
- Filter extraction returns correct JSON
- Cache hit/miss logic works
- Card fetching calls the right methods
- Error handling for missing cards
- Query formatting for LLM prompts

### ✅ Integration Tests (Medium - Seconds to Minutes)
**Test component interactions with some real deps:**
- RAG search applies filters correctly
- Cards are retrieved from database
- Similar cards are properly ranked
- Cache stores and retrieves correctly

### ✅ E2E Tests (Slow - Minutes)
**Test the full user experience:**
- Natural language query returns helpful answer
- Combo detection finds real synergies
- Deck building works end-to-end

---

## Conclusion

**You're 100% correct.** Our current "unit tests" are actually integration/E2E tests disguised as unit tests. They:
1. Test if **Ollama is smart** (not our job)
2. Don't test **our logic in isolation**
3. Are **slow** because they hit external services
4. Are **flaky** because LLM responses vary

**The fix:**
1. Mock the LLM in unit tests (test our logic)
2. Move LLM-dependent tests to `tests/e2e/`
3. Add real unit tests for our code
4. Use integration tests for component interactions

This gives us:
- **Fast feedback** during development (unit tests)
- **Confidence in integration** (integration tests)
- **Validation of user experience** (E2E tests)

Would you like me to start implementing this refactoring?
