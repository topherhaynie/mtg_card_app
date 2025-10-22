# Protocol-Based Testing Pattern

**Created:** October 20, 2025  
**Project:** MTG Card App  
**Context:** Phase 2A Complete - Moving to Phase 3

## Overview

This document describes the protocol-based testing pattern established for service implementations in the MTG Card App. This pattern tests the **interface contract** rather than implementation details, making tests more maintainable and enabling easy addition of new service implementations.

## Motivation

**Problem with Mock-Heavy Tests:**
- Tightly coupled to implementation details (mocking `_client`, `_model`, internal methods)
- Break when internal structure changes, even if public API remains the same
- Don't test actual behavior - just test that mocks are called
- Difficult to add new implementations

**Solution - Protocol-Based Testing:**
- Test the public API contract defined by protocols/base classes
- Parametrize tests to run against all implementations
- Use real services where possible (embedding models, vector stores)
- Mock only external dependencies (HTTP calls, file I/O)

## Test Structure

### Directory Organization

```
tests/unit/managers/
├── card_data/
│   └── services/
│       ├── __init__.py
│       └── test_card_data_service_protocol.py  # Tests CardDataService protocol
└── rag/
    ├── test_embedding_service_protocol.py      # Tests EmbeddingService protocol
    └── test_vector_store_service_protocol.py   # Tests VectorStoreService protocol
```

### File Naming Convention

- **Pattern:** `test_<service_type>_service_protocol.py`
- **Examples:**
  - `test_card_data_service_protocol.py`
  - `test_embedding_service_protocol.py`
  - `test_vector_store_service_protocol.py`

## Implementation Pattern

### 1. Parametrized Fixture

Create a pytest fixture that yields all implementations of the protocol:

```python
@pytest.fixture(
    params=[
        pytest.param("implementation_key", id="ImplementationClassName"),
        # Add more implementations here
    ],
)
def service_fixture(request, tmp_path):
    """Fixture that provides all ServiceProtocol implementations."""
    if request.param == "implementation_key":
        # Set up the service (use tmp_path for file-based services)
        service = ConcreteImplementation(...)
        yield service
        # Cleanup if needed
        service.cleanup()
    # Add elif blocks for additional implementations
```

**Key Points:**
- Use `params` to define all implementations to test
- Use descriptive `id` values for clear test output
- Handle setup/teardown in the fixture
- Use `tmp_path` for services that need file storage

### 2. Test Classes by Protocol Method

Organize tests by the protocol method being tested:

```python
class TestMethodName:
    """Test method_name protocol compliance."""
    
    def test_returns_expected_type(self, service_fixture):
        """Test that method_name returns the correct type."""
        # Arrange
        ...
        
        # Act
        result = service_fixture.method_name(...)
        
        # Assert
        assert isinstance(result, ExpectedType)
    
    def test_handles_edge_case(self, service_fixture):
        """Test that method_name handles edge cases correctly."""
        ...
```

**Benefits:**
- Clear organization: one class per protocol method
- Easy to find tests for specific functionality
- Natural grouping in test output

### 3. Test the Contract, Not Implementation

**Good - Tests Protocol Contract:**
```python
def test_embed_text_returns_list_of_floats(self, embedding_service):
    """Test that embed_text returns a list of floats."""
    result = embedding_service.embed_text("Test text")
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(x, float) for x in result)
```

**Bad - Tests Implementation Details:**
```python
def test_embed_text_calls_internal_method(self, embedding_service, monkeypatch):
    """Test that embed_text calls _load_model."""
    mock_load = MagicMock()
    monkeypatch.setattr(embedding_service, "_load_model", mock_load)
    
    embedding_service.embed_text("Test")
    
    assert mock_load.called  # ❌ Testing implementation detail
```

### 4. Mock Only External Dependencies

**When to Mock:**
- HTTP/API calls (use `unittest.mock.patch`)
- File system operations (or use `tmp_path`)
- External services (databases, cloud APIs)

**When NOT to Mock:**
- Internal service methods
- Protocol-compliant dependencies
- Logic within the service

**Example:**
```python
@pytest.fixture
def card_data_service(request):
    """Fixture with mocked external API client."""
    with patch("path.to.ScryfallClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.get_request_stats.return_value = {"requests": 0}
        mock_client_class.return_value = mock_client
        
        service = ScryfallCardDataService()
        service._mock_client = mock_client  # For test assertions
        yield service
```

## Current Test Coverage

### CardDataService Protocol (9 tests)
- ✅ `get_card_by_name` - returns dict, handles not found, respects exact parameter
- ✅ `get_card_by_id` - returns dict, handles not found
- ✅ Service info - `get_service_name()`, `get_stats()`

**Implementations Tested:**
- `ScryfallCardDataService`

### EmbeddingService Protocol (11 tests)
- ✅ `embed_text` - returns list of floats, consistent dimensions, handles various inputs
- ✅ `embed_texts` - batch processing
- ✅ `get_embedding_dimension` - matches actual output
- ✅ Service info - `get_model_name()`, `get_service_name()`, `get_stats()`

**Implementations Tested:**
- `SentenceTransformerEmbeddingService` (uses real model!)

### VectorStoreService Protocol (17 tests)  
- ✅ `add_embedding` - returns true, retrieval, various dimensions
- ✅ `add_embeddings` - batch operations
- ✅ `get_embedding` - returns None for nonexistent, returns embedding for existing
- ✅ `exists` - false for nonexistent, true for existing
- ✅ `search_similar` - returns list of tuples with correct structure
- ✅ `delete` - returns true, removes from store
- ✅ `count` - returns integer, increases after add
- ✅ Service info - `get_service_name()`, `get_stats()`

**Implementations Tested:**
- `ChromaVectorStoreService` (uses real ChromaDB!)

## Running Tests

### Run All Protocol Tests
```bash
python -m pytest tests/unit/managers/ -k "protocol" -v
```

### Run Tests for Specific Protocol
```bash
python -m pytest tests/unit/managers/card_data/services/test_card_data_service_protocol.py -v
python -m pytest tests/unit/managers/rag/test_embedding_service_protocol.py -v
python -m pytest tests/unit/managers/rag/test_vector_store_service_protocol.py -v
```

### Run Tests for Specific Implementation
```bash
python -m pytest tests/unit/managers/ -k "protocol and Scryfall" -v
python -m pytest tests/unit/managers/ -k "protocol and SentenceTransformer" -v
python -m pytest tests/unit/managers/ -k "protocol and Chroma" -v
```

## Adding New Implementations

When adding a new implementation of an existing protocol:

1. **Add to the parametrized fixture:**
   ```python
   @pytest.fixture(
       params=[
           pytest.param("existing", id="ExistingImplementation"),
           pytest.param("new", id="NewImplementation"),  # ← Add here
       ],
   )
   def service_fixture(request):
       ...
       elif request.param == "new":
           # Set up new implementation
           service = NewImplementation(...)
           yield service
   ```

2. **Run the tests:**
   ```bash
   python -m pytest tests/unit/managers/ -k "protocol and NewImplementation" -v
   ```

3. **All existing tests automatically run against the new implementation!**

## Benefits Realized

### ✅ Test Maintainability
- Tests survive internal refactoring
- Only break when public API changes
- Clear what the contract requires

### ✅ Implementation Flexibility
- Easy to add new implementations
- Encourages consistent interfaces
- Documents expected behavior

### ✅ Real Behavior Testing
- Embedding tests use actual transformer models
- Vector store tests use real ChromaDB
- Catches integration issues early

### ✅ Clear Test Output
```
test_card_data_service_protocol.py::TestGetCardByName::test_returns_dict[ScryfallCardDataService] PASSED
test_embedding_service_protocol.py::TestEmbedText::test_returns_list[SentenceTransformerEmbeddingService] PASSED
test_vector_store_service_protocol.py::TestAddEmbedding::test_returns_true[ChromaVectorStoreService] PASSED
```

## Lessons Learned

1. **Don't mock what you own** - If it's in your codebase, test it directly
2. **Mock at the boundaries** - Only mock external systems (APIs, databases)
3. **Test behavior, not structure** - Focus on what the service does, not how
4. **Parametrize for scale** - One test suite tests all implementations
5. **Use real services in tests** - Catches real bugs that mocks miss

## Future Additions

When adding new service types:

1. Define the protocol in `managers/<type>/services/base.py`
2. Create `tests/unit/managers/<type>/test_<type>_service_protocol.py`
3. Follow the pattern established in existing protocol tests
4. Add all implementations to the parametrized fixture
5. Watch all tests pass! 🎉

## Related Documentation

- `SERVICE_ABSTRACTION_COMPLETE.md` - Service architecture overview
- `DEPENDENCY_INJECTION_REFACTORING.md` - Dependency injection pattern
- `TESTING_SETUP_COMPLETE.md` - Initial testing infrastructure (superseded by this document)

---

**Result:** 37 protocol tests, 100% passing, testing 3 different service types across 3 implementations. New implementations can be added with ~5 lines of code and get full test coverage automatically.
