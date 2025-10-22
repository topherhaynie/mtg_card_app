# MTG Card App

An application for finding new MTG card combos.

## Installation

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app
pip install -e .
```

### For Development

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Package Structure

The package is organized into modules and submodules that can be run independently:

```
mtg_card_app/
├── __init__.py          # Main package initialization
├── __main__.py          # Main entry point
├── deck_builder/        # Deck building module
│   ├── __init__.py      # Module functionality
│   └── __main__.py      # Standalone entry point
└── card_search/         # Card search module
    ├── __init__.py      # Module functionality
    └── __main__.py      # Standalone entry point
```

## Usage

### MCP Server

You can run the MCP server in two modes: the classic stdio server (default) or the official MCP Python server.

Run classic (default):

```bash
python -m mtg_card_app.interfaces.mcp
```

Run the official MCP server (requires the `mcp` package, already declared in pyproject):

```bash
python -m mtg_card_app.interfaces.mcp --server official
```

Or set an environment default:

```bash
MCP_SERVER=official python -m mtg_card_app.interfaces.mcp
```

With uv (optional):

```bash
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt
```

### Running the Main Application

After installation, you can run the main application:

```bash
# Using the installed script
mtg-card-app

# Using python -m
python -m mtg_card_app
```

### Command Line Interfaces

Two CLIs are provided for quick testing and scripting.

#### Deck Builder CLI

```bash
# Build a deck from a pool file (newline-delimited card names)
mtg-deck-builder build \
    --format Commander \
    --pool cards.txt \
    --commander "Edgar Markov" \
    --metadata '{"theme":"vampires"}'

# Validate a deck JSON
mtg-deck-builder validate --deck deck.json

# Analyze a deck JSON (curve, types, colors, issues)
mtg-deck-builder analyze --deck deck.json

# Suggest cards with basic constraints
mtg-deck-builder suggest --deck deck.json --constraints '{"budget":200}'

# Suggest cards with advanced combo controls
mtg-deck-builder suggest --deck deck.json --constraints '{
  "theme": "control",
  "budget": 100.0,
  "power": 7,
  "combo_mode": "focused",
  "combo_limit": 3,
  "combo_types": ["infinite_mana", "infinite_draw"],
  "exclude_cards": ["Thassa'\''s Oracle"],
  "sort_by": "power",
  "explain_combos": true
}'

# Export deck to various formats
mtg-deck-builder export --deck deck.json --format text --output deck.txt
mtg-deck-builder export --deck deck.json --format moxfield
mtg-deck-builder export --deck deck.json --format arena --output arena_deck.txt

# Alternatively, run with python -m
python -m mtg_card_app.deck_builder suggest --deck deck.json
```

##### Constraint Options

When using `suggest`, the following constraint keys are available:

- **theme** (str): Deck theme/archetype (e.g., "control", "aggro", "combo")
- **budget** (float): Maximum total price in USD
- **power** (int): Target power level from 1 (casual) to 10 (cEDH)
- **banned** (list): Card names to exclude from suggestions
- **n_results** (int): Maximum number of suggestions to return
- **combo_mode** (str): "focused" (strict constraints) or "broad" (all relevant)
- **combo_limit** (int): Maximum combos to show per suggestion
- **combo_types** (list): Filter by combo types:
  - `infinite_mana`, `infinite_draw`, `infinite_damage`, `infinite_life`
  - `infinite_tokens`, `infinite_mill`, `lock`, `one_shot`, `engine`, `synergy`, `other`
- **exclude_cards** (list): Additional cards to exclude from combos
- **sort_by** (str): Sort results by:
  - `power` (default): By ranking score
  - `price`: Cheapest first
  - `popularity`: Most popular first
  - `complexity`: Simplest first
- **explain_combos** (bool): Include LLM-powered explanations for each combo

##### Export Formats

When using `export`, the following formats are available:

- **text**: Plain text with sections and headers (human-readable)
- **json**: JSON format (programmatic access)
- **moxfield**: Moxfield.com import format
- **mtgo**: Magic Online format
- **arena**: MTG Arena format (with set codes if available)
- **archidekt**: Archidekt.com import format

#### Card Search CLI

```bash
# Fuzzy search by name; prints JSON list of cards
mtg-card-search search --name "Lightning Bolt"

# Natural language query via RAG + LLM
mtg-card-search query --text "best blue counterspells under $5"

# Find combo pieces for a card
mtg-card-search combos --card "Isochron Scepter" --n 3

# Alternatively, run with python -m
python -m mtg_card_app.card_search query --text "efficient removal"
```

### Programmatic Usage

You can also use the package programmatically in your Python code:

```python
from mtg_card_app.core.manager_registry import ManagerRegistry
from mtg_card_app.domain.entities.deck import Deck

interactor = ManagerRegistry.get_instance().interactor

# Search for cards
cards = interactor.search_cards("Lightning Bolt")
cards_json = [c.to_dict() for c in cards]

# Build/validate/analyze/suggest deck
pool = [f"Card{i}" for i in range(1, 101)]
deck = interactor.build_deck("Commander", pool, commander="Card1", metadata={"theme": "control"})
valid = interactor.validate_deck(Deck.from_dict(deck.to_dict()))
analysis = interactor.analyze_deck(Deck.from_dict(deck.to_dict()))
suggestions = interactor.suggest_cards(Deck.from_dict(deck.to_dict()), {"budget": 200})
```

See `examples/usage_example.py` for more detailed examples.

## Examples

Run the example script to see all features in action:

```bash
python examples/usage_example.py
```

## Architecture

### Data Storage

The application uses a hybrid storage approach optimized for scale:

- **Cards**: SQLite database (`data/cards.db`) with indexed lookups
  - 35,000+ cards with <1ms lookup performance
  - Case-insensitive name search
  - Efficient filtering by colors, type, CMC, rarity
  - 6 indexes for fast queries

- **Combos**: JSON file (`data/combos.json`)
  - ~1,000 combos optimized for this scale
  - Fast enough for frequent reads

- **Vector Embeddings**: ChromaDB (`data/chroma/`)
  - 35,000+ card embeddings for semantic search
  - Used by RAG system for natural language queries

### Performance

- **Card lookups**: <1ms average (21.9x faster than JSON)
- **Deck suggestions**: ~18ms with warm cache
- **Cache hit rate**: 78.1% on repeated queries
- **Scalability**: Ready for 100k+ cards

### Key Components

- **Interactor**: Central orchestration layer
- **Managers**: Domain-specific business logic (Cards, RAG, LLM, Deck Building)
- **Services**: Pluggable implementations (Scryfall, Ollama, ChromaDB, SQLite)
- **Protocols**: Interface definitions for swappable services

## Features

- **Modular Design**: Independent modules for different functionality
- **Multiple Entry Points**: Run modules independently or through the main app
- **Interactive Mode**: Interactive command-line interfaces for deck building and card searching
- **Programmatic API**: Use the package in your own Python scripts
- **High Performance**: Sub-millisecond card lookups, sub-second suggestions
- **Scalable Storage**: SQLite for 35k+ cards with room to grow

## Development

### Running Tests

```bash
pytest
```

### Project Configuration

The package uses `pyproject.toml` for configuration and follows modern Python packaging standards.

## License

MIT License - see LICENSE file for details.
