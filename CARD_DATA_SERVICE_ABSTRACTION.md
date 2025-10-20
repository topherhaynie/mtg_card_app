# Card Data Service Abstraction

## Overview

We've refactored the card data layer to use a pluggable service architecture. This allows you to easily swap between different card data providers (Scryfall, MTGJSON, custom APIs, etc.) without changing any business logic.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│  (Interactor, ManagerRegistry, CardDataManager)         │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ Uses Interface
                            ▼
┌─────────────────────────────────────────────────────────┐
│              CardDataService (Abstract Base)             │
│  • get_card_by_name()                                    │
│  • get_card_by_id()                                      │
│  • search_cards()                                        │
│  • autocomplete()                                        │
│  • build_search_query()                                  │
│  • get_stats()                                           │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ Implementations
                ┌───────────┼──────────┐
                ▼           ▼          ▼
    ┌─────────────────┬──────────┬────────────┐
    │  Scryfall       │ MTGJSON  │  Custom    │
    │  Service        │ Service  │  Service   │
    │  (Default)      │ (Future) │  (Future)  │
    └─────────────────┴──────────┴────────────┘
```

## Key Components

### 1. `CardDataService` (Base Protocol)
Location: `mtg_card_app/interfaces/card_data/base.py`

Abstract base class defining the interface all card data providers must implement:

```python
from abc import ABC, abstractmethod

class CardDataService(ABC):
    @abstractmethod
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        """Get card data by name."""
        pass
    
    @abstractmethod
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get card data by unique identifier."""
        pass
    
    # ... other abstract methods
```

### 2. `ScryfallCardDataService` (Implementation)
Location: `mtg_card_app/interfaces/card_data/scryfall_service.py`

Concrete implementation using Scryfall API:

```python
from mtg_card_app.interfaces.card_data.base import CardDataService

class ScryfallCardDataService(CardDataService):
    def __init__(self, client: Optional[ScryfallClient] = None):
        self._client = client or ScryfallClient()
    
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        # Implementation using Scryfall
        return self._client.get_card_by_name(name, fuzzy=not exact)
    
    # ... other method implementations
```

### 3. Updated `CardDataManager`
Location: `mtg_card_app/managers/card_data/manager.py`

Now accepts any `CardDataService` implementation:

```python
class CardDataManager:
    def __init__(
        self,
        card_service: CardService,
        card_data_service: Optional[CardDataService] = None,
    ):
        self.card_service = card_service
        # Defaults to Scryfall if not provided
        self.card_data_service = card_data_service or ScryfallCardDataService()
```

### 4. Updated `ManagerRegistry`
Location: `mtg_card_app/core/manager_registry.py`

Manages the card data service:

```python
class ManagerRegistry:
    def __init__(
        self,
        data_dir: str = "data",
        card_data_service: Optional[CardDataService] = None,
    ):
        self.data_dir = data_dir
        self._card_data_service = card_data_service or ScryfallCardDataService()
```

## Benefits

### 1. **Modularity**
- Easy to swap between data providers
- No changes needed in business logic
- Clean separation of concerns

### 2. **Testability**
- Mock implementations for testing
- No need for real API calls in tests
- Faster test execution

### 3. **Extensibility**
- Add new providers without modifying existing code
- Support multiple providers simultaneously
- Easy to implement fallback strategies

### 4. **Flexibility**
- Use different providers for different use cases
- Combine multiple sources (e.g., Scryfall + local cache + MTGJSON)
- Easy to add rate limiting, retries, caching at the service level

## Usage Examples

### Using Default (Scryfall) Service

```python
from mtg_card_app.core import Interactor

# Uses Scryfall by default
interactor = Interactor()
card = interactor.fetch_card("Lightning Bolt")
```

### Using a Custom Service

```python
from mtg_card_app.core import ManagerRegistry, Interactor
from mtg_card_app.interfaces.card_data import ScryfallCardDataService

# Create a service with custom configuration
service = ScryfallCardDataService()

# Inject into registry
registry = ManagerRegistry(card_data_service=service)

# Use it
interactor = Interactor(registry=registry)
```

### Creating a Mock Service for Testing

```python
from mtg_card_app.interfaces.card_data.base import CardDataService

class MockCardDataService(CardDataService):
    def __init__(self, mock_data: Dict[str, Dict]):
        self.mock_data = mock_data
    
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        return self.mock_data.get(name)
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        for card in self.mock_data.values():
            if card.get('id') == card_id:
                return card
        return None
    
    # ... implement other required methods

# Use in tests
mock_service = MockCardDataService({
    "Lightning Bolt": {"id": "123", "name": "Lightning Bolt", ...}
})

registry = ManagerRegistry(card_data_service=mock_service)
interactor = Interactor(registry=registry)

# Now all calls use mock data - no API calls!
card = interactor.fetch_card("Lightning Bolt")
```

## Future Provider Ideas

### MTGJSON Service
```python
class MTGJsonCardDataService(CardDataService):
    """Implementation using MTGJSON bulk data."""
    
    def __init__(self, json_file_path: str):
        with open(json_file_path) as f:
            self.data = json.load(f)
    
    # Implement required methods using local JSON data
```

### Hybrid Service (Multiple Sources)
```python
class HybridCardDataService(CardDataService):
    """Try multiple sources with fallback."""
    
    def __init__(self, primary: CardDataService, fallback: CardDataService):
        self.primary = primary
        self.fallback = fallback
    
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        result = self.primary.get_card_by_name(name, exact)
        if result is None:
            result = self.fallback.get_card_by_name(name, exact)
        return result
```

### Cached Service (Performance)
```python
class CachedCardDataService(CardDataService):
    """Add caching to any service."""
    
    def __init__(self, wrapped: CardDataService, ttl: int = 3600):
        self.wrapped = wrapped
        self.cache = {}
        self.ttl = ttl
    
    def get_card_by_name(self, name: str, exact: bool = True) -> Optional[Dict[str, Any]]:
        cache_key = f"{name}:{exact}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self.wrapped.get_card_by_name(name, exact)
        self.cache[cache_key] = result
        return result
```

## Migration Notes

### What Changed?

1. **Removed direct Scryfall dependency** from `CardDataManager`
   - Old: `scryfall_client: Optional[ScryfallClient]`
   - New: `card_data_service: Optional[CardDataService]`

2. **ManagerRegistry now manages the service**
   - Old: Created `ScryfallClient` directly
   - New: Creates `ScryfallCardDataService` (which wraps the client)

3. **All API calls go through the service**
   - Old: `self.scryfall_client.get_card_by_name(...)`
   - New: `self.card_data_service.get_card_by_name(...)`

### Backward Compatibility

✅ **Fully backward compatible** - All existing code works without changes!
- Default behavior uses Scryfall (same as before)
- Same method signatures
- Same data formats

### What's Still the Same?

- Scryfall is still the default provider
- Same API for fetching cards
- Same caching strategy
- Same Card entities
- Same storage layer

## Testing

Test that services are working:

```python
from mtg_card_app.interfaces.card_data import ScryfallCardDataService

# Create service
service = ScryfallCardDataService()

# Test basic functionality
print(service.get_service_name())  # "Scryfall"
print(service.supports_bulk_data())  # True

# Test fetching a card
card_data = service.get_card_by_name("Lightning Bolt")
print(card_data['name'])  # "Lightning Bolt"

# Test stats
stats = service.get_stats()
print(stats['service'])  # "Scryfall"
print(stats['total_requests'])  # Number of API calls made
```

## Summary

This refactor creates a clean, modular architecture where:

1. **Business logic** (CardDataManager) doesn't care about the data source
2. **Services** implement the `CardDataService` interface
3. **Default behavior** remains unchanged (Scryfall)
4. **Future extensions** are easy to add
5. **Testing** becomes much simpler with mock services

The system is now **open for extension, closed for modification** - you can add new data providers without touching existing code! 🎉
