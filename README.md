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

### Running the Main Application

After installation, you can run the main application:

```bash
# Using the installed script
mtg-card-app

# Using python -m
python -m mtg_card_app
```

### Running Submodules Independently

Each submodule can be run independently:

#### Deck Builder Module

```bash
# Using the installed script
mtg-deck-builder

# Using python -m
python -m mtg_card_app.deck_builder

# With options
mtg-deck-builder --name "My Awesome Deck"
mtg-deck-builder --interactive
```

#### Card Search Module

```bash
# Using the installed script
mtg-card-search

# Using python -m
python -m mtg_card_app.card_search

# With search options
mtg-card-search --name "Lightning"
mtg-card-search --color Red
mtg-card-search --type Instant
mtg-card-search --interactive
```

### Programmatic Usage

You can also use the package programmatically in your Python code:

```python
from mtg_card_app.deck_builder import DeckBuilder
from mtg_card_app.card_search import CardSearch

# Build a deck
deck = DeckBuilder("My Deck")
deck.add_card("Lightning Bolt", 4)
deck.list_cards()

# Search for cards
searcher = CardSearch()
results = searcher.search_by_name("bolt")
searcher.print_results(results)
```

See `examples/usage_example.py` for more detailed examples.

## Examples

Run the example script to see all features in action:

```bash
python examples/usage_example.py
```

## Features

- **Modular Design**: Independent modules for different functionality
- **Multiple Entry Points**: Run modules independently or through the main app
- **Interactive Mode**: Interactive command-line interfaces for deck building and card searching
- **Programmatic API**: Use the package in your own Python scripts

## Development

### Running Tests

```bash
pytest
```

### Project Configuration

The package uses `pyproject.toml` for configuration and follows modern Python packaging standards.

## License

MIT License - see LICENSE file for details.
