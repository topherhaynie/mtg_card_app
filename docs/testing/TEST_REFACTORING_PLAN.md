# Test Refactoring Action Plan

## Goal
Transform our test suite from "integration tests disguised as unit tests" to a proper test pyramid with true unit tests, integration tests, and E2E tests.

## Current State
- ❌ 18 tests labeled "unit" but actually hitting real LLM (30s each)
- ❌ Testing if Ollama is smart, not if our code is correct
- ❌ Slow feedback loop during development
- ✅ 90 tests that are already fast and proper

## Target State
- ✅ True unit tests with mocked dependencies (<5s total)
- ✅ Integration tests for component interactions (~30s)
- ✅ E2E tests for user experience validation (~5min)
- ✅ Fast CI pipeline (unit + integration)
- ✅ Nightly full suite (all tests)

---

## Phase 1: Create Mock LLM Infrastructure

### Step 1.1: Create Mock LLM Service
**File**: `tests/mocks/mock_llm_service.py`

```python
"""Mock LLM service for fast, predictable testing."""

class MockLLMService:
    """Mock LLM that returns canned responses based on prompt analysis."""
    
    def __init__(self, responses: dict[str, str] | None = None):
        """Initialize with optional response mapping.
        
        Args:
            responses: Dict mapping prompt keywords to responses
        """
        self.responses = responses or {}
        self.calls = []
        self.generate_count = 0
    
    def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate a mock response based on prompt keywords."""
        self.calls.append(prompt)
        self.generate_count += 1
        
        # Check for custom responses first
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        # Default responses based on prompt type
        if "extract filter" in prompt.lower() or "filter extraction" in prompt.lower():
            return self._mock_filter_extraction(prompt)
        
        if "combo" in prompt.lower() or "synergy" in prompt.lower():
            return self._mock_combo_response(prompt)
        
        if "format" in prompt.lower() or "relevant mtg cards" in prompt.lower():
            return self._mock_format_response(prompt)
        
        return "Mock LLM response for testing purposes."
    
    def _mock_filter_extraction(self, prompt: str) -> str:
        """Mock filter extraction based on query content."""
        filters = {}
        
        # Color extraction
        if "blue" in prompt.lower():
            filters["colors"] = "U"
        elif "red" in prompt.lower():
            filters["colors"] = "R"
        elif "green" in prompt.lower():
            filters["colors"] = "G"
        elif "black" in prompt.lower():
            filters["colors"] = "B"
        elif "white" in prompt.lower():
            filters["colors"] = "W"
        elif "grixis" in prompt.lower():
            filters["colors"] = "U,B,R"
        
        # CMC extraction
        if "under 3" in prompt.lower():
            filters["max_cmc"] = 2
        elif "under 4" in prompt.lower():
            filters["max_cmc"] = 3
        elif "3 or less" in prompt.lower():
            filters["max_cmc"] = 3
        
        import json
        return json.dumps(filters)
    
    def _mock_combo_response(self, prompt: str) -> str:
        """Mock combo analysis response."""
        if "isochron scepter" in prompt.lower():
            return ("Isochron Scepter creates powerful synergies with instant-speed spells. "
                    "Dramatic Reversal is the most famous combo piece, generating infinite mana "
                    "with mana-producing artifacts. Other good options include counterspells "
                    "and card draw instants for repeatable value.")
        
        if "dramatic reversal" in prompt.lower():
            return ("Dramatic Reversal combos with Isochron Scepter and mana rocks to generate "
                    "infinite mana. You need artifacts that produce at least 3 total mana to go infinite.")
        
        return "These cards have strong synergies when played together in combo-focused decks."
    
    def _mock_format_response(self, prompt: str) -> str:
        """Mock formatted card response."""
        return ("Here are some relevant cards for your query:\n\n"
                "1. Counterspell - The classic 2-mana hard counter\n"
                "2. Lightning Bolt - Efficient 1-mana removal\n"
                "3. Sol Ring - The most powerful mana rock\n\n"
                "These cards offer excellent value and are staples in their respective archetypes.")
    
    def get_model_name(self) -> str:
        """Return mock model name."""
        return "mock-llm-v1"
    
    def get_stats(self) -> dict:
        """Return mock stats."""
        return {
            "model": "mock-llm-v1",
            "total_calls": self.generate_count,
            "api_url": "mock://localhost",
        }
```

### Step 1.2: Create Mock Fixtures
**File**: `tests/conftest.py` (append to existing)

```python
from tests.mocks.mock_llm_service import MockLLMService

@pytest.fixture
def mock_llm():
    """Provide a mock LLM service for unit tests."""
    return MockLLMService()

@pytest.fixture
def mock_llm_with_responses():
    """Provide a mock LLM with custom responses."""
    def _mock_llm(responses: dict[str, str]):
        return MockLLMService(responses=responses)
    return _mock_llm
```

---

## Phase 2: Create True Unit Tests

### Step 2.1: Test Filter Extraction Logic
**File**: `tests/unit/core/test_interactor_filter_extraction.py` (NEW)

```python
"""Unit tests for Interactor filter extraction logic."""

import json
import pytest
from unittest.mock import Mock

from mtg_card_app.core.interactor import Interactor
from tests.mocks.mock_llm_service import MockLLMService


class TestFilterExtraction:
    """Test filter extraction with mocked LLM."""
    
    def test_extract_blue_color_filter(self):
        """Test extraction of blue color filter."""
        mock_llm = MockLLMService()
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )
        
        filters = interactor._extract_filters("Show me blue counterspells")
        
        assert filters == {"colors": "U"}
        assert mock_llm.generate_count == 1
    
    def test_extract_cmc_filter(self):
        """Test extraction of CMC filter."""
        mock_llm = MockLLMService()
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )
        
        filters = interactor._extract_filters("Find creatures under 3 mana")
        
        assert filters == {"max_cmc": 2}
    
    def test_extract_combined_filters(self):
        """Test extraction of multiple filters."""
        mock_llm = MockLLMService()
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )
        
        filters = interactor._extract_filters("Show me blue spells under 4 mana")
        
        assert filters == {"colors": "U", "max_cmc": 3}
    
    def test_no_filters_extracted(self):
        """Test query with no explicit filters."""
        mock_llm = MockLLMService()
        interactor = Interactor(
            card_data_manager=Mock(),
            rag_manager=Mock(),
            llm_manager=mock_llm,
        )
        
        filters = interactor._extract_filters("What are some infinite combos?")
        
        assert filters == {}
```

### Step 2.2: Test Combo Logic
**File**: `tests/unit/core/test_interactor_combo_logic.py` (NEW)

```python
"""Unit tests for Interactor combo detection logic."""

import pytest
from unittest.mock import Mock, MagicMock

from mtg_card_app.core.interactor import Interactor
from mtg_card_app.domain.entities import Card
from tests.mocks.mock_llm_service import MockLLMService


class TestComboLogic:
    """Test combo detection workflow with mocked dependencies."""
    
    def test_find_combo_fetches_card(self):
        """Test that combo finder retrieves the base card."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint an instant...",
        )
        
        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=MockLLMService(),
        )
        
        interactor.find_combo_pieces("Isochron Scepter")
        
        mock_card_manager.get_card.assert_called_once_with("Isochron Scepter")
    
    def test_find_combo_searches_similar_cards(self):
        """Test that combo finder searches for similar cards via RAG."""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            ("card1", 0.95, {}),
            ("card2", 0.88, {}),
        ]
        
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint an instant...",
        )
        
        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=MockLLMService(),
        )
        
        interactor.find_combo_pieces("Isochron Scepter", n_results=3)
        
        # Verify RAG search was called
        assert mock_rag.search_similar.called
        call_kwargs = mock_rag.search_similar.call_args.kwargs
        assert call_kwargs.get("n_results") == 3
    
    def test_find_combo_handles_missing_card(self):
        """Test graceful handling when card doesn't exist."""
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = None
        
        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=Mock(),
            llm_manager=MockLLMService(),
        )
        
        result = interactor.find_combo_pieces("Nonexistent Card")
        
        assert "not found" in result.lower()
    
    def test_find_combo_provides_context_to_llm(self):
        """Test that LLM receives proper context about the card and similar cards."""
        mock_llm = MockLLMService()
        
        mock_card_manager = Mock()
        mock_card_manager.get_card.return_value = Card(
            id="scepter",
            name="Isochron Scepter",
            type_line="Artifact",
            oracle_text="Imprint an instant...",
        )
        mock_card_manager.get_card_by_id.return_value = Card(
            id="reversal",
            name="Dramatic Reversal",
            type_line="Instant",
            oracle_text="Untap all nonland permanents...",
        )
        
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [("reversal", 0.95, {})]
        
        interactor = Interactor(
            card_data_manager=mock_card_manager,
            rag_manager=mock_rag,
            llm_manager=mock_llm,
        )
        
        result = interactor.find_combo_pieces("Isochron Scepter")
        
        # Verify LLM was called
        assert mock_llm.generate_count == 1
        prompt = mock_llm.calls[0]
        
        # Verify prompt contains card info
        assert "Isochron Scepter" in prompt
        assert "Dramatic Reversal" in prompt
```

---

## Phase 3: Move E2E Tests

### Step 3.1: Create E2E Directory Structure
```bash
mkdir -p tests/e2e/core
```

### Step 3.2: Move Existing Tests
```bash
# Move filtering tests (renamed)
mv tests/unit/core/test_interactor_filtering.py \
   tests/e2e/core/test_query_answering_e2e.py

# Move combo tests (renamed)
mv tests/unit/core/test_interactor_combos.py \
   tests/e2e/core/test_combo_detection_e2e.py

# Move query tests (renamed)
mv tests/unit/core/test_interactor_queries.py \
   tests/e2e/core/test_natural_language_e2e.py
```

### Step 3.3: Update E2E Test Markers
Change `@pytest.mark.slow` to `@pytest.mark.e2e` in moved files.

---

## Phase 4: Create Integration Tests

### Step 4.1: Test Filtering Pipeline
**File**: `tests/integration/test_filtering_pipeline.py` (NEW)

```python
"""Integration tests for filtering pipeline with real RAG, mocked LLM."""

import pytest
from mtg_card_app.core.interactor import Interactor
from mtg_card_app.core.manager_registry import ManagerRegistry
from tests.mocks.mock_llm_service import MockLLMService


@pytest.mark.integration
class TestFilteringPipeline:
    """Test filter application with real RAG but mocked LLM."""
    
    def test_blue_filter_applied_to_rag_search(self):
        """Test that blue color filter is properly applied to RAG search."""
        registry = ManagerRegistry.get_instance()
        mock_llm = MockLLMService()
        
        interactor = Interactor(
            card_data_manager=registry.card_data_manager,
            rag_manager=registry.rag_manager,
            llm_manager=mock_llm,  # Mock LLM only
            db_manager=registry.db_manager,
        )
        
        # This should extract blue filter and search
        response = interactor.answer_natural_language_query("blue counterspells")
        
        # Verify mock LLM was called
        assert mock_llm.generate_count >= 2  # Filter extraction + formatting
        
        # Response should be formatted
        assert isinstance(response, str)
        assert len(response) > 0
```

---

## Phase 5: Update Test Configuration

### Step 5.1: Update pytest.ini
**File**: `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
]
markers = [
    "unit: Fast unit tests with all dependencies mocked (< 5s total)",
    "integration: Integration tests with some real dependencies (~30s)",
    "e2e: End-to-end tests with all real dependencies including LLM (~5min)",
    "slow: Deprecated - use e2e instead",
]
```

### Step 5.2: Create Test Commands
**File**: `Makefile` or `justfile`

```makefile
# Fast tests for development
test-unit:
	pytest -m unit -v

# Medium tests for pre-commit
test-integration:
	pytest -m "unit or integration" -v

# Full test suite
test-all:
	pytest -v

# Only E2E tests
test-e2e:
	pytest -m e2e -v

# CI pipeline (fast)
test-ci:
	pytest -m "unit or integration" --tb=short
```

---

## Phase 6: Update Documentation

### Step 6.1: Update README
Add test strategy section explaining:
- What each test level covers
- When to run which tests
- How to add new tests

### Step 6.2: Create TESTING.md
Document:
- Test pyramid strategy
- Mocking guidelines
- When to use unit vs integration vs E2E

---

## Implementation Order

### Week 1: Foundation
1. ✅ Create `tests/mocks/mock_llm_service.py`
2. ✅ Add mock fixtures to `conftest.py`
3. ✅ Create first unit tests for filter extraction

### Week 2: Unit Tests
4. ✅ Create unit tests for combo logic
5. ✅ Create unit tests for query handling
6. ✅ Create unit tests for caching

### Week 3: Reorganization
7. ✅ Move E2E tests to `tests/e2e/`
8. ✅ Create integration tests
9. ✅ Update test markers

### Week 4: Polish
10. ✅ Update documentation
11. ✅ Create test commands
12. ✅ Run full suite validation

---

## Success Metrics

### Before Refactoring
- ❌ 18 "unit" tests taking ~9 minutes
- ❌ Testing LLM intelligence, not our code
- ❌ Slow development feedback loop

### After Refactoring
- ✅ ~100 true unit tests taking <5 seconds
- ✅ ~20 integration tests taking ~30 seconds
- ✅ ~18 E2E tests taking ~5 minutes
- ✅ Fast CI pipeline (unit + integration in <35s)
- ✅ Nightly full suite (all tests)
- ✅ Testing our logic, not external services

---

## Questions to Answer

1. Should we keep ANY E2E tests, or mock everything?
   - **Answer**: Keep E2E tests, but run them less frequently (nightly/weekly)

2. What's the right balance of unit vs integration vs E2E?
   - **Answer**: Follow the test pyramid: 70% unit, 20% integration, 10% E2E

3. Should LLM protocol tests use real LLM?
   - **Answer**: One or two E2E tests to verify LLM works, rest mocked

4. How do we handle RAG tests?
   - **Answer**: Integration tests with real RAG, mocked LLM

Would you like me to start implementing this plan? I suggest starting with Phase 1 (Mock LLM) and Phase 2.1 (Filter extraction tests) as a proof of concept.
