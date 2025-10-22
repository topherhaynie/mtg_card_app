# Phase 6: CLI Interface & Infrastructure

**Status:** ✅ Tracks 1 & 2 COMPLETE | 📋 Track 3 IN PLANNING  
**Created:** October 21, 2025  
**Completed:** Tracks 1 & 2 - October 21, 2025  
**Duration:** ~2 weeks (Tracks 1 & 2)  
**Scope:** CLI ✅ + LLM Providers ✅ + Installation System 📋

---

## Implementation Status

### ✅ Track 1: CLI Interface - COMPLETE
- **11 commands implemented** (chat + 10 direct)
- **Interactive chat mode** with Rich REPL
- **Setup wizard** (432 lines, 4-step process)
- **Update command** with detailed progress bars (233 lines)
- **Comprehensive documentation** (README, CLI Guide, Setup Guide)
- **See:** `docs/phases/PHASE_6_TRACK_1_SUMMARY.md`

### ✅ Track 2: LLM Provider System - COMPLETE
- **5 provider implementations** (Ollama, OpenAI, Anthropic, Gemini, Groq)
- **Configuration system** (TOML + environment variables)
- **Provider factory pattern**
- **Optional dependencies**
- **50 unit tests** (36 passing, 14 expected failures)
- **See:** `docs/phases/PHASE_6_TRACK_2_SUMMARY.md`

### 📋 Track 3: Installation & Packaging - IN PLANNING
- Docker image with pre-computed data
- PyPI package publication
- Native installers (.dmg, .deb, .exe)
- Pre-computed data bundle
- CI/CD pipeline

---

## Executive Summary

Phase 6 creates the user-facing command-line interface and supporting infrastructure:

**Primary Goal:** Conversational CLI (chat with your MTG collection like talking to Claude)  
**Secondary Goal:** LLM provider flexibility (choose free or paid options)  
**Tertiary Goal:** Easy installation (Docker, pip, native packages with pre-computed data)

**Phase 7 Scope:** Web UI (builds on Phase 6 infrastructure)

---

## User Experience Vision

### Primary Interface: Conversational (80% of usage)
```bash
$ mtg
🎴 MTG Card App - Chat Mode
Connected to: Ollama (llama3) | 35,402 cards loaded

> show me blue counterspells under $5
[Assistant analyzes query and searches...]

Found 15 blue counterspells under $5:
1. Counterspell - $3.50
2. Negate - $0.25
3. Dispel - $0.15
...

> what combos work with Thoracle?
[Assistant finds combo pieces...]

Top combos with Thassa's Oracle:
1. Thoracle + Demonic Consultation (cEDH, 99% win rate)
   Power Level: 10/10
   Budget: $350
   [View Details] [Add to Deck]
...

> exit
Goodbye! ✨
```

### Secondary Interface: Direct Commands (20% of usage)
```bash
$ mtg search "Lightning Bolt"
$ mtg combo "Isochron Scepter" --limit 5
$ mtg deck build --commander "Muldrotha" --budget 200
```

Direct commands are **shortcuts** that bypass LLM routing for power users.

---

## Architecture

### Three Parallel Development Tracks

```
┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│  Track 1: CLI       │  │ Track 2: LLM Providers│  │ Track 3: Install   │
│  (Week 1-2)         │  │ (Week 1-2)           │  │ (Week 2-3)         │
│                     │  │                      │  │                    │
│  • Chat mode        │  │ • Provider protocol  │  │ • Pre-computed data│
│  • Direct commands  │  │ • OpenAI            │  │ • Docker image     │
│  • Rich formatting  │  │ • Anthropic         │  │ • pip package      │
│  • Config system    │  │ • Gemini (free!)    │  │ • Native install   │
└─────────────────────┘  └──────────────────────┘  └─────────────────────┘
         │                         │                          │
         └─────────────────────────┴──────────────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  Integration      │
                         │  & Testing        │
                         │  (Week 3)         │
                         └───────────────────┘
```

**Key Decision:** Tracks 1 & 2 are **independent** - CLI works with Ollama while we add providers

---

## Track 1: CLI Interface

### Module Structure
```
mtg_card_app/ui/cli/
├── __init__.py
├── main.py                 # Entry point, router
├── chat.py                 # Interactive chat mode (REPL)
├── commands/
│   ├── __init__.py
│   ├── search.py          # Direct search command
│   ├── combo.py           # Direct combo command
│   ├── deck.py            # Deck builder commands
│   ├── config.py          # Configuration commands
│   └── stats.py           # System stats
├── formatters/
│   ├── __init__.py
│   ├── card.py            # Card display formatting
│   ├── combo.py           # Combo display formatting
│   ├── deck.py            # Deck display formatting
│   └── table.py           # Table utilities (Rich)
└── utils.py               # Shared utilities
```

### Capability Inventory

**Current Interactor Methods (all must be exposed):**

**Card Operations:**
- `fetch_card(name)` - Get single card by name
- `search_cards(query, use_scryfall)` - Search with Scryfall syntax
- `import_cards(card_names)` - Bulk import from Scryfall
- `get_budget_cards(max_price)` - Find cards under price
- `answer_natural_language_query(query)` - RAG + LLM query answering
- `find_combo_pieces(card_name, n_results)` - Semantic combo discovery

**Combo Operations:**
- `create_combo(card_names, name, description)` - Manual combo creation
- `find_combos_by_card(card_name)` - Find existing combos with card
- `get_budget_combos(max_price)` - Find combos under price

**Deck Operations:**
- `build_deck(format, card_pool, commander, constraints, metadata)` - Construct deck
- `validate_deck(deck)` - Check format legality
- `analyze_deck(deck)` - Mana curve, type distribution, weaknesses
- `suggest_cards(deck, constraints)` - AI-powered suggestions with combos
- `export_deck(deck, format)` - Export to text/json/moxfield/mtgo/arena/archidekt

**System Operations:**
- `get_system_stats()` - Card count, cache stats, service info
- `initialize_with_sample_data()` - Load test data

### Command Design

#### Primary: Conversational Mode (80% of usage)
```bash
mtg                    # Start interactive chat
mtg chat               # Explicit chat mode
mtg "your question"    # Single-shot chat query
```

**Chat Mode Features:**
- Persistent conversation context
- Command history (up/down arrows)
- Auto-completion
- Colorized output with Rich
- Streaming LLM responses
- Special commands: `/help`, `/exit`, `/clear`, `/history`

**Chat Examples:**
```
> show me blue counterspells under $5
> what combos work with Thoracle?
> build a Muldrotha deck with $200 budget
> analyze my deck and suggest improvements
> find cards similar to Sol Ring
```

The LLM routes to appropriate Interactor methods automatically.

#### Secondary: Direct Commands (20% of usage - power users, scripting)

**Search Commands:**
```bash
mtg search <query>                    # Natural language search via RAG
mtg search "Lightning Bolt" --exact   # Exact name match
mtg search "bolt" --fuzzy             # Fuzzy name matching
mtg search "type:instant cmc<=2"      # Scryfall syntax search
mtg search --budget 5                 # Budget filter
mtg search --format json              # JSON output for scripting

# Examples:
mtg search "blue counterspells"
mtg search "t:creature cmc<=3 c:g" --limit 20
mtg search --budget 10 --format json > cheap_cards.json
```

**Card Detail Commands:**
```bash
mtg card <name>                       # Show card details
mtg card "Sol Ring" --format json    # JSON output
mtg card "Mana Crypt" --prices       # Show all price data

# Examples:
mtg card "Black Lotus"
mtg card "Thassa's Oracle" --prices
```

**Combo Commands:**
```bash
mtg combo find <card_name>            # Find combos with card (semantic)
mtg combo find "Isochron Scepter" --limit 5
mtg combo find "Thoracle" --power cedh

mtg combo search <card_name>          # Search existing combo database
mtg combo search "Demonic Consultation"

mtg combo create <card1> <card2> ...  # Manually create combo
mtg combo create "Thassa's Oracle" "Demonic Consultation" --name "Thoracle Win"

mtg combo budget <max_price>          # Find combos under price
mtg combo budget 50

# Examples:
mtg combo find "Isochron Scepter"
mtg combo search "Dramatic Reversal" 
mtg combo budget 100 --format json
mtg combo create "Card A" "Card B" --name "My Combo"
```

**Deck Commands:**
```bash
mtg deck new <format>                 # Create new deck
mtg deck new commander --commander "Muldrotha"

mtg deck build <file>                 # Build from card pool
mtg deck build cards.txt --format commander --budget 200

mtg deck validate <file>              # Check legality
mtg deck validate my_deck.txt

mtg deck analyze <file>               # Analyze mana curve, types, etc.
mtg deck analyze my_deck.txt --format markdown

mtg deck suggest <file> [options]     # AI-powered suggestions
mtg deck suggest my_deck.txt --theme "graveyard"
mtg deck suggest my_deck.txt --budget 50 --combo-mode focused
mtg deck suggest my_deck.txt --sort-by power --explain-combos

mtg deck export <file> <format>       # Export deck
mtg deck export my_deck.txt moxfield
mtg deck export my_deck.txt arena > arena_import.txt
mtg deck export my_deck.txt json

# Deck suggestion options:
# --theme <theme>           Deck archetype
# --budget <max>            Max card price
# --power <level>           Power level 1-10
# --combo-mode <mode>       "focused" or "broad"
# --combo-limit <n>         Max combos per suggestion
# --sort-by <method>        "power", "price", "popularity", "complexity"
# --explain-combos          Add LLM explanations
# --exclude <cards>         Exclude specific cards

# Examples:
mtg deck new commander --commander "Muldrotha the Gravetide"
mtg deck validate commander_deck.txt
mtg deck analyze commander_deck.txt
mtg deck suggest commander_deck.txt --theme "graveyard" --budget 100
mtg deck export commander_deck.txt moxfield > import.txt
```

**Import Commands:**
```bash
mtg import <card_names...>            # Import cards from Scryfall
mtg import "Sol Ring" "Mana Crypt" "Demonic Tutor"
mtg import --file cards.txt           # Import from file (one per line)
mtg import --fuzzy                    # Use fuzzy matching

# Examples:
mtg import "Lightning Bolt" "Counterspell"
mtg import --file popular_cards.txt
```

**Configuration Commands:**
```bash
mtg config show                       # Show all settings
mtg config get <key>                  # Get specific setting
mtg config set <key> <value>          # Set setting

mtg config set llm.provider openai
mtg config set llm.openai.api_key sk-...
mtg config set llm.model gpt-4o-mini
mtg config set cache.enabled true

# Examples:
mtg config show
mtg config get llm.provider
mtg config set llm.provider anthropic
```

**System Commands:**
```bash
mtg stats                             # System statistics
mtg stats --cache                     # Cache statistics
mtg stats --format json

mtg update                            # Update to latest cards
mtg update --force                    # Force re-download

mtg setup                             # First-time setup wizard
mtg setup --provider ollama           # Skip provider selection

mtg version                           # Show version
mtg help [command]                    # Show help

# Examples:
mtg stats
mtg update
mtg help deck suggest
```

### Technology Stack

**CLI Framework:** `click` (mature, powerful)  
**Rich Output:** `rich` (beautiful terminal UI)  
**REPL:** `prompt-toolkit` (interactive mode)  
**Config:** `pydantic-settings` (validation)

**Dependencies to add:**
```toml
[project.dependencies]
# ... existing ...
click = "~=8.1"
rich = "~=13.0"
prompt-toolkit = "~=3.0"
pydantic-settings = "~=2.0"
```

### Implementation Steps

**Step 1: Basic CLI (Day 1-2)**
- [ ] Create `cli/main.py` with Click groups
- [ ] Implement `mtg search` command
- [ ] Implement `mtg combo` command
- [ ] Wire to existing Interactor
- [ ] Basic text output (no formatting)

**Step 2: Chat Mode (Day 3-4)**
- [ ] Create `cli/chat.py` with prompt-toolkit REPL
- [ ] Implement conversation loop
- [ ] Stream LLM responses
- [ ] Add command history
- [ ] Special commands (/help, /exit)

**Step 3: Rich Formatting (Day 5-6)**
- [ ] Implement formatters (card, combo, deck)
- [ ] Add Rich tables and panels
- [ ] Color-code mana symbols
- [ ] Progress indicators for slow ops
- [ ] Multiple output formats (human, JSON, markdown)

**Step 4: Direct Commands (Day 7-8)**
- [ ] Implement deck commands
- [ ] Implement config commands
- [ ] Implement stats commands
- [ ] Add helpful error messages

**Step 5: Polish (Day 9-10)**
- [ ] Tab completion
- [ ] Help text for all commands
- [ ] Examples in help
- [ ] Error handling

**Deliverable:** Production-ready conversational CLI

---

## Track 2: LLM Provider Abstraction

### Current State
- Hard-coded to Ollama + Llama3

### Goal
- Support multiple LLM providers
- User can choose based on needs (free vs paid, speed vs privacy)

### Provider Options

| Provider | Cost | Speed | Privacy | Free Tier |
|----------|------|-------|---------|-----------|
| **Ollama** | Free | Slow (5-10s) | Complete | ✅ Unlimited |
| **Gemini** | Free/Paid | Fast (1-2s) | Google | ✅ 15 req/min |
| **Groq** | Free/Paid | Very Fast (<1s) | Groq | ✅ 30 req/min |
| **OpenAI** | Paid | Fast (1-2s) | OpenAI | ❌ Pay per use |
| **Anthropic** | Paid | Fast (1-2s) | Anthropic | ❌ Pay per use |

### Architecture

```python
# mtg_card_app/managers/llm/providers/
├── base.py              # LLMProvider protocol
├── ollama.py            # Existing implementation
├── openai_provider.py   # New
├── anthropic_provider.py # New
├── gemini_provider.py   # New
└── groq_provider.py     # New
```

**Provider Protocol:**
```python
from typing import Protocol

class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Iterator[str]:
        """Generate response from LLM."""
        ...
    
    def get_info(self) -> dict[str, Any]:
        """Get provider info (model, version, etc.)."""
        ...
```

### Configuration

```toml
# ~/.mtg/config.toml

[llm]
provider = "ollama"  # or "openai", "anthropic", "gemini", "groq"
model = "llama3"

[llm.ollama]
base_url = "http://localhost:11434"
model = "llama3"

[llm.openai]
api_key = "${OPENAI_API_KEY}"  # Or direct value
model = "gpt-4o-mini"
max_tokens = 1000

[llm.anthropic]
api_key = "${ANTHROPIC_API_KEY}"
model = "claude-3-5-sonnet-20241022"
max_tokens = 1000

[llm.gemini]
api_key = "${GOOGLE_API_KEY}"
model = "gemini-1.5-flash"

[llm.groq]
api_key = "${GROQ_API_KEY}"
model = "llama-3.1-70b-versatile"
```

### Implementation Steps

**Step 1: Protocol Definition (Day 1)**
- [ ] Create `LLMProvider` protocol
- [ ] Refactor existing `OllamaLLMService` to match protocol
- [ ] Update `LLMManager` to use protocol

**Step 2: OpenAI Provider (Day 2)**
- [ ] Implement `OpenAIProvider`
- [ ] Add openai SDK dependency
- [ ] Test with real API key

**Step 3: Anthropic Provider (Day 3)**
- [ ] Implement `AnthropicProvider`
- [ ] Add anthropic SDK dependency
- [ ] Test with real API key

**Step 4: Gemini Provider (Day 4)**
- [ ] Implement `GeminiProvider`
- [ ] Add google-generativeai SDK dependency
- [ ] Test with free tier

**Step 5: Groq Provider (Day 5)**
- [ ] Implement `GroqProvider`
- [ ] Add groq SDK dependency
- [ ] Test with free tier

**Step 6: Configuration System (Day 6-7)**
- [ ] Create config file structure
- [ ] Add provider selection logic
- [ ] Add `mtg config` commands
- [ ] Environment variable support
- [ ] Validation and error handling

**Deliverable:** Flexible LLM provider system

---

## Track 3: Installation & Setup

### Goals
1. **Pre-computed Data**: No 20-minute wait on first install
2. **Multiple Install Methods**: Docker, pip, native packages
3. **Easy Setup**: Wizard for configuration
4. **Incremental Updates**: Download new cards without regenerating everything

### Pre-computed Data Bundle

**Contents:**
```
mtg-data-v1.0.0.tar.xz  (~100 MB compressed)
├── cards.db            # SQLite (35,402 cards)
├── chroma/             # Vector embeddings
└── VERSION             # Build date/version
```

**Storage:**
- Hosted on GitHub Releases (2 GB file limit - we're 100 MB)
- Automatic download during `mtg setup`
- Extracted to `~/.mtg/data/`

**Update Mechanism:**
```bash
$ mtg update
Checking for updates...
Current version: 2025-10-21
Latest version: 2025-11-15
Found 147 new cards

Download updates? (100 MB) [y/N]: y
Downloading... ████████████████ 100%
Importing new cards...
Generating embeddings... ████████████████ 147/147
✓ Updated to version 2025-11-15
```

### Installation Methods

#### 1. Docker (Fastest - 2 minutes)
```bash
docker pull ghcr.io/topherhaynie/mtg-card-app:latest
docker run -p 3000:3000 mtg-card-app

# Or with docker-compose:
services:
  mtg-app:
    image: ghcr.io/topherhaynie/mtg-card-app:latest
    ports:
      - "3000:3000"
    volumes:
      - ~/.mtg:/root/.mtg  # Persist config
```

**Includes:**
- Pre-built database
- Pre-computed embeddings
- Web UI ready
- Ollama NOT included (configure external LLM)

#### 2. pip/pipx (Recommended - 5 minutes)
```bash
pipx install mtg-card-app

# First-time setup
mtg setup

🎴 MTG Card App - First Time Setup

Step 1/3: Download Card Database
  Downloading pre-computed data (100 MB)...
  ████████████████████████████████ 100%
  ✓ Extracted 35,402 cards

Step 2/3: Configure LLM
  Choose your AI provider:
  
  1. Ollama (Free, Local, Private) - Recommended for beginners
  2. OpenAI (Paid, Fast, $0.50/100 queries)
  3. Anthropic Claude (Paid, Best Quality, $1/100 queries)
  4. Google Gemini (Free Tier: 15 req/min)
  5. Groq (Free Tier: 30 req/min)
  6. Skip (configure later)
  
  Choice [1]: 1
  
  ✓ Ollama detected at http://localhost:11434
  ✓ Model llama3 available

Step 3/3: Test Connection
  Testing database... ✓
  Testing embeddings... ✓
  Testing LLM... ✓
  
🎉 Setup complete! Run 'mtg' to start.
```

#### 3. Native Installers (Coming Soon - 5 minutes)
```
macOS:  MTGCardApp-1.0.0.dmg
Linux:  mtg-card-app_1.0.0_amd64.deb
        mtg-card-app-1.0.0-1.x86_64.rpm
Windows: MTGCardApp-Setup-1.0.0.exe
```

**Created with:**
- macOS: `create-dmg` or `py2app`
- Linux: `fpm` (deb/rpm packages)
- Windows: `pyinstaller` + Inno Setup

**Includes:**
- Python runtime bundled
- Pre-computed data
- Desktop icon
- Uninstaller

### Implementation Steps

**Step 1: Pre-computed Data (Day 1-2)**
- [ ] Create build script for data bundle
- [ ] Generate tarball with SQLite + ChromaDB
- [ ] Upload to GitHub Releases
- [ ] Test download and extraction

**Step 2: Setup Wizard (Day 3-4)**
- [ ] Create `mtg setup` command
- [ ] Download pre-computed data
- [ ] LLM provider selection
- [ ] Configuration file creation
- [ ] Connection testing

**Step 3: Docker Image (Day 5-6)**
- [ ] Create Dockerfile
- [ ] Multi-stage build (minimize size)
- [ ] Include pre-computed data
- [ ] GitHub Actions for auto-build
- [ ] Publish to ghcr.io

**Step 4: pip Package (Day 7)**
- [ ] Update pyproject.toml
- [ ] Entry point configuration
- [ ] Test installation
- [ ] Publish to PyPI

**Step 5: Native Installers (Day 8-10)**
- [ ] macOS .dmg creation
- [ ] Linux .deb/.rpm packages
- [ ] Windows .exe installer
- [ ] Testing on each platform

**Deliverable:** Multiple installation options with pre-computed data

---

## Integration & Testing (Week 3)

### Integration Tasks
- [ ] CLI uses provider abstraction
- [ ] Setup wizard configures providers
- [ ] Docker image works with all install methods
- [ ] Update mechanism tested

### Testing Strategy

**Unit Tests:**
- [ ] CLI command parsing
- [ ] Formatter output
- [ ] Provider implementations
- [ ] Config validation

**Integration Tests:**
- [ ] Full CLI workflows
- [ ] Provider switching
- [ ] Setup wizard

**E2E Tests:**
- [ ] Fresh install on clean system
- [ ] Chat session with each provider
- [ ] Direct commands work
- [ ] Update mechanism

**Manual Testing:**
- [ ] Docker installation
- [ ] pip installation
- [ ] User acceptance testing (3-5 people)

---

## Timeline

### Week 1: Core Development
- **Days 1-2**: Basic CLI structure + Provider protocol
- **Days 3-4**: Chat mode + OpenAI provider
- **Days 5-6**: Rich formatting + Anthropic provider
- **Day 7**: Deck commands + Gemini provider

### Week 2: Features & Infrastructure
- **Days 1-2**: Config system + Groq provider
- **Days 3-4**: Setup wizard + Pre-computed data
- **Days 5-6**: Docker image + pip package
- **Day 7**: Polish and bug fixes

### Week 3: Integration & Launch
- **Days 1-2**: Integration testing
- **Days 3-4**: E2E testing + bug fixes
- **Day 5**: Documentation
- **Days 6-7**: Launch prep + user testing

**Total:** 15-21 days

---

## Success Criteria

- [ ] ✅ Users can chat naturally with the app
- [ ] ✅ All Interactor methods accessible via CLI
- [ ] ✅ Multiple LLM providers working
- [ ] ✅ Installation takes <5 minutes
- [ ] ✅ Pre-computed data downloads automatically
- [ ] ✅ Beautiful, colorized output
- [ ] ✅ Sub-100ms response for cached queries
- [ ] ✅ Comprehensive help text
- [ ] ✅ Zero crashes on valid inputs
- [ ] ✅ All tests passing

---

## Open Questions

1. **Config Location**: `~/.mtg/config.toml` vs XDG standard?  
   **Recommendation:** `~/.mtg/` for simplicity, XDG support later

2. **Default Provider**: Ollama vs Gemini (free tier)?  
   **Recommendation:** Ollama (privacy-first), suggest Gemini for speed

3. **Data Updates**: Auto-check for updates or manual only?  
   **Recommendation:** Manual with notification ("New cards available!")

4. **Telemetry**: Anonymous usage stats?  
   **Recommendation:** No telemetry initially, opt-in later if needed

5. **Windows Support**: Priority for Phase 6?  
   **Recommendation:** macOS/Linux first, Windows in Phase 6.1

---

## Next Steps

1. **Approve this plan** ✋
2. **Set up development branches** (track-1-cli, track-2-providers, track-3-install)
3. **Start Track 1 & 2 in parallel**
4. **Daily standups** to sync progress

---

**Status:** Awaiting approval  
**Last Updated:** October 21, 2025  
**Next Review:** After Track 1 & 2 completion
