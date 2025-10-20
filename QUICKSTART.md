# MTG Card App - Quick Start Guide

This document provides a quick reference for all the ways to use the mtg_card_app package.

## Installation

```bash
# Install from source
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Running the Application

### 1. Main Application Entry Point

```bash
# Using the installed script
mtg-card-app

# Using python -m
python -m mtg_card_app

# Get version
mtg-card-app --version

# Get help
mtg-card-app -h
```

### 2. Running Submodules Independently

#### Deck Builder

```bash
# Basic usage
python -m mtg_card_app.deck_builder
mtg-deck-builder

# With custom deck name
mtg-deck-builder --name "My Awesome Deck"

# Interactive mode
mtg-deck-builder --interactive
```

#### Card Search

```bash
# Basic usage
python -m mtg_card_app.card_search
mtg-card-search

# Search by name
mtg-card-search --name "Lightning"

# Search by color
mtg-card-search --color Red

# Search by type
mtg-card-search --type Instant

# Multiple filters
mtg-card-search --color Blue --type Instant

# Interactive mode
mtg-card-search --interactive
```

### 3. Using Main App with Subcommands

```bash
# Run deck builder through main app
python -m mtg_card_app deck-builder
python -m mtg_card_app deck-builder --name "Cool Deck"

# Run card search through main app
python -m mtg_card_app card-search
python -m mtg_card_app card-search --name "bolt"
python -m mtg_card_app card-search --color Green
```

## Programmatic Usage

### Basic Import and Usage

```python
from mtg_card_app.deck_builder import DeckBuilder
from mtg_card_app.card_search import CardSearch

# Create and use a deck builder
deck = DeckBuilder("My Deck")
deck.add_card("Lightning Bolt", 4)
deck.add_card("Mountain", 20)
deck.list_cards()

# Search for cards
searcher = CardSearch()
results = searcher.search_by_name("bolt")
searcher.print_results(results)
```

### Using Helper Functions

```python
from mtg_card_app.deck_builder import create_deck, add_card_to_deck
from mtg_card_app.card_search import search_by_name, search_by_color

# Using helper functions
deck = create_deck("Control Deck")
add_card_to_deck(deck, "Counterspell", 4)

# Search using helper functions
cards = search_by_name("Lightning")
blue_cards = search_by_color("Blue")
```

### Full Example

```python
from mtg_card_app.deck_builder import DeckBuilder
from mtg_card_app.card_search import CardSearch

# Search for cards
searcher = CardSearch()
red_cards = searcher.search_by_color("Red")
instants = [c for c in red_cards if "Instant" in c["type"]]

# Build a deck with found cards
deck = DeckBuilder("Red Burn")
for card in instants:
    deck.add_card(card["name"], 4)
deck.add_card("Mountain", 20)

# Display the deck
deck.list_cards()
```

## Running the Example

```bash
python examples/usage_example.py
```

## Package Structure

```
mtg_card_app/
├── __init__.py          # Package initialization with version and exports
├── __main__.py          # Main entry point with subcommand support
├── deck_builder/        # Deck building module
│   ├── __init__.py      # DeckBuilder class and helper functions
│   └── __main__.py      # Standalone entry point
└── card_search/         # Card search module
    ├── __init__.py      # CardSearch class and helper functions
    └── __main__.py      # Standalone entry point
```

## Key Features

1. **Multiple Entry Points**: Run the package or individual modules
2. **Submodule Independence**: Each module can run standalone
3. **Interactive Modes**: Interactive CLI for deck building and searching
4. **Programmatic API**: Import and use in your own Python code
5. **Command-line Arguments**: Full argparse support for all modules
6. **Proper Package Structure**: Follows Python best practices

## Development

The package uses modern Python packaging with `pyproject.toml`:
- Build system: setuptools
- Entry points defined for all scripts
- Development dependencies separated
- Follows PEP 517/518 standards
