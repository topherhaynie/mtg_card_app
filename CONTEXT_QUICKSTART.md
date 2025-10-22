# Quick Start for New Context Windows# Quick Start for New Context Windows



**Last Updated:** October 21, 2025  **Last Updated:** October 21, 2025  

**Purpose:** Get up to speed in <5 minutes when starting a new conversation**Purpose:** Get up to speed in <5 minutes when starting a new conversation



------



## 🎯 TL;DR - What Is This Project?## 🎯 TL;DR - What Is This Project?



**MTG Card App** - AI-powered Magic: The Gathering assistant with conversational CLI, semantic search, combo discovery, and AI deck building.**MTG Card App** - AI-powered Magic: The Gathering assistant that helps players discover cards, build decks, and explore combos through natural language conversation.



**Current Status:** Phase 6 Tracks 1 & 2 Complete ✅  **Current Status:** Phase 5.1 Complete ✅  

**Next Phase:** Phase 6 Track 3 (Installation & Packaging) or Phase 7 (Web UI) 📋  **Next Phase:** Phase 6 (CLI + LLM Providers + Installation) 📋  

**Ready to Use:** YES ✅ - Full CLI available via `mtg` command**Ready to Code:** YES ✅



------



## 📊 Project Health## 📊 Project Health



| Metric | Status || Metric | Status |

|--------|--------||--------|--------|

| **CLI Interface** | ✅ Complete - 11 commands, chat mode, setup wizard || **Code Quality** | ✅ 0 linting errors |

| **LLM Providers** | ✅ 5 providers (Ollama, OpenAI, Anthropic, Gemini, Groq) || **Tests** | ✅ 169 unit, 18 integration (all passing) |

| **Tests** | ✅ 186 tests (36/50 config, 169 core - all passing/expected) || **Database** | ✅ 35,402 cards in SQLite |

| **Database** | ✅ 35,402 cards in SQLite (<1ms lookups) || **Performance** | ✅ <1ms card lookups, <5ms semantic search |

| **Performance** | ✅ 1,111x improvement (18ms suggestions vs 20+ seconds) || **Architecture** | ✅ Clean, well-documented, ready for Phase 6 |

| **Architecture** | ✅ Clean, tested, documented || **Planning** | ✅ Phase 6 & 7 comprehensively planned |



------



## 🚀 Try It Now## 📚 Essential Documents (Read These First)



```bash### 1. Architecture Understanding

# Interactive chat mode**[docs/architecture/ARCHITECTURE_OVERVIEW.md](docs/architecture/ARCHITECTURE_OVERVIEW.md)**

mtg

- Complete system architecture (Interface → Business Logic → Services → Storage)

# View system stats- All 16 Interactor methods documented with examples

mtg stats- Data flow patterns

- Phase 6 extension points

# Find a card

mtg card "Lightning Bolt"**Read if:** Starting any development work



# Find combos### 2. What's Been Built

mtg combo find "Thassa's Oracle"**[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)**



# Build a deck- Phases 1-5 complete (Data Layer, RAG, LLM, MCP, Deck Builder, SQLite)

mtg deck new commander --commander "Muldrotha"- Current capabilities

- Performance metrics

# Get suggestions- Testing strategy

mtg deck suggest my_deck.json --theme "graveyard" --budget 200

**Read if:** Need to understand what features exist

# Setup wizard

mtg setup### 3. What's Next

**[docs/phases/PHASE_6_PLAN.md](docs/phases/PHASE_6_PLAN.md)**

# Update card database

mtg update- CLI Interface (conversational + direct commands)

```- LLM Provider abstraction (Ollama, OpenAI, Anthropic, Gemini, Groq)

- Installation system (Docker, pip, native)

---- 2-3 week timeline, 3 parallel tracks



## 📚 Essential Documents**Read if:** Implementing Phase 6



### 1. **README.md** - Start Here!### 4. Future Vision

Comprehensive user guide with:**[docs/phases/PHASE_7_PLAN.md](docs/phases/PHASE_7_PLAN.md)**

- Installation & setup

- All CLI commands with examples- Web UI with FastAPI backend + React frontend

- LLM provider configuration- Chat interface + quick action buttons

- Architecture overview- Local hosting (localhost:3000)

- 3-4 week timeline

### 2. **PROJECT_ROADMAP.md** - Status & Plans

- Phases 1-6 (Tracks 1 & 2) complete**Read if:** Planning ahead

- Phase 6 Track 3 & Phase 7 planned

- Performance metrics---

- Timeline estimates

## 🏗️ Architecture at a Glance

### 3. **docs/architecture/ARCHITECTURE_OVERVIEW.md** - System Design

- Complete architecture (16 Interactor methods)```

- Data flow patternsInterfaces (MCP ✅, CLI 📋, Web 📋)

- Extension points for new interfaces    ↓

Interactor (16 public methods - SINGLE SOURCE OF TRUTH)

### 4. **docs/phases/PHASE_6_TRACK_2_SUMMARY.md** - LLM Providers    ↓

- 5 provider implementationsManagerRegistry (Service Locator)

- Configuration system (TOML + env vars)    ↓

- Provider factory patternManagers (CardData, RAG, LLM, Database, DeckBuilder)

    ↓

---Services (SQLite, JSON, ChromaDB, Scryfall, Ollama)

    ↓

## 🏗️ Architecture at a GlanceStorage (cards.db, combos.json, chroma/)

```

```

┌─────────────────────────────────────────┐**Key Principle:** All business logic goes through `Interactor`. Interfaces (CLI, Web, MCP) just call `Interactor` methods and format output.

│     User Interfaces                      │

│  ┌──────┐  ┌──────┐  ┌──────────────┐  │---

│  │ CLI  │  │ MCP  │  │  Web (Future) │  │

│  │✅    │  │✅    │  │  📋           │  │## 🔧 Current Capabilities (Interactor Methods)

│  └──┬───┘  └──┬───┘  └──────┬───────┘  │

└─────┼─────────┼───────────────┼─────────┘### Card Operations (6)

      │         │               │```python

      └─────────┼───────────────┘interactor.fetch_card("Sol Ring")

                │interactor.search_cards("blue instants")

     ┌──────────▼──────────┐interactor.import_cards(["Lightning Bolt", "Counterspell"])

     │    Interactor       │interactor.get_budget_cards(max_price=5.0)

     │ (16 public methods) │interactor.answer_natural_language_query("show me red burn spells")

     └──────────┬──────────┘interactor.find_combo_pieces("Isochron Scepter", n_results=5)

                │```

     ┌──────────▼──────────┐

     │  ManagerRegistry    │### Combo Operations (3)

     └──┬─────┬──────┬─────┘```python

        │     │      │interactor.create_combo(["Card A", "Card B"], name="My Combo")

  ┌─────▼──┐ ┌▼───┐ ┌▼────┐interactor.find_combos_by_card("Thassa's Oracle")

  │CardData│ │RAG │ │LLM  │interactor.get_budget_combos(max_price=50.0)

  │Manager │ │Mgr │ │Mgr  │```

  │SQLite  │ │Chroma│ │Multi│

  │35k cards│ │DB  │ │Prov│### Deck Operations (5)

  └────────┘ └────┘ └────┘```python

```interactor.build_deck("commander", card_pool, commander="Muldrotha")

interactor.validate_deck(deck)

**Key Principle:** All business logic in `Interactor`. Interfaces just call methods and format output.interactor.analyze_deck(deck)

interactor.suggest_cards(deck, constraints={"theme": "graveyard", "budget": 100})

---interactor.export_deck(deck, format="moxfield")

```

## 📋 CLI Commands (All Available Now!)

### System Operations (2)

### Interactive Mode```python

```bashinteractor.get_system_stats()

mtg                    # Start chat (primary interface)interactor.initialize_with_sample_data()

mtg chat "question"    # Single question```

```

**All of these are fully implemented, tested, and ready to expose via CLI/Web.**

### Card Commands

```bash---

mtg card "Lightning Bolt"              # Card details (rich)

mtg card "Sol Ring" --format json      # JSON output## 🚀 Phase 6 Implementation Roadmap

mtg search "blue counterspells"        # Search

```### Track 1: CLI Interface (Week 1-2)



### Combo Commands**Goal:** Conversational CLI with direct commands

```bash

mtg combo find "Isochron Scepter"      # Semantic search**Files to Create:**

mtg combo search "Thoracle"            # Combo database```

mtg combo budget 100                   # Under $100mtg_card_app/ui/cli/

mtg combo create "Card A" "Card B"     # Custom combo├── main.py              # Entry point: `mtg` command

```├── chat.py              # Interactive REPL mode

├── commands/

### Deck Commands│   ├── search.py        # mtg search → Interactor.search_cards()

```bash│   ├── card.py          # mtg card → Interactor.fetch_card()

mtg deck new commander --commander "Muldrotha"│   ├── combo.py         # mtg combo → Interactor combo methods

mtg deck build deck.txt --format commander --theme "graveyard"│   ├── deck.py          # mtg deck → Interactor deck methods

mtg deck validate my_deck.json│   ├── import.py        # mtg import → Interactor.import_cards()

mtg deck analyze my_deck.json│   ├── config.py        # mtg config → Read/write config

mtg deck suggest my_deck.json --budget 200 --combo-mode focused│   └── stats.py         # mtg stats → Interactor.get_system_stats()

mtg deck export my_deck.json arena└── formatters/

```    ├── card.py          # Pretty-print Card entities

    ├── combo.py         # Pretty-print Combo entities

### Config Commands    └── deck.py          # Pretty-print Deck entities

```bash```

mtg config show                        # Display config

mtg config set llm.provider openai     # Change provider**Dependencies to Add:**

mtg config providers                   # List providers```toml

```click = "~=8.1"          # CLI framework

rich = "~=13.0"          # Terminal formatting

### System Commandsprompt-toolkit = "~=3.0" # Interactive REPL

```bashpydantic-settings = "~=2.0" # Config management

mtg stats              # System statistics```

mtg setup              # Interactive setup wizard

mtg update             # Download/update cards**Pattern:**

``````python

# Every CLI command follows this pattern:

---@click.command()

@click.argument('query')

## 🤖 LLM Provider Configurationdef search(query):

    registry = ManagerRegistry.get_instance()

### Available Providers    interactor = registry.interactor

    results = interactor.search_cards(query)

| Provider | Status | Install |    display_cards(results)  # Rich formatting

|----------|--------|---------|```

| Ollama | ✅ Always available | Built-in |

| Gemini | ⚠️ Optional | `pip install mtg-card-app[gemini]` |### Track 2: LLM Providers (Week 1-2)

| Groq | ⚠️ Optional | `pip install mtg-card-app[groq]` |

| OpenAI | ⚠️ Optional | `pip install mtg-card-app[openai]` |**Goal:** Support multiple LLM providers (user choice)

| Anthropic | ⚠️ Optional | `pip install mtg-card-app[anthropic]` |

**Files to Create:**

### Setup```

mtg_card_app/managers/llm/services/

```bash├── base.py              # LLMService protocol (exists)

# Interactive├── ollama_service.py    # Existing ✅

mtg setup├── openai_service.py    # New

├── anthropic_service.py # New

# Manual├── gemini_service.py    # New

mtg config set llm.provider openai└── groq_service.py      # New

export OPENAI_API_KEY="sk-..."```



# For Ollama (free, local)**Configuration:**

ollama pull llama3```toml

mtg config set llm.provider ollama# ~/.mtg/config.toml

```[llm]

provider = "ollama"  # or openai, anthropic, gemini, groq

---

[llm.ollama]

## 🧪 Running Testsbase_url = "http://localhost:11434"

model = "llama3"

```bash

# All tests[llm.openai]

pytestapi_key = "${OPENAI_API_KEY}"

model = "gpt-4o-mini"

# Specific categories```

pytest tests/unit/config/              # Config system (36/50 passing)

pytest tests/unit/core/                # Core logic (169 passing)### Track 3: Installation (Week 2-3)

pytest tests/integration/              # Integration tests

**Goal:** Easy installation with pre-computed data

# With coverage

pytest --cov=mtg_card_app**Components:**

```1. **Pre-computed data bundle** (~100 MB)

   - SQLite database (35k cards)

---   - ChromaDB embeddings

   - Hosted on GitHub Releases

## 📁 Key Files to Know

2. **Docker image**

### Configuration   - Pre-built with everything

- **~/.mtg/config.toml** - User configuration (LLM provider, API keys, cache settings)   - `docker run ghcr.io/topherhaynie/mtg-card-app`

- **mtg_card_app/config/manager.py** - Config manager (TOML + env vars)

- **mtg_card_app/config/provider_factory.py** - LLM provider factory3. **pip/pipx package**

   - Setup wizard: `mtg setup`

### CLI   - Downloads pre-computed data

- **mtg_card_app/ui/cli/main.py** - CLI entry point (Click framework)   - Configures LLM provider

- **mtg_card_app/ui/cli/chat.py** - Interactive chat mode (Rich REPL)

- **mtg_card_app/ui/cli/commands/** - All CLI commands:4. **Native installers** (Phase 6.1)

  - `card.py` - Card details   - .dmg (macOS)

  - `combo.py` - Combo operations   - .deb/.rpm (Linux)

  - `deck.py` - Deck operations   - .exe (Windows)

  - `config.py` - Configuration

  - `search.py` - Card search---

  - `stats.py` - System stats

  - `setup.py` - Setup wizard (432 lines)## 💻 Development Workflow

  - `update.py` - Data updates (233 lines with progress bars)

### Setup Development Environment

### Core Business Logic```bash

- **mtg_card_app/core/interactor.py** - Main orchestration (16 methods)# Clone repo

- **mtg_card_app/core/manager_registry.py** - Service locatorgit clone https://github.com/topherhaynie/mtg_card_app.git

- **mtg_card_app/core/dependency_manager.py** - Service containercd mtg_card_app



### Data# Create virtual environment

- **data/cards.db** - SQLite database (35,402 cards)python3.13 -m venv .venv

- **data/combos.json** - Combo database (~1,000 combos)source .venv/bin/activate

- **data/chroma/** - Vector embeddings (ChromaDB)

# Install dependencies

---pip install -e .

pip install -r requirements-dev.txt

## 🎯 Current Development Focus

# Run tests

### ✅ Completed (Phase 6 Tracks 1 & 2)pytest  # 169 unit tests (~40s)

pytest -m e2e  # 18 integration tests (~2 min)

**Track 1: CLI Interface**```

- ✅ Conversational chat mode (primary interface)

- ✅ 11 direct commands (card, combo, deck, config, system)### Create Feature Branch

- ✅ Rich terminal UI (progress bars, tables, panels)```bash

- ✅ Interactive setup wizardgit checkout -b phase-6-cli  # or phase-6-llm, phase-6-install

- ✅ Data update with detailed progress```



**Track 2: LLM Providers**### Run Linting

- ✅ 5 provider implementations```bash

- ✅ Configuration system (TOML + env vars)ruff check .  # Should show 0 errors

- ✅ Provider factory pattern```

- ✅ Optional dependencies (install what you need)

- ✅ 50 unit tests (36 passing, 14 expected failures for optional deps)### Typical Development Cycle

```bash

### 📋 Next Up (Choose One)# 1. Make changes

# 2. Run tests

**Option 1: Track 3 - Installation & Packaging**pytest tests/unit/ui/cli/  # Test your new code

- Docker image with pre-computed data

- pip/pipx package improvements# 3. Check linting

- Native installers (.dmg, .deb, .exe)ruff check mtg_card_app/ui/cli/

- Pre-computed data bundle (~100 MB)

- Setup wizard enhancements# 4. Commit

git add mtg_card_app/ui/cli/

**Option 2: Phase 7 - Web UI**git commit -m "feat(cli): Add search command"

- FastAPI backend (wraps Interactor)

- React + Tailwind + shadcn/ui frontend# 5. Push and open PR

- Chat interface (primary)git push origin phase-6-cli

- Quick action buttons (secondary)```

- Local hosting (localhost:3000)

---

**Option 3: Documentation & Polish**

- CLI user guide with examples## 🧪 Testing Strategy

- API documentation

- Video tutorials### Unit Tests (Fast - ~40s)

- Performance benchmarks```bash

- More example scriptspytest tests/unit/

```

---- Test each component in isolation

- Mock dependencies

## 🛠️ Development Workflow- 169 tests covering all Interactor methods



### Starting Development### Integration Tests (Medium - ~2 min)

```bash

```bashpytest tests/integration/

# 1. Check current state```

git status- Test end-to-end workflows

mtg stats- Real database (test data)

- 18 tests

# 2. Run tests to ensure everything works

pytest### E2E Tests (Slow - ~30s each)

```bash

# 3. Read relevant docspytest -m e2e

# - README.md for user perspective```

# - docs/architecture/ for system design- Real Ollama LLM

# - docs/phases/ for implementation details- Real Scryfall API

- Only run when needed

# 4. Make changes

### New Test Pattern

# 5. Test```python

pytest# tests/unit/ui/cli/test_search_command.py

mtg <command>  # Manual testingdef test_search_command():

    # Arrange

# 6. Commit with descriptive message    mock_registry = Mock()

git add -A    mock_interactor = Mock()

git commit -m "feat: Add feature X"    mock_registry.interactor = mock_interactor

```    mock_interactor.search_cards.return_value = [test_card]

    

### Adding a New CLI Command    # Act

    result = cli_search("Lightning Bolt", registry=mock_registry)

1. **Create command file**: `mtg_card_app/ui/cli/commands/mycommand.py`    

2. **Implement with Click**: Use `@click.command()` or `@click.group()`    # Assert

3. **Call Interactor**: Use existing Interactor methods    assert "Lightning Bolt" in result

4. **Format output**: Use Rich for beautiful terminal output    mock_interactor.search_cards.assert_called_once()

5. **Register**: Add to `main.py` with `cli.add_command()````

6. **Test manually**: Run `mtg mycommand`

7. **Document**: Add to README and this file---



### Adding a New LLM Provider## 📝 Code Style Guidelines



1. **Create service**: `mtg_card_app/managers/llm/services/myprovider_service.py`### Type Annotations

2. **Implement protocol**: Follow `LLMService` protocol```python

3. **Add to factory**: Update `provider_factory.py`# ✅ Modern (Python 3.10+)

4. **Add optional dep**: Update `pyproject.toml` optional-dependenciesdef fetch_card(name: str) -> Card | None:

5. **Test**: Write unit tests in `tests/unit/config/`    cards: list[Card] = []

6. **Document**: Update README provider table    metadata: dict[str, Any] = {}



---# ❌ Old style (don't use)

from typing import Dict, List

## 🚨 Common Issues & Solutionsdef fetch_card(name: str) -> Optional[Card]:

    cards: List[Card] = []

### "Card not found"```

- Run `mtg update` to download card database

- Database might be empty or outdated### Docstrings

```python

### "LLM provider not available"def fetch_card(name: str) -> Card | None:

- Install provider: `pip install mtg-card-app[openai]`    """Fetch a card by name.

- Or use Ollama (always available)    

    Args:

### "Config file error"        name: Card name to search for

- Delete `~/.mtg/config.toml` and run `mtg setup`        

- Config will be regenerated with defaults    Returns:

        Card entity if found, None otherwise

### "Tests failing"        

- 14 config tests expected to fail (optional deps not installed)    Example:

- Run `pytest tests/unit/core/` for core tests only        >>> card = interactor.fetch_card("Sol Ring")

        >>> print(card.name)

### "Slow performance"        Sol Ring

- First run generates cache (slower)    """

- Subsequent runs use cache (fast)```

- Clear cache if issues: `rm -rf ~/.mtg/cache`

### Logging

---```python

import logging

## 📊 Performance Expectationslogger = logging.getLogger(__name__)



- **Card lookup**: <1ms (SQLite with indexes)logger.info("Fetching card: %s", card_name)

- **Deck suggestions**: ~18ms with cache, ~2s coldlogger.debug("Cache hit for query: %s", query)

- **Semantic search**: <5ms (ChromaDB HNSW)logger.warning("Card not found: %s", card_name)

- **LLM queries**: 1-10s depending on providerlogger.error("Failed to connect to Scryfall: %s", e)

- **Cache hit rate**: 78% on repeated queries```



------



## 🎓 Key Concepts## 🔍 Common Tasks



### Interactor Pattern### Add a New CLI Command

- **Single source of truth** for business logic1. Create file in `mtg_card_app/ui/cli/commands/`

- All interfaces call Interactor methods2. Import `ManagerRegistry` and get `interactor`

- Pure business logic, no UI concerns3. Call appropriate `interactor.method()`

4. Format output using Rich

### Manager Pattern5. Register command in `main.py`

- Each domain has a manager (CardData, RAG, LLM, DeckBuilder)6. Write unit tests

- Managers use services (protocols for swappability)

- Centralized via ManagerRegistry### Add a New LLM Provider

1. Create file in `mtg_card_app/managers/llm/services/`

### Service Protocol2. Implement `LLMService` protocol

- Interface definition (Protocol)3. Add configuration to `~/.mtg/config.toml` format

- Multiple implementations (SQLite, JSON, Ollama, OpenAI, etc.)4. Update `DependencyManager` to instantiate provider

- Dependency injection via DependencyManager5. Write unit tests



### Configuration System### Add a New Interactor Method

- TOML-based (`~/.mtg/config.toml`)1. Add method to `mtg_card_app/core/interactor.py`

- Environment variable support (`${VAR_NAME}`)2. Use existing managers (don't create new dependencies)

- Dotted key access (`config.get("llm.provider")`)3. Write docstring with example

- Provider factory for LLM instantiation4. Write unit tests in `tests/unit/core/test_interactor.py`

5. Update `ARCHITECTURE_OVERVIEW.md` with new capability

---

---

## 💡 Tips for Success

## 🐛 Debugging Tips

1. **Start with README.md** - Best overview of current state

2. **Use `mtg` command** - See the CLI in action### Check What's in the Database

3. **Read architecture docs** - Understand before changing```python

4. **Run tests often** - Catch issues earlyfrom mtg_card_app.core.manager_registry import ManagerRegistry

5. **Follow existing patterns** - Consistency matters

6. **Ask questions** - Reference docs are comprehensiveregistry = ManagerRegistry.get_instance()

card_service = registry.db_manager.card_service

---

# Count cards

## 📞 Need Help?print(f"Total cards: {card_service.count()}")



- **Architecture**: Read `docs/architecture/ARCHITECTURE_OVERVIEW.md`# Search

- **Current features**: Run `mtg --help` or `mtg stats`results = card_service.search("Lightning Bolt")

- **Next steps**: Check `PROJECT_ROADMAP.md`for card in results:

- **Specific phase**: Read `docs/phases/PHASE_X_*.md`    print(f"{card.name} - ${card.usd}")

```

---

### Test Interactor Methods Directly

**Updated:** October 21, 2025  ```python

**Status:** Phase 6 Tracks 1 & 2 Complete | Ready for Track 3 or Phase 7  from mtg_card_app.core.manager_registry import ManagerRegistry

**Quick Command:** `mtg` to start using the app! 🎉

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
