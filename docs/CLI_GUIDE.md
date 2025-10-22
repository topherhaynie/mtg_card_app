# CLI User Guide

**Complete reference for the MTG Card App command-line interface**

---

## Table of Contents

- [Overview](#overview)
- [Interactive Chat Mode](#interactive-chat-mode)
- [Card Commands](#card-commands)
- [Combo Commands](#combo-commands)
- [Deck Commands](#deck-commands)
- [Configuration Commands](#configuration-commands)
- [System Commands](#system-commands)
- [Advanced Usage](#advanced-usage)
- [Tips & Best Practices](#tips--best-practices)

---

## Overview

The MTG Card App provides **two interaction modes**:

1. **Conversational Chat** (recommended) - Natural language queries in interactive mode
2. **Direct Commands** - Quick one-off operations

```bash
# Conversational mode (primary interface)
mtg

# Direct commands (quick operations)
mtg card "Lightning Bolt"
mtg deck validate my_deck.json
```

### Global Options

All commands support these global flags:

```bash
--help              # Show help for any command
--version           # Show app version
--config PATH       # Use custom config file (default: ~/.mtg/config.toml)
```

---

## Interactive Chat Mode

**Primary interface** for natural language queries and conversations.

### Starting Chat

```bash
# Start interactive mode
mtg

# Ask a single question and exit
mtg chat "What are the best Thassa's Oracle combos?"
```

### Chat Features

- **Natural language queries** - Ask questions like you would a friend
- **Context awareness** - Follow-up questions remember previous context
- **Semantic search** - Finds relevant cards/combos even with imprecise language
- **Rich formatting** - Beautiful terminal output with tables and panels

### Example Conversations

```
You: What are the best commanders for a graveyard deck?
Assistant: Based on graveyard synergies, here are top picks:
  • Muldrotha, the Gravetide - Play permanents from graveyard
  • Meren of Clan Nel Toth - Recursion engine
  • Karador, Ghost Chieftain - Cost reduction for creatures

You: Tell me more about Muldrotha
Assistant: [Shows detailed card info, combos, and synergies]

You: Build me a Muldrotha deck under $200
Assistant: [Generates optimized decklist with budget constraints]
```

### Chat Commands

Within interactive mode, you can use special commands:

- **`/help`** - Show available commands
- **`/clear`** - Clear conversation history
- **`/stats`** - Show system statistics
- **`/config`** - Show current configuration
- **`/exit`** or `Ctrl+D` - Exit chat mode

### Tips for Chat Mode

1. **Be conversational** - "What combos work with Thoracle?" instead of keywords
2. **Ask follow-ups** - Context is preserved across the conversation
3. **Use constraints** - "under $100", "in Bant colors", "competitive level"
4. **Request formats** - "show as JSON", "export for Arena"

---

## Card Commands

Get detailed information about specific Magic cards.

### `mtg card`

Display comprehensive card details.

```bash
# Basic usage
mtg card "Lightning Bolt"

# With format options
mtg card "Sol Ring" --format json      # JSON output
mtg card "Counterspell" --format text  # Plain text (no colors)
mtg card "Brainstorm" --format rich    # Rich terminal (default)
```

**Output includes:**
- Card name, mana cost, type
- Oracle text
- Power/toughness (creatures)
- Rarity, set information
- Prices (USD, foil)
- Legality in all formats
- EDHREC rank and popularity

**Example:**

```bash
$ mtg card "Thassa's Oracle"

╭─────────────────── Thassa's Oracle ───────────────────╮
│                                                        │
│  Cost: {U}{U}                                         │
│  Type: Legendary Creature — Merfolk Wizard            │
│  P/T:  1/3                                            │
│                                                        │
│  Oracle Text:                                          │
│  When Thassa's Oracle enters the battlefield, look at │
│  the top X cards of your library, where X is your     │
│  devotion to blue. Put up to one of them on top of    │
│  your library and the rest on the bottom in a random  │
│  order. If X is greater than or equal to the number   │
│  of cards in your library, you win the game.          │
│                                                        │
│  Rarity: Rare                                         │
│  Set: Theros Beyond Death (THB)                       │
│  Price: $15.99 | Foil: $24.99                         │
│  EDHREC Rank: #42                                     │
│                                                        │
╰────────────────────────────────────────────────────────╯
```

### `mtg search`

Search for cards using natural language or keywords.

```bash
# Natural language
mtg search "blue counterspells that cost 2 mana"

# Keywords
mtg search "dragon creature red legendary"

# Advanced filters
mtg search "commander:golgari graveyard"
```

**Search supports:**
- Card names (fuzzy matching)
- Colors and color identity
- Types (creature, instant, artifact, etc.)
- Mana cost ranges
- Keywords (flying, hexproof, etc.)
- Format legality
- Price ranges

**Example:**

```bash
$ mtg search "legendary creatures with partner"

Found 71 cards:

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Name                 ┃ Cost   ┃ Type  ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ Akroma, Vision...    │ 5WW    │ Creat │
│ Ardenn, Intrepi...   │ 2W     │ Creat │
│ Bruse Tarl, Boo...   │ 2RW    │ Creat │
│ ...                  │ ...    │ ...   │
└──────────────────────┴────────┴───────┘
```

---

## Combo Commands

Discover, search, and create combo interactions.

### `mtg combo find`

Find combos using **semantic search** - understands meaning, not just keywords.

```bash
# Find combos with a specific card
mtg combo find "Thassa's Oracle"

# Find combos with multiple cards
mtg combo find "Isochron Scepter" "Dramatic Reversal"

# Natural language
mtg combo find "infinite mana in simic colors"
```

**Returns:**
- Combo description
- Required pieces (2-5 cards)
- Steps to execute
- Color identity
- Estimated price
- Power level

**Example:**

```bash
$ mtg combo find "Thassa's Oracle"

Found 12 combos:

╭─────────────────── Thoracle + Consultation ────────────────╮
│                                                             │
│  Cards:                                                     │
│  • Thassa's Oracle                                         │
│  • Demonic Consultation                                    │
│                                                             │
│  Steps:                                                     │
│  1. Cast Demonic Consultation naming a card not in deck    │
│  2. Exile entire library                                   │
│  3. Cast Thassa's Oracle                                   │
│  4. ETB trigger with 0 cards in library = win              │
│                                                             │
│  Colors: {U}{B}                                            │
│  Price: ~$25                                               │
│  Power: cEDH staple                                        │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### `mtg combo search`

Search the **combo database** using exact keywords.

```bash
# Search by card name
mtg combo search "Kiki-Jiki"

# Search by mechanic
mtg combo search "storm"

# Search by result
mtg combo search "infinite tokens"
```

**Difference from `find`:**
- `find` = Semantic (AI-powered, understands meaning)
- `search` = Keyword (database query, exact matches)

Use `find` for exploration, `search` for specific lookups.

### `mtg combo budget`

Find combos within a price range.

```bash
# Under $50
mtg combo budget 50

# Between $20-100
mtg combo budget 100 --min 20

# Specific colors
mtg combo budget 30 --colors "UR"
```

**Example:**

```bash
$ mtg combo budget 25

Found 47 combos under $25:

┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Combo                  ┃ Price  ┃ Colors┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ Pili-Pala + Grand Arc… │ $3.50  │ {G}{U}│
│ Famished Paladin + …   │ $2.25  │ {W}{G}│
│ Heliod + Walking Ball… │ $18.99 │ {W}   │
└────────────────────────┴────────┴───────┘
```

### `mtg combo create`

Generate custom combo suggestions between cards.

```bash
# Two cards
mtg combo create "Isochron Scepter" "Counterspell"

# Multiple cards
mtg combo create "Aetherflux Reservoir" "Bolas's Citadel" "Sensei's Divining Top"
```

Uses AI to analyze synergies and suggest interactions.

---

## Deck Commands

Build, validate, analyze, and optimize decks.

### `mtg deck new`

Create a new deck from scratch.

```bash
# Commander deck
mtg deck new commander --commander "Muldrotha, the Gravetide"

# Standard deck
mtg deck new standard --archetype aggro

# With theme
mtg deck new commander --commander "Atraxa" --theme "superfriends"

# With budget
mtg deck new commander --commander "Krenko" --budget 150
```

**Generates:**
- Commander + 99 cards (Commander format)
- 60-card deck (Standard/Modern)
- Mana base appropriate for colors
- Synergistic card choices
- Budget-conscious selections

**Output:**
- Saves to `<commander-name>_deck.json`
- Displays decklist in terminal
- Shows statistics (avg CMC, color distribution, etc.)

### `mtg deck build`

Build a deck from a decklist file.

```bash
# From .txt file
mtg deck build my_list.txt --format commander

# With theme guidance
mtg deck build my_list.txt --theme "aristocrats"

# With budget limit
mtg deck build my_list.txt --budget 200

# Specify output
mtg deck build my_list.txt --output my_deck.json
```

**Decklist formats supported:**
```
# Simple format (card names only)
Lightning Bolt
Counterspell
Island

# With quantities
4 Lightning Bolt
4 Counterspell
20 Island

# Arena format
4 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55

# MTGO format
4x Lightning Bolt
4x Counterspell
```

### `mtg deck validate`

Check deck legality and rules compliance.

```bash
# Basic validation
mtg deck validate my_deck.json

# Specific format
mtg deck validate my_deck.json --format commander

# Verbose output
mtg deck validate my_deck.json --verbose
```

**Checks:**
- ✅ Correct deck size (60/100 cards)
- ✅ Commander eligibility (legendary creature)
- ✅ Color identity compliance
- ✅ Card legality in format
- ✅ Singleton rules (Commander)
- ✅ Maximum copies (4x for non-Commander)
- ✅ Banned/restricted list

**Example:**

```bash
$ mtg deck validate goblins.json

Validating deck: Krenko Goblin Tribal

✅ Deck size: 100 cards
✅ Commander: Krenko, Mob Boss (legal)
✅ Color identity: {R} (all cards legal)
✅ Singleton rule: passed
✅ Format legality: Commander (legal)

⚠️  Warnings:
  • High average CMC (3.8) - consider more 1-2 drops
  • Low land count (32) - recommend 36-38 for this CMC

Deck is LEGAL for Commander format.
```

### `mtg deck analyze`

Get detailed statistics and insights.

```bash
# Basic analysis
mtg deck analyze my_deck.json

# Include price breakdown
mtg deck analyze my_deck.json --prices

# Detailed report
mtg deck analyze my_deck.json --detailed
```

**Analysis includes:**
- **Mana curve** - CMC distribution graph
- **Color distribution** - Mana symbol breakdown
- **Card types** - Creature/instant/sorcery/etc. percentages
- **Synergy score** - How well cards work together
- **Power level** - Casual/focused/optimized/cEDH
- **Price breakdown** - Total cost and expensive cards
- **Weaknesses** - Potential issues (low removal, no board wipes, etc.)

**Example:**

```bash
$ mtg deck analyze muldrotha.json

╭──────────────── Deck Analysis ────────────────╮
│                                                │
│  Deck: Muldrotha Graveyard Value              │
│  Commander: Muldrotha, the Gravetide          │
│  Format: Commander                             │
│                                                │
│  📊 Statistics:                                │
│  • Cards: 100                                  │
│  • Avg CMC: 3.2                               │
│  • Total Price: $428.50                       │
│  • Power Level: Optimized (7/10)              │
│                                                │
│  🎨 Color Distribution:                        │
│  • Green: 35% ███████                         │
│  • Blue: 32% ██████                           │
│  • Black: 28% █████                           │
│  • Colorless: 5% █                            │
│                                                │
│  📈 Mana Curve:                                │
│  CMC 0-1: ████ (8 cards)                      │
│  CMC 2:   ████████████ (18 cards)             │
│  CMC 3:   ████████████████ (24 cards)         │
│  CMC 4:   ████████████ (18 cards)             │
│  CMC 5:   ████████ (12 cards)                 │
│  CMC 6+:  ████████ (12 cards)                 │
│  Lands:   ████████████████ (38 cards)         │
│                                                │
│  🎯 Synergy Score: 8.5/10                      │
│  Strong graveyard synergies, consistent       │
│  recursion engine, excellent value plays.     │
│                                                │
│  ⚠️  Recommendations:                          │
│  • Add more board wipes (3 → 5-6)            │
│  • Consider Cyclonic Rift for protection     │
│  • More instant-speed interaction            │
│                                                │
╰────────────────────────────────────────────────╯
```

### `mtg deck suggest`

Get AI-powered improvement suggestions.

```bash
# Basic suggestions
mtg deck suggest my_deck.json

# With constraints
mtg deck suggest my_deck.json --budget 100 --theme "combo"

# Specific focus
mtg deck suggest my_deck.json --combo-mode focused
mtg deck suggest my_deck.json --archetype control

# Number of suggestions
mtg deck suggest my_deck.json --count 20
```

**Suggestion modes:**

- **`--combo-mode none`** - No combo focus (battlecruiser)
- **`--combo-mode backup`** - Combo as plan B (default)
- **`--combo-mode focused`** - Combo as primary strategy

**Returns:**
- Suggested additions (with reasoning)
- Suggested removals (what to cut)
- Upgrade paths (budget → optimized)
- Combo packages (if combo-mode enabled)

**Example:**

```bash
$ mtg deck suggest krenko.json --budget 50

Suggestions for: Krenko Goblin Tribal

📈 Additions (within $50 budget):

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Card                 ┃ Price ┃ Reason              ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Skirk Prospector     │ $0.50 │ Mana acceleration   │
│ Goblin Chieftain     │ $2.00 │ Haste enabler       │
│ Shared Animosity     │ $8.99 │ Win condition       │
│ Coat of Arms         │ $12.50│ Alt win condition   │
└──────────────────────┴───────┴─────────────────────┘

📉 Suggested Cuts:

• Goblin Shortcutter - Too slow, minimal impact
• Raging Goblin - Vanilla 1/1, better options exist
• Goblin Sky Raider - Flying rarely matters

Total upgrade cost: $23.99 (within budget ✅)
```

### `mtg deck export`

Export deck to various formats.

```bash
# Arena format
mtg deck export my_deck.json arena

# MTGO format
mtg deck export my_deck.json mtgo

# Text format
mtg deck export my_deck.json text

# Moxfield (for import)
mtg deck export my_deck.json moxfield

# Save to file
mtg deck export my_deck.json arena --output deck.txt
```

**Supported formats:**
- `arena` - MTG Arena import format
- `mtgo` - Magic Online format
- `text` - Simple text list
- `moxfield` - Moxfield.com import
- `json` - Raw JSON data

---

## Configuration Commands

Manage app settings and LLM providers.

### `mtg config show`

Display current configuration.

```bash
# Show all settings
mtg config show

# Show specific section
mtg config show llm
mtg config show cache
```

**Example:**

```bash
$ mtg config show

Current Configuration:

╭───────────── LLM Settings ──────────────╮
│                                          │
│  Provider: ollama                        │
│  Model: llama3                           │
│  Temperature: 0.7                        │
│  Max Tokens: 2048                        │
│                                          │
╰──────────────────────────────────────────╯

╭───────────── Cache Settings ────────────╮
│                                          │
│  Enabled: true                           │
│  TTL: 3600 seconds                       │
│  Max Size: 1000 entries                  │
│                                          │
╰──────────────────────────────────────────╯

╭───────────── Data Paths ────────────────╮
│                                          │
│  Cards DB: ~/.mtg/data/cards.db          │
│  Combos: ~/.mtg/data/combos.json         │
│  Chroma: ~/.mtg/data/chroma/             │
│                                          │
╰──────────────────────────────────────────╯
```

### `mtg config set`

Change configuration values.

```bash
# Set LLM provider
mtg config set llm.provider openai
mtg config set llm.model gpt-4

# Set API key (alternatively use environment variable)
mtg config set llm.openai.api_key "sk-..."

# Set temperature
mtg config set llm.temperature 0.8

# Set cache settings
mtg config set cache.enabled true
mtg config set cache.ttl 7200
```

**Common settings:**

| Setting | Options | Default |
|---------|---------|---------|
| `llm.provider` | ollama, openai, anthropic, gemini, groq | ollama |
| `llm.model` | (provider-specific) | llama3 |
| `llm.temperature` | 0.0 - 2.0 | 0.7 |
| `llm.max_tokens` | 100 - 8192 | 2048 |
| `cache.enabled` | true, false | true |
| `cache.ttl` | seconds | 3600 |

### `mtg config get`

Retrieve specific configuration value.

```bash
# Get single value
mtg config get llm.provider
# Output: ollama

# Get nested value
mtg config get llm.openai.api_key
# Output: sk-... (or ${OPENAI_API_KEY} if using env var)
```

### `mtg config reset`

Reset configuration to defaults.

```bash
# Reset everything
mtg config reset

# Reset specific section
mtg config reset llm
mtg config reset cache

# Reset with confirmation
mtg config reset --confirm
```

**Warning:** This will delete custom settings. Use `--confirm` to skip confirmation prompt.

### `mtg config providers`

List available LLM providers and their status.

```bash
mtg config providers
```

**Example:**

```bash
$ mtg config providers

Available LLM Providers:

┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider ┃ Status ┃ Installation         ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ ollama   │ ✅ Ready│ Built-in            │
│ openai   │ ⚠️ Not │ pip install [openai]│
│ anthropic│ ⚠️ Not │ pip install [anth…] │
│ gemini   │ ⚠️ Not │ pip install [gemini]│
│ groq     │ ⚠️ Not │ pip install [groq]  │
└──────────┴────────┴─────────────────────┘

Current: ollama (llama3)

To switch providers:
1. Install dependencies: pip install mtg-card-app[openai]
2. Set API key: export OPENAI_API_KEY="sk-..."
3. Switch provider: mtg config set llm.provider openai
```

---

## System Commands

Utility commands for setup and maintenance.

### `mtg stats`

Display system statistics and health.

```bash
mtg stats
```

**Shows:**
- Database statistics (card count, combo count)
- Cache statistics (hit rate, size)
- LLM provider status
- Performance metrics
- Disk usage

**Example:**

```bash
$ mtg stats

╭──────────────── System Statistics ────────────────╮
│                                                    │
│  📊 Database:                                      │
│  • Cards: 35,402                                   │
│  • Combos: 1,247                                   │
│  • Embeddings: 35,402                              │
│                                                    │
│  💾 Cache:                                         │
│  • Enabled: Yes                                    │
│  • Hit Rate: 78.3%                                 │
│  • Entries: 247 / 1000                             │
│  • Size: 12.4 MB                                   │
│                                                    │
│  🤖 LLM:                                           │
│  • Provider: ollama                                │
│  • Model: llama3                                   │
│  • Status: ✅ Connected                            │
│                                                    │
│  ⚡ Performance:                                   │
│  • Avg query time: 18ms                            │
│  • Deck suggestions: 18ms (cached)                 │
│  • Card lookups: <1ms                              │
│                                                    │
│  💿 Disk Usage:                                    │
│  • Database: 45.2 MB                               │
│  • Embeddings: 127.8 MB                            │
│  • Cache: 12.4 MB                                  │
│  • Total: 185.4 MB                                 │
│                                                    │
╰────────────────────────────────────────────────────╯
```

### `mtg setup`

Interactive setup wizard for first-time configuration.

```bash
mtg setup
```

**4-step process:**

1. **Welcome & Status** - Show current configuration
2. **LLM Provider** - Choose and configure provider
3. **Data Files** - Verify card database and embeddings
4. **Test Connection** - Validate configuration

**Features:**
- Provider comparison table
- API key configuration (env vars or direct)
- Data verification and download prompts
- Connection testing with sample query
- Helpful tips and troubleshooting

**Example flow:**

```bash
$ mtg setup

╭────────────────────────────────────────╮
│                                        │
│   🎴 MTG Card App Setup Wizard         │
│                                        │
│   Let's get you set up!                │
│                                        │
╰────────────────────────────────────────╯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1/4: Current Configuration

Current LLM Provider: ollama (llama3)
Status: ✅ Connected

Would you like to change your LLM provider? [y/N]: y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 2/4: LLM Provider Selection

Available providers:

┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Provider ┃ Cost   ┃ Speed    ┃ Quality   ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ Ollama   │ FREE   │ Fast     │ Good      │
│ Gemini   │ Low    │ Fast     │ Excellent │
│ Groq     │ Low    │ Fastest  │ Great     │
│ OpenAI   │ Medium │ Medium   │ Excellent │
│ Anthropic│ Medium │ Medium   │ Best      │
└──────────┴────────┴──────────┴───────────┘

Select provider [ollama]: gemini

Enter Gemini API key (or press Enter to use GEMINI_API_KEY env var):
[Hidden input]

✅ Gemini configured successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 3/4: Data Files

Checking data files...
✅ cards.db found (35,402 cards)
✅ combos.json found (1,247 combos)
✅ chroma/ found (35,402 embeddings)

All data files are present and up to date!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 4/4: Testing Configuration

Testing Gemini connection...
✅ Connection successful!

Testing query: "What are good commanders for beginners?"
✅ Query successful! (responded in 1.2s)

╭────────────────────────────────────────╮
│                                        │
│   ✅ Setup Complete!                   │
│                                        │
│   You're all set up and ready to go!  │
│                                        │
│   Try: mtg                            │
│                                        │
╰────────────────────────────────────────╯
```

### `mtg update`

Download and update card database.

```bash
# Update everything (cards + embeddings)
mtg update

# Force update (re-download even if up to date)
mtg update --force

# Update only cards (skip embeddings)
mtg update --cards-only

# Update only embeddings (skip download)
mtg update --embeddings-only
```

**Process:**
1. **Download** - Fetch latest Oracle cards from Scryfall (~40 MB)
2. **Import** - Parse JSON and insert into SQLite database
3. **Embeddings** - Generate vector embeddings for semantic search

**Progress bars show:**
- Download: MB transferred, speed, ETA
- Import: Percentage, card count (15,000 / 35,000)
- Embeddings: Percentage, batch progress (1-500 / 35,402)

**Example:**

```bash
$ mtg update

Updating MTG Card Database...

Downloading Oracle cards from Scryfall...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.2/40.2 MB • 5.2 MB/s • 0:00:00

Importing cards into database...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 35,402/35,402 cards

Generating embeddings...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • Batch 71/71

✅ Update complete!
   • Cards: 35,402 (↑ 42 new)
   • Embeddings: 35,402
   • Time: 8m 23s
```

**Frequency:**
- Run weekly for new set releases
- Run after major errata updates
- First-time setup runs automatically

---

## Advanced Usage

### Environment Variables

Override config file settings with environment variables:

```bash
# LLM provider settings
export MTG_LLM_PROVIDER=openai
export MTG_LLM_MODEL=gpt-4
export MTG_LLM_TEMPERATURE=0.8

# API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
export GROQ_API_KEY="gsk_..."

# Cache settings
export MTG_CACHE_ENABLED=true
export MTG_CACHE_TTL=7200

# Data paths
export MTG_DATA_DIR=~/.mtg/data
export MTG_CONFIG_PATH=~/.mtg/config.toml
```

Environment variables take precedence over config file.

### Custom Config File

Use a different config file:

```bash
mtg --config ~/my-config.toml stats
mtg --config /path/to/config.toml card "Lightning Bolt"
```

Useful for:
- Multiple configurations (testing vs production)
- Shared team configurations
- CI/CD pipelines

### Batch Operations

Use shell scripting for batch operations:

```bash
# Analyze multiple decks
for deck in decks/*.json; do
  echo "Analyzing $deck..."
  mtg deck analyze "$deck" --detailed > "analysis/$(basename $deck .json).txt"
done

# Export all decks to Arena format
for deck in decks/*.json; do
  mtg deck export "$deck" arena --output "arena/$(basename $deck .json).txt"
done

# Search and save results
mtg search "legendary dragons" --format json > dragons.json
```

### Piping and Output

Redirect output for further processing:

```bash
# Save card info as JSON
mtg card "Lightning Bolt" --format json > bolt.json

# Search and filter with jq
mtg search "legendary creatures" --format json | jq '.[] | select(.cmc <= 4)'

# Export deck and upload
mtg deck export my_deck.json arena | pbcopy  # macOS clipboard
```

### Scripting with Python

Import the library directly for advanced usage:

```python
from mtg_card_app.core.interactor import Interactor

# Initialize
interactor = Interactor()

# Use methods directly
card = interactor.get_card_details("Lightning Bolt")
combos = interactor.find_combos("Thassa's Oracle")
deck = interactor.build_deck(
    commander="Muldrotha",
    theme="graveyard",
    budget=200
)

# Validate and analyze
validation = interactor.validate_deck(deck)
analysis = interactor.analyze_deck(deck)
suggestions = interactor.suggest_deck_improvements(
    deck,
    budget=100,
    combo_mode="focused"
)
```

See `examples/` directory for more examples.

---

## Tips & Best Practices

### General Tips

1. **Use chat mode for exploration** - More intuitive than remembering commands
2. **Use direct commands for automation** - Better for scripts and workflows
3. **Set up your LLM provider first** - Run `mtg setup` on first use
4. **Update data regularly** - Run `mtg update` weekly for new cards
5. **Check stats periodically** - `mtg stats` shows system health

### Performance Tips

1. **Cache is your friend** - First query is slow, subsequent are fast
2. **Use `--format json` for parsing** - Easier to process programmatically
3. **Batch similar operations** - Group deck analyses together
4. **Clear cache if stale** - `rm -rf ~/.mtg/cache` if seeing old data

### Deck Building Tips

1. **Start with theme** - Use `--theme` flag for better suggestions
2. **Set budget constraints** - AI respects `--budget` limits
3. **Validate often** - Catch illegal cards early
4. **Analyze before finalizing** - Check mana curve and synergies
5. **Use suggest iteratively** - Apply suggestions, re-analyze, repeat

### Combo Discovery Tips

1. **Use `find` for exploration** - Semantic search finds creative combos
2. **Use `search` for specifics** - Faster for known combos
3. **Set budget constraints** - `combo budget` for budget builds
4. **Combine with deck builder** - Find combos, then build around them

### Configuration Tips

1. **Use environment variables for secrets** - Don't store API keys in config
2. **Start with Ollama** - Free and works offline
3. **Upgrade to cloud providers for better quality** - Gemini/Groq for speed, Claude for quality
4. **Adjust temperature for creativity** - 0.7 default, 0.3 for consistency, 1.0 for creativity

### Troubleshooting

**Problem: "Card not found"**
- Solution: Run `mtg update` to download card database

**Problem: "LLM provider not available"**
- Solution: Install dependencies: `pip install mtg-card-app[openai]`

**Problem: "Config error"**
- Solution: Delete config and re-run setup: `rm ~/.mtg/config.toml && mtg setup`

**Problem: "Slow performance"**
- Solution: First query builds cache (slow), subsequent are fast. If consistently slow, check `mtg stats` for cache hit rate.

**Problem: "API key error"**
- Solution: Set environment variable: `export OPENAI_API_KEY="sk-..."`

---

## Quick Reference

### Most Used Commands

```bash
mtg                              # Start chat (most common)
mtg card "Card Name"             # Quick card lookup
mtg combo find "Card"            # Find combos
mtg deck new commander --commander "X"  # New deck
mtg deck suggest deck.json       # Improve deck
mtg stats                        # Check system health
mtg setup                        # First-time setup
mtg update                       # Update card data
```

### Common Workflows

**Building a new deck:**
```bash
1. mtg deck new commander --commander "Muldrotha" --theme "graveyard" --budget 200
2. mtg deck validate muldrotha_deck.json
3. mtg deck analyze muldrotha_deck.json
4. mtg deck suggest muldrotha_deck.json --budget 50
5. mtg deck export muldrotha_deck.json moxfield
```

**Finding budget combos:**
```bash
1. mtg combo budget 50
2. mtg combo find "Card from results"
3. mtg deck new commander --commander "X" --theme "combo"
```

**Researching a card:**
```bash
1. mtg card "Card Name"
2. mtg combo find "Card Name"
3. mtg search "similar cards"
```

---

**Last Updated:** October 21, 2025  
**For full documentation, see:** [README.md](../README.md)  
**For quick start, see:** [CONTEXT_QUICKSTART.md](../CONTEXT_QUICKSTART.md)