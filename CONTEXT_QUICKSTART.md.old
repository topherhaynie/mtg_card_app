# Quick Start for New Context Windows

**Last Updated:** October 21, 2025  
**Purpose:** Get up to speed in <5 minutes when starting a new conversation

---

## 🎯 TL;DR - What Is This Project?

**MTG Card App** - AI-powered Magic: The Gathering assistant that helps players discover cards, build decks, and explore combos through natural language conversation.

**Current Status:** Phase 5.1 Complete ✅  
**Next Phase:** Phase 6 (CLI + LLM Providers + Installation) 📋  
**Ready to Code:** YES ✅

---

## 📊 Project Health

| Metric | Status |
|--------|--------|
| **Code Quality** | ✅ 0 linting errors |
| **Tests** | ✅ 169 unit, 18 integration (all passing) |
| **Database** | ✅ 35,402 cards in SQLite |
| **Performance** | ✅ <1ms card lookups, <5ms semantic search |
| **Architecture** | ✅ Clean, well-documented, ready for Phase 6 |
| **Planning** | ✅ Phase 6 & 7 comprehensively planned |

---

## 📚 Essential Documents (Read These First)

### 1. Architecture Understanding
**[docs/architecture/ARCHITECTURE_OVERVIEW.md](docs/architecture/ARCHITECTURE_OVERVIEW.md)**

- Complete system architecture (Interface → Business Logic → Services → Storage)
- All 16 Interactor methods documented with examples
- Data flow patterns
- Phase 6 extension points

**Read if:** Starting any development work

### 2. What's Been Built
**[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)**

- Phases 1-5 complete (Data Layer, RAG, LLM, MCP, Deck Builder, SQLite)
- Current capabilities
- Performance metrics
- Testing strategy

**Read if:** Need to understand what features exist

### 3. What's Next
**[docs/phases/PHASE_6_PLAN.md](docs/phases/PHASE_6_PLAN.md)**

- CLI Interface (conversational + direct commands)
- LLM Provider abstraction (Ollama, OpenAI, Anthropic, Gemini, Groq)
- Installation system (Docker, pip, native)
- 2-3 week timeline, 3 parallel tracks

**Read if:** Implementing Phase 6

### 4. Future Vision
**[docs/phases/PHASE_7_PLAN.md](docs/phases/PHASE_7_PLAN.md)**

- Web UI with FastAPI backend + React frontend
- Chat interface + quick action buttons
- Local hosting (localhost:3000)
- 3-4 week timeline

**Read if:** Planning ahead

---

## 🏗️ Architecture at a Glance

```
Interfaces (MCP ✅, CLI 📋, Web 📋)
    ↓
Interactor (16 public methods - SINGLE SOURCE OF TRUTH)
    ↓
ManagerRegistry (Service Locator)
    ↓
Managers (CardData, RAG, LLM, Database, DeckBuilder)
    ↓
Services (SQLite, JSON, ChromaDB, Scryfall, Ollama)
    ↓
Storage (cards.db, combos.json, chroma/)
```

**Key Principle:** All business logic goes through `Interactor`. Interfaces (CLI, Web, MCP) just call `Interactor` methods and format output.

---

## 🔧 Current Capabilities (Interactor Methods)

### Card Operations (6)
```python
interactor.fetch_card("Sol Ring")
interactor.search_cards("blue instants")
interactor.import_cards(["Lightning Bolt", "Counterspell"])
interactor.get_budget_cards(max_price=5.0)
interactor.answer_natural_language_query("show me red burn spells")
interactor.find_combo_pieces("Isochron Scepter", n_results=5)
```

### Combo Operations (3)
```python
interactor.create_combo(["Card A", "Card B"], name="My Combo")
interactor.find_combos_by_card("Thassa's Oracle")
interactor.get_budget_combos(max_price=50.0)
```

### Deck Operations (5)
```python
interactor.build_deck("commander", card_pool, commander="Muldrotha")
interactor.validate_deck(deck)
interactor.analyze_deck(deck)
interactor.suggest_cards(deck, constraints={"theme": "graveyard", "budget": 100})
interactor.export_deck(deck, format="moxfield")
```

### System Operations (2)
```python
interactor.get_system_stats()
interactor.initialize_with_sample_data()
```

**All of these are fully implemented, tested, and ready to expose via CLI/Web.**

---

## 🚀 Phase 6 Implementation Roadmap

### Track 1: CLI Interface (Week 1-2)

**Goal:** Conversational CLI with direct commands

**Files to Create:**
```
mtg_card_app/ui/cli/
├── main.py              # Entry point: `mtg` command
├── chat.py              # Interactive REPL mode
├── commands/
│   ├── search.py        # mtg search → Interactor.search_cards()
│   ├── card.py          # mtg card → Interactor.fetch_card()
│   ├── combo.py         # mtg combo → Interactor combo methods
│   ├── deck.py          # mtg deck → Interactor deck methods
│   ├── import.py        # mtg import → Interactor.import_cards()
│   ├── config.py        # mtg config → Read/write config
│   └── stats.py         # mtg stats → Interactor.get_system_stats()
└── formatters/
    ├── card.py          # Pretty-print Card entities
    ├── combo.py         # Pretty-print Combo entities
    └── deck.py          # Pretty-print Deck entities
```

**Dependencies to Add:**
```toml
click = "~=8.1"          # CLI framework
rich = "~=13.0"          # Terminal formatting
prompt-toolkit = "~=3.0" # Interactive REPL
pydantic-settings = "~=2.0" # Config management
```

**Pattern:**
```python
# Every CLI command follows this pattern:
@click.command()
@click.argument('query')
def search(query):
    registry = ManagerRegistry.get_instance()
    interactor = registry.interactor
    results = interactor.search_cards(query)
    display_cards(results)  # Rich formatting
```

### Track 2: LLM Providers (Week 1-2)

**Goal:** Support multiple LLM providers (user choice)

**Files to Create:**
```
mtg_card_app/managers/llm/services/
├── base.py              # LLMService protocol (exists)
├── ollama_service.py    # Existing ✅
├── openai_service.py    # New
├── anthropic_service.py # New
├── gemini_service.py    # New
└── groq_service.py      # New
```

**Configuration:**
```toml
# ~/.mtg/config.toml
[llm]
provider = "ollama"  # or openai, anthropic, gemini, groq

[llm.ollama]
base_url = "http://localhost:11434"
model = "llama3"

[llm.openai]
api_key = "${OPENAI_API_KEY}"
model = "gpt-4o-mini"
```

### Track 3: Installation (Week 2-3)

**Goal:** Easy installation with pre-computed data

**Components:**
1. **Pre-computed data bundle** (~100 MB)
   - SQLite database (35k cards)
   - ChromaDB embeddings
   - Hosted on GitHub Releases

2. **Docker image**
   - Pre-built with everything
   - `docker run ghcr.io/topherhaynie/mtg-card-app`

3. **pip/pipx package**
   - Setup wizard: `mtg setup`
   - Downloads pre-computed data
   - Configures LLM provider

4. **Native installers** (Phase 6.1)
   - .dmg (macOS)
   - .deb/.rpm (Linux)
   - .exe (Windows)

---

## 💻 Development Workflow

### Setup Development Environment
```bash
# Clone repo
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest  # 169 unit tests (~40s)
pytest -m e2e  # 18 integration tests (~2 min)
```

### Create Feature Branch
```bash
git checkout -b phase-6-cli  # or phase-6-llm, phase-6-install
```

### Run Linting
```bash
ruff check .  # Should show 0 errors
```

### Typical Development Cycle
```bash
# 1. Make changes
# 2. Run tests
pytest tests/unit/ui/cli/  # Test your new code

# 3. Check linting
ruff check mtg_card_app/ui/cli/

# 4. Commit
git add mtg_card_app/ui/cli/
git commit -m "feat(cli): Add search command"

# 5. Push and open PR
git push origin phase-6-cli
```

---

## 🧪 Testing Strategy

### Unit Tests (Fast - ~40s)
```bash
pytest tests/unit/
```
- Test each component in isolation
- Mock dependencies
- 169 tests covering all Interactor methods

### Integration Tests (Medium - ~2 min)
```bash
pytest tests/integration/
```
- Test end-to-end workflows
- Real database (test data)
- 18 tests

### E2E Tests (Slow - ~30s each)
```bash
pytest -m e2e
```
- Real Ollama LLM
- Real Scryfall API
- Only run when needed

### New Test Pattern
```python
# tests/unit/ui/cli/test_search_command.py
def test_search_command():
    # Arrange
    mock_registry = Mock()
    mock_interactor = Mock()
    mock_registry.interactor = mock_interactor
    mock_interactor.search_cards.return_value = [test_card]
    
    # Act
    result = cli_search("Lightning Bolt", registry=mock_registry)
    
    # Assert
    assert "Lightning Bolt" in result
    mock_interactor.search_cards.assert_called_once()
```

---

## 📝 Code Style Guidelines

### Type Annotations
```python
# ✅ Modern (Python 3.10+)
def fetch_card(name: str) -> Card | None:
    cards: list[Card] = []
    metadata: dict[str, Any] = {}

# ❌ Old style (don't use)
from typing import Dict, List
def fetch_card(name: str) -> Optional[Card]:
    cards: List[Card] = []
```

### Docstrings
```python
def fetch_card(name: str) -> Card | None:
    """Fetch a card by name.
    
    Args:
        name: Card name to search for
        
    Returns:
        Card entity if found, None otherwise
        
    Example:
        >>> card = interactor.fetch_card("Sol Ring")
        >>> print(card.name)
        Sol Ring
    """
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Fetching card: %s", card_name)
logger.debug("Cache hit for query: %s", query)
logger.warning("Card not found: %s", card_name)
logger.error("Failed to connect to Scryfall: %s", e)
```

---

## 🔍 Common Tasks

### Add a New CLI Command
1. Create file in `mtg_card_app/ui/cli/commands/`
2. Import `ManagerRegistry` and get `interactor`
3. Call appropriate `interactor.method()`
4. Format output using Rich
5. Register command in `main.py`
6. Write unit tests

### Add a New LLM Provider
1. Create file in `mtg_card_app/managers/llm/services/`
2. Implement `LLMService` protocol
3. Add configuration to `~/.mtg/config.toml` format
4. Update `DependencyManager` to instantiate provider
5. Write unit tests

### Add a New Interactor Method
1. Add method to `mtg_card_app/core/interactor.py`
2. Use existing managers (don't create new dependencies)
3. Write docstring with example
4. Write unit tests in `tests/unit/core/test_interactor.py`
5. Update `ARCHITECTURE_OVERVIEW.md` with new capability

---

## 🐛 Debugging Tips

### Check What's in the Database
```python
from mtg_card_app.core.manager_registry import ManagerRegistry

registry = ManagerRegistry.get_instance()
card_service = registry.db_manager.card_service

# Count cards
print(f"Total cards: {card_service.count()}")

# Search
results = card_service.search("Lightning Bolt")
for card in results:
    print(f"{card.name} - ${card.usd}")
```

### Test Interactor Methods Directly
```python
from mtg_card_app.core.manager_registry import ManagerRegistry

registry = ManagerRegistry.get_instance()
interactor = registry.interactor

# Test card fetch
card = interactor.fetch_card("Sol Ring")
print(card.to_dict())

# Test natural language query
response = interactor.answer_natural_language_query(
    "show me blue counterspells under $5"
)
print(response)
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all logger.debug() calls will show
```

---

## ❓ FAQ

**Q: Where is the main business logic?**  
A: `mtg_card_app/core/interactor.py` - ALL business logic goes here.

**Q: How do I add a new feature?**  
A: Add method to Interactor, then expose via interface (CLI/Web/MCP).

**Q: Can I call managers directly from CLI/Web?**  
A: No, always call through Interactor. Keeps logic centralized and testable.

**Q: Where should I put CLI-specific code?**  
A: `mtg_card_app/ui/cli/` - formatting, argument parsing, display logic only.

**Q: How do I swap SQLite for PostgreSQL?**  
A: Create new service implementing `BaseService[Card]`, inject via `DependencyManager`.

**Q: Where are the tests?**  
A: `tests/unit/` (fast), `tests/integration/` (medium), `tests/e2e/` (slow).

**Q: Why is QueryOrchestrator gone?**  
A: Removed in Phase 3.5 refactor. Interactor is now single source of truth.

**Q: Do I need Ollama running?**  
A: Only for LLM features (natural language queries, combo analysis). Card lookup works without it.

---

## 📞 Getting Help

1. **Read the architecture overview** - Most questions answered there
2. **Check existing tests** - Show how to use each component
3. **Look at examples/** - Working demos of key features
4. **Review Phase 6 plan** - Detailed implementation guidance

---

## ✅ Ready to Start?

1. Read **ARCHITECTURE_OVERVIEW.md** (5 min)
2. Read **PHASE_6_PLAN.md** (10 min)
3. Choose a track (CLI, LLM, or Installation)
4. Create feature branch
5. Start coding!

**You're now fully up to speed. Happy coding! 🚀**

---

**Last Updated:** October 21, 2025  
**Next Review:** After Phase 6 completion  
**Maintained by:** Project Lead
