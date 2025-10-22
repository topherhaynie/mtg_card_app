# MTG Card App# MTG Card App



🎴 **Your AI-powered Magic: The Gathering assistant**An application for finding new MTG card combos.



An intelligent MTG companion that combines semantic search, LLM reasoning, and conversational interfaces to help you discover cards, build decks, and explore combos through natural language.## Installation



[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)### From Source

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Clone the repository and install in development mode:

---

```bash

## ✨ Featuresgit clone https://github.com/topherhaynie/mtg_card_app.git

cd mtg_card_app

- 🤖 **Conversational Chat Interface** - Talk to your MTG assistant naturallypip install -e .

- 🔍 **Semantic Search** - Find cards by meaning, not just keywords```

- 🎯 **Combo Discovery** - AI-powered combo detection with 10-factor ranking

- 🏗️ **Deck Builder** - Build, analyze, and optimize Commander/Modern/Standard decks### For Development

- ⚡ **Multiple LLM Providers** - Ollama (free, local), OpenAI, Anthropic, Gemini, Groq

- 📊 **Rich Terminal UI** - Beautiful progress bars, tables, and panelsInstall with development dependencies:

- 💾 **High Performance** - 35k+ cards with sub-millisecond lookups

- 🔌 **MCP Integration** - Use with Claude Desktop and other MCP clients```bash

pip install -e ".[dev]"

---```



## 🚀 Quick Start## Package Structure



### InstallationThe package is organized into modules and submodules that can be run independently:



```bash```

# Clone the repositorymtg_card_app/

git clone https://github.com/topherhaynie/mtg_card_app.git├── __init__.py          # Main package initialization

cd mtg_card_app├── __main__.py          # Main entry point

├── deck_builder/        # Deck building module

# Install with uv (recommended)│   ├── __init__.py      # Module functionality

uv pip install -e .│   └── __main__.py      # Standalone entry point

└── card_search/         # Card search module

# Or with pip    ├── __init__.py      # Module functionality

pip install -e .    └── __main__.py      # Standalone entry point

``````



### First-Time Setup## Usage



Run the interactive setup wizard:### MCP Server



```bashYou can run the MCP server in two modes: the classic stdio server (default) or the official MCP Python server.

mtg setup

```Run classic (default):



This will guide you through:```bash

1. Choosing an LLM provider (Ollama, OpenAI, Anthropic, Gemini, Groq)python -m mtg_card_app.interfaces.mcp

2. Configuring API keys```

3. Verifying data files

4. Testing your connectionRun the official MCP server (requires the `mcp` package, already declared in pyproject):



### Download Card Data```bash

python -m mtg_card_app.interfaces.mcp --server official

```bash```

mtg update

```Or set an environment default:



Downloads ~35,000 Oracle cards from Scryfall and generates vector embeddings for semantic search (takes 5-10 minutes).```bash

MCP_SERVER=official python -m mtg_card_app.interfaces.mcp

---```



## 💬 UsageWith uv (optional):



### Interactive Chat Mode (Primary Interface)```bash

uv pip compile pyproject.toml -o requirements.txt

Just type `mtg` to start a conversation:uv pip sync requirements.txt

```

```bash

$ mtg### Running the Main Application



🎴 Welcome to MTG Card App!After installation, you can run the main application:



> show me blue counterspells under $5```bash

# Using the installed script

> what combos work with Thassa's Oracle?mtg-card-app



> build me a Muldrotha deck with a $200 budget# Using python -m

python -m mtg_card_app

> /help           # Show available commands```

> /exit           # Quit

```### Command Line Interfaces



### Direct Commands (Quick Operations)Two CLIs are provided for quick testing and scripting.



```bash#### Deck Builder CLI

# Card Operations

mtg card "Lightning Bolt"              # Show card details```bash

mtg card "Sol Ring" --format json      # JSON output# Build a deck from a pool file (newline-delimited card names)

mtg search "blue counterspells"        # Search cardsmtg-deck-builder build \

    --format Commander \

# Combo Operations    --pool cards.txt \

mtg combo find "Isochron Scepter"      # Find combo pieces (semantic)    --commander "Edgar Markov" \

mtg combo search "Thoracle"            # Search combo database    --metadata '{"theme":"vampires"}'

mtg combo budget 100                   # Find combos under $100

mtg combo create "Card A" "Card B"     # Create custom combo# Validate a deck JSON

mtg-deck-builder validate --deck deck.json

# Deck Operations

mtg deck new commander --commander "Muldrotha"# Analyze a deck JSON (curve, types, colors, issues)

mtg deck build deck.txt --format commander --theme "graveyard"mtg-deck-builder analyze --deck deck.json

mtg deck validate my_deck.json

mtg deck analyze my_deck.json --format markdown# Suggest cards with basic constraints

mtg deck suggest my_deck.json --theme "control" --budget 200mtg-deck-builder suggest --deck deck.json --constraints '{"budget":200}'

mtg deck export my_deck.json arena --output arena_import.txt

# Suggest cards with advanced combo controls

# Configurationmtg-deck-builder suggest --deck deck.json --constraints '{

mtg config show                        # Display configuration  "theme": "control",

mtg config set llm.provider openai     # Change LLM provider  "budget": 100.0,

mtg config providers                   # List available providers  "power": 7,

  "combo_mode": "focused",

# System  "combo_limit": 3,

mtg stats                              # System statistics  "combo_types": ["infinite_mana", "infinite_draw"],

mtg setup                              # Run setup wizard  "exclude_cards": ["Thassa'\''s Oracle"],

mtg update                             # Update card database  "sort_by": "power",

```  "explain_combos": true

}'

---

# Export deck to various formats

## 🤖 LLM Provider Optionsmtg-deck-builder export --deck deck.json --format text --output deck.txt

mtg-deck-builder export --deck deck.json --format moxfield

| Provider | Cost | Speed | Privacy | Free Tier | Install |mtg-deck-builder export --deck deck.json --format arena --output arena_deck.txt

|----------|------|-------|---------|-----------|---------|

| **Ollama** | Free | Medium (5-10s) | Complete | ✅ Unlimited | None |# Alternatively, run with python -m

| **Gemini** | Free/Paid | Fast (1-2s) | Google | ✅ 15/min | `pip install mtg-card-app[gemini]` |python -m mtg_card_app.deck_builder suggest --deck deck.json

| **Groq** | Free/Paid | Very Fast (<1s) | Groq | ✅ 30/min | `pip install mtg-card-app[groq]` |```

| **OpenAI** | Paid | Fast (1-2s) | OpenAI | ❌ Pay/use | `pip install mtg-card-app[openai]` |

| **Anthropic** | Paid | Fast (1-2s) | Anthropic | ❌ Pay/use | `pip install mtg-card-app[anthropic]` |##### Constraint Options



### Configure Your ProviderWhen using `suggest`, the following constraint keys are available:



```bash- **theme** (str): Deck theme/archetype (e.g., "control", "aggro", "combo")

# Interactive setup- **budget** (float): Maximum total price in USD

mtg setup- **power** (int): Target power level from 1 (casual) to 10 (cEDH)

- **banned** (list): Card names to exclude from suggestions

# Or manually- **n_results** (int): Maximum number of suggestions to return

mtg config set llm.provider openai- **combo_mode** (str): "focused" (strict constraints) or "broad" (all relevant)

export OPENAI_API_KEY="sk-..."- **combo_limit** (int): Maximum combos to show per suggestion

- **combo_types** (list): Filter by combo types:

# For Ollama (local, private)  - `infinite_mana`, `infinite_draw`, `infinite_damage`, `infinite_life`

ollama pull llama3  - `infinite_tokens`, `infinite_mill`, `lock`, `one_shot`, `engine`, `synergy`, `other`

mtg config set llm.provider ollama- **exclude_cards** (list): Additional cards to exclude from combos

```- **sort_by** (str): Sort results by:

  - `power` (default): By ranking score

---  - `price`: Cheapest first

  - `popularity`: Most popular first

## 📚 Command Reference  - `complexity`: Simplest first

- **explain_combos** (bool): Include LLM-powered explanations for each combo

### Chat Commands

##### Export Formats

```bash

mtg                                    # Start chat modeWhen using `export`, the following formats are available:

mtg chat "show me counterspells"       # Single question

```- **text**: Plain text with sections and headers (human-readable)

- **json**: JSON format (programmatic access)

**Special commands in chat mode:**- **moxfield**: Moxfield.com import format

- `/help` - Show available commands- **mtgo**: Magic Online format

- `/exit` - Quit chat- **arena**: MTG Arena format (with set codes if available)

- `/clear` - Clear screen- **archidekt**: Archidekt.com import format



### Card Commands#### Card Search CLI



```bash```bash

# Card details# Fuzzy search by name; prints JSON list of cards

mtg card "Lightning Bolt"              # Rich format (default)mtg-card-search search --name "Lightning Bolt"

mtg card "Sol Ring" --format text      # Plain text

mtg card "Mana Crypt" --format json    # JSON output# Natural language query via RAG + LLM

mtg card "Force of Will" --prices      # Show pricing infomtg-card-search query --text "best blue counterspells under $5"



# Search cards# Find combo pieces for a card

mtg search "blue counterspells"        # Natural languagemtg-card-search combos --card "Isochron Scepter" --n 3

mtg search "t:instant cmc<=2" --limit 20  # Scryfall syntax

```# Alternatively, run with python -m

python -m mtg_card_app.card_search query --text "efficient removal"

### Combo Commands```



```bash### Programmatic Usage

# Find combo pieces (semantic search)

mtg combo find "Isochron Scepter" --limit 10You can also use the package programmatically in your Python code:



# Search combo database```python

mtg combo search "Thassa's Oracle"from mtg_card_app.core.manager_registry import ManagerRegistry

from mtg_card_app.domain.entities.deck import Deck

# Find combos under budget

mtg combo budget 100                   # Under $100interactor = ManagerRegistry.get_instance().interactor

mtg combo budget 50 --limit 20         # Top 20 under $50

# Search for cards

# Create custom combocards = interactor.search_cards("Lightning Bolt")

mtg combo create "Card A" "Card B" "Card C" \cards_json = [c.to_dict() for c in cards]

  --name "My Combo" \

  --description "Infinite mana combo"# Build/validate/analyze/suggest deck

```pool = [f"Card{i}" for i in range(1, 101)]

deck = interactor.build_deck("Commander", pool, commander="Card1", metadata={"theme": "control"})

### Deck Commandsvalid = interactor.validate_deck(Deck.from_dict(deck.to_dict()))

analysis = interactor.analyze_deck(Deck.from_dict(deck.to_dict()))

```bashsuggestions = interactor.suggest_cards(Deck.from_dict(deck.to_dict()), {"budget": 200})

# Create new deck```

mtg deck new commander --commander "Muldrotha, the Gravetide"

mtg deck new modern --output my_modern.txtSee `examples/usage_example.py` for more detailed examples.



# Build deck from scratch## Examples

mtg deck build my_deck.txt \

  --format commander \Run the example script to see all features in action:

  --theme "graveyard recursion" \

  --budget 200```bash

python examples/usage_example.py

# Validate deck```

mtg deck validate my_deck.json

## Architecture

# Analyze deck

mtg deck analyze my_deck.json                  # Rich format### Data Storage

mtg deck analyze my_deck.json --format markdown

mtg deck analyze my_deck.json --format jsonThe application uses a hybrid storage approach optimized for scale:



# Get suggestions- **Cards**: SQLite database (`data/cards.db`) with indexed lookups

mtg deck suggest my_deck.json \  - 35,000+ cards with <1ms lookup performance

  --theme "control" \  - Case-insensitive name search

  --budget 200 \  - Efficient filtering by colors, type, CMC, rarity

  --combo-mode focused  - 6 indexes for fast queries



# Export deck- **Combos**: JSON file (`data/combos.json`)

mtg deck export my_deck.json txt  - ~1,000 combos optimized for this scale

mtg deck export my_deck.json arena --output arena.txt  - Fast enough for frequent reads

mtg deck export my_deck.json moxfield

```- **Vector Embeddings**: ChromaDB (`data/chroma/`)

  - 35,000+ card embeddings for semantic search

### Configuration Commands  - Used by RAG system for natural language queries



```bash### Performance

# View configuration

mtg config show- **Card lookups**: <1ms average (21.9x faster than JSON)

mtg config get llm.provider- **Deck suggestions**: ~18ms with warm cache

- **Cache hit rate**: 78.1% on repeated queries

# Modify configuration- **Scalability**: Ready for 100k+ cards

mtg config set llm.provider openai

mtg config set llm.openai.model gpt-4o### Key Components

mtg config set cache.enabled true

- **Interactor**: Central orchestration layer

# Reset to defaults- **Managers**: Domain-specific business logic (Cards, RAG, LLM, Deck Building)

mtg config reset- **Services**: Pluggable implementations (Scryfall, Ollama, ChromaDB, SQLite)

- **Protocols**: Interface definitions for swappable services

# List providers

mtg config providers## Features

```

- **Modular Design**: Independent modules for different functionality

### System Commands- **Multiple Entry Points**: Run modules independently or through the main app

- **Interactive Mode**: Interactive command-line interfaces for deck building and card searching

```bash- **Programmatic API**: Use the package in your own Python scripts

# View statistics- **High Performance**: Sub-millisecond card lookups, sub-second suggestions

mtg stats- **Scalable Storage**: SQLite for 35k+ cards with room to grow



# Setup wizard## Development

mtg setup

### Running Tests

# Update card database

mtg update                             # Full update```bash

mtg update --force                     # Force re-downloadpytest

mtg update --cards-only                # Skip embeddings```

mtg update --embeddings-only           # Only regenerate embeddings

```### Project Configuration



---The package uses `pyproject.toml` for configuration and follows modern Python packaging standards.



## 🏗️ Architecture## License



### High-Level OverviewMIT License - see LICENSE file for details.


```
┌─────────────────────────────────────────────┐
│           User Interfaces                    │
│  ┌────────┐  ┌────────┐  ┌──────────────┐  │
│  │  CLI   │  │  MCP   │  │ Web UI       │  │
│  │ (Chat) │  │ (Claude)│  │ (Future)     │  │
│  └────┬───┘  └───┬────┘  └──────┬───────┘  │
└───────┼──────────┼───────────────┼──────────┘
        │          │               │
        └──────────┼───────────────┘
                   │
        ┌──────────▼──────────┐
        │    Interactor       │
        │ (Business Logic)    │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  ManagerRegistry    │
        │ (Service Locator)   │
        └─────┬─────┬─────┬───┘
              │     │     │
    ┌─────────▼─┐ ┌─▼───┐ ┌▼────┐
    │CardData   │ │ RAG │ │ LLM │
    │Manager    │ │ Mgr │ │ Mgr │
    │           │ │     │ │     │
    │SQLite     │ │Chroma│ │Multi│
    │35k cards  │ │DB   │ │Prov │
    └───────────┘ └─────┘ └─────┘
```

### Data Storage

- **Cards**: SQLite database (`data/cards.db`)
  - 35,000+ Oracle cards with <1ms lookups
  - 6 indexes for efficient queries (name, colors, type, CMC, rarity)
  
- **Combos**: JSON file (`data/combos.json`)
  - ~1,000 curated combos with metadata
  
- **Embeddings**: ChromaDB (`data/chroma/`)
  - 35,000+ card embeddings for semantic search
  - HNSW indexing for fast similarity search

### Performance

- **Card lookups**: <1ms average (21.9x faster than JSON)
- **Deck suggestions**: ~18ms with warm cache (1,111x improvement)
- **Cache hit rate**: 78.1% on repeated queries
- **Scalability**: Ready for 100k+ cards

---

## 🔌 MCP Integration

Use with Claude Desktop or other MCP clients:

```bash
# Run MCP server (classic mode - default)
python -m mtg_card_app.interfaces.mcp

# Run official MCP server
python -m mtg_card_app.interfaces.mcp --server official

# Or set environment default
export MCP_SERVER=official
python -m mtg_card_app.interfaces.mcp
```

**Available Tools:**
- `query_cards` - Natural language card search
- `search_cards` - Direct card search
- `find_combo_pieces` - Semantic combo discovery
- `explain_card` - Card analysis
- `compare_cards` - Side-by-side comparison
- `build_deck` - AI-powered deck building
- `validate_deck` - Format legality check
- `analyze_deck` - Mana curve & statistics
- `suggest_cards` - Combo-aware suggestions

---

## 🛠️ Development

### Installation for Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or with all providers
pip install -e ".[dev,all-providers]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mtg_card_app

# Run specific test file
pytest tests/unit/config/test_manager.py
```

### Project Structure

```
mtg_card_app/
├── config/              # Configuration system
│   ├── manager.py       # TOML config manager
│   └── provider_factory.py  # LLM provider factory
├── core/                # Business logic
│   ├── interactor.py    # Main orchestration layer
│   ├── manager_registry.py  # Service locator
│   └── dependency_manager.py  # Service container
├── domain/              # Domain entities
│   └── entities/        # Card, Deck, Combo
├── managers/            # Domain managers
│   ├── card_data/       # Card operations
│   ├── rag/             # Semantic search
│   ├── llm/             # LLM integrations
│   └── deck_building/   # Deck operations
├── interfaces/          # External interfaces
│   └── mcp/             # MCP server
└── ui/                  # User interfaces
    └── cli/             # Command-line interface
        ├── main.py      # CLI entry point
        ├── chat.py      # Interactive chat
        └── commands/    # CLI commands
```

---

## 📖 Documentation

- **[CONTEXT_QUICKSTART.md](CONTEXT_QUICKSTART.md)** - Quick reference for new sessions
- **[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)** - Development roadmap and status
- **[docs/architecture/](docs/architecture/)** - Architecture documentation
- **[docs/phases/](docs/phases/)** - Phase-by-phase implementation docs

---

## 🗺️ Roadmap

### ✅ Completed

- **Phase 1-5**: Data layer, RAG, LLM, MCP, Deck Builder
- **Phase 6 Track 1**: Full-featured CLI interface
- **Phase 6 Track 2**: Multi-provider LLM system

### 🚧 In Progress

- **Phase 6 Track 3**: Installation & packaging (Docker, pip, native installers)

### 📋 Planned

- **Phase 7**: Web UI (FastAPI + React + Tailwind)
- **Phase 8**: Community features (deck sharing, ratings)

See [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for detailed plans.

---

## 🤝 Contributing

Contributions are welcome! This project uses:
- **Python 3.13+**
- **uv** for package management
- **pytest** for testing
- **ruff** for linting
- **mypy** for type checking

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Scryfall** - Card data API
- **OpenMTG** - Combo database
- **Sentence Transformers** - Embedding models
- **ChromaDB** - Vector store
- **Click & Rich** - Beautiful CLI

---

## 📧 Contact

- **GitHub**: [@topherhaynie](https://github.com/topherhaynie)
- **Project**: [mtg_card_app](https://github.com/topherhaynie/mtg_card_app)

---

**Made with ❤️ for the MTG community**
