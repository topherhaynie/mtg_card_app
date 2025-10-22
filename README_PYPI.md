# MTG Card App

🎴 **AI-powered Magic: The Gathering assistant for combo discovery and deck building**

[![PyPI version](https://img.shields.io/pypi/v/mtg-card-app.svg)](https://pypi.org/project/mtg-card-app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-100%20passing-green.svg)](https://github.com/topherhaynie/mtg_card_app)

An intelligent MTG companion that combines semantic search, LLM reasoning, and conversational interfaces to help you discover cards, build decks, and explore combos through natural language.

## ✨ Features

- 🤖 **Conversational Chat Interface** - Talk to your MTG assistant naturally
- 🔍 **Semantic Search** - Find cards by meaning, not just keywords  
- 🎯 **Combo Discovery** - AI-powered combo detection with 10-factor ranking
- 🏗️ **Deck Builder** - Build, analyze, and optimize Commander/Modern/Standard decks
- ⚡ **Multiple LLM Providers** - Ollama (free, local), OpenAI, Anthropic, Gemini, Groq
- 📊 **Rich Terminal UI** - Beautiful progress bars, tables, and panels
- 💾 **High Performance** - 35k+ cards with sub-millisecond lookups
- 🔌 **MCP Integration** - Use with Claude Desktop and other MCP clients

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install mtg-card-app

# Or install with specific LLM providers
pip install mtg-card-app[openai]        # OpenAI GPT-4
pip install mtg-card-app[anthropic]     # Claude
pip install mtg-card-app[gemini]        # Google Gemini (free tier!)
pip install mtg-card-app[groq]          # Groq (fast & free)
pip install mtg-card-app[all-providers] # All providers

# For development
pip install mtg-card-app[dev]
```

### First-Time Setup

Run the interactive setup wizard:

```bash
mtg setup
```

This guides you through:
1. **Choosing an LLM provider** (Ollama, OpenAI, Anthropic, Gemini, Groq)
2. **Configuring API keys** (if needed)
3. **Downloading card data** (~2 minutes with pre-built bundle)
4. **Testing your connection**

### Start Chatting

```bash
$ mtg

🎴 Welcome to MTG Card App!

> show me blue counterspells under $5
> what combos work with Thassa's Oracle?
> build me a Muldrotha deck with a $200 budget
> /help
> /exit
```

## 💬 Usage Examples

### Interactive Chat Mode (Primary Interface)

```bash
mtg  # Start conversational interface
```

Natural language queries:
- "Show me efficient blue counterspells"
- "What combos work with Thassa's Oracle?"
- "Build a Muldrotha graveyard deck for $200"
- "Find cards similar to Lightning Bolt"

### Command-Line Interface

```bash
# Card operations
mtg card "Lightning Bolt"
mtg search "blue counterspells"

# Combo discovery
mtg combo find "Isochron Scepter"
mtg combo budget 100

# Deck building
mtg deck new commander --commander "Muldrotha"
mtg deck analyze my_deck.json
mtg deck suggest my_deck.json --budget 200

# Configuration
mtg config show
mtg config set llm.provider openai

# System
mtg stats
mtg update  # Update card database
```

## 🤖 LLM Provider Options

| Provider | Cost | Speed | Privacy | Free Tier | Install |
|----------|------|-------|---------|-----------|---------|
| **Ollama** | Free | Medium (5-10s) | Complete | ✅ Unlimited | None (local) |
| **Gemini** | Free/Paid | Fast (1-2s) | Google | ✅ 15/min | `pip install mtg-card-app[gemini]` |
| **Groq** | Free/Paid | Very Fast (<1s) | Groq | ✅ 30/min | `pip install mtg-card-app[groq]` |
| **OpenAI** | Paid | Fast (1-2s) | OpenAI | ❌ Pay/use | `pip install mtg-card-app[openai]` |
| **Anthropic** | Paid | Fast (1-2s) | Anthropic | ❌ Pay/use | `pip install mtg-card-app[anthropic]` |

### Recommended Providers

**For beginners:** Gemini or Groq (free tier, fast, no setup)  
**For privacy:** Ollama (completely local, no API keys)  
**For best quality:** Claude (Anthropic) or GPT-4 (OpenAI)

### Configure Your Provider

```bash
# Interactive setup (recommended)
mtg setup

# Manual configuration
mtg config set llm.provider openai
export OPENAI_API_KEY="sk-..."

# For Ollama (local, private)
ollama pull llama3
mtg config set llm.provider ollama
```

## 🔌 MCP Integration

Use with Claude Desktop or other MCP clients:

```bash
# Add to Claude Desktop config (~/.config/claude/claude_desktop_config.json):
{
  "mcpServers": {
    "mtg-card-app": {
      "command": "python",
      "args": ["-m", "mtg_card_app.interfaces.mcp"]
    }
  }
}
```

**Available MCP Tools:**
- `query_cards` - Natural language card search
- `search_cards` - Direct card search
- `find_combo_pieces` - Semantic combo discovery
- `explain_card` - Card analysis with AI
- `compare_cards` - Side-by-side comparison
- `build_deck` - AI-powered deck building
- `validate_deck` - Format legality check
- `analyze_deck` - Mana curve & statistics
- `suggest_cards` - Combo-aware suggestions

## 🏗️ Architecture Highlights

### Data Storage

- **Cards**: SQLite database with 35,000+ Oracle cards
  - Sub-millisecond lookups (21.9x faster than JSON)
  - Indexed by name, colors, type, CMC, rarity
  
- **Combos**: JSON file with ~1,000 curated combos
  - Ranked by 10-factor scoring system
  - Filtered by price, colors, complexity
  
- **Embeddings**: ChromaDB vector store
  - 35,000+ card embeddings for semantic search
  - HNSW indexing for fast similarity search

### Performance

- **Card lookups**: <1ms average
- **Deck suggestions**: ~18ms with warm cache
- **Cache hit rate**: 78.1% on repeated queries
- **Setup time**: ~2 minutes (with pre-built data bundle)

## 📚 Documentation

- **[Full Documentation](https://github.com/topherhaynie/mtg_card_app#readme)** - Complete guide on GitHub
- **[Architecture Overview](https://github.com/topherhaynie/mtg_card_app/tree/main/docs/architecture)** - System design
- **[API Reference](https://github.com/topherhaynie/mtg_card_app/tree/main/docs)** - Detailed API docs
- **[Examples](https://github.com/topherhaynie/mtg_card_app/tree/main/examples)** - Usage examples

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=mtg_card_app
```

## 🗺️ Roadmap

### ✅ Completed

- ✅ Data layer with SQLite + ChromaDB
- ✅ RAG-powered semantic search
- ✅ Multi-provider LLM system
- ✅ Full-featured CLI interface
- ✅ MCP integration for Claude Desktop
- ✅ Deck builder with combo awareness
- ✅ 100 passing tests

### 🚧 In Progress

- 🚧 PyPI package (this!)
- 🚧 Docker image
- 🚧 CI/CD pipeline

### 📋 Planned

- 📋 Web UI (FastAPI + React)
- 📋 Community features (deck sharing)
- 📋 Native desktop app

## 🤝 Contributing

Contributions are welcome! This project uses:
- **Python 3.10+**
- **pytest** for testing
- **ruff** for linting
- **mypy** for type checking

See [CONTRIBUTING.md](https://github.com/topherhaynie/mtg_card_app/blob/main/CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](https://github.com/topherhaynie/mtg_card_app/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- **[Scryfall](https://scryfall.com/)** - Comprehensive MTG card API
- **[OpenMTG](https://openmtg.com/)** - Combo database
- **[Sentence Transformers](https://www.sbert.net/)** - Embedding models
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[Click](https://click.palletsprojects.com/)** & **[Rich](https://rich.readthedocs.io/)** - Beautiful CLI

## 📧 Contact

- **GitHub**: [@topherhaynie](https://github.com/topherhaynie)
- **Issues**: [Report a bug](https://github.com/topherhaynie/mtg_card_app/issues)
- **Discussions**: [Ask questions](https://github.com/topherhaynie/mtg_card_app/discussions)

---

**Made with ❤️ for the MTG community**
