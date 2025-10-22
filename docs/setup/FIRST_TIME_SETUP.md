# First-Time Setup Guide

**Get started with MTG Card App in 5-10 minutes**

---

## Overview

This guide will walk you through:
1. ✅ Installing the app
2. ✅ Choosing an LLM provider
3. ✅ Downloading card data
4. ✅ Testing your setup
5. ✅ Making your first query

**Time required:** 5-10 minutes (mostly downloading card data)

---

## Prerequisites

### System Requirements

- **Python**: 3.11+ (3.12 recommended)
- **OS**: macOS, Linux, or Windows
- **Disk space**: ~200 MB for data files
- **RAM**: 2 GB minimum (4 GB recommended)
- **Internet**: Required for initial setup and card updates

### Check Python Version

```bash
python --version
# Should show: Python 3.11.x or higher

# If not, install Python 3.12:
# macOS: brew install python@3.12
# Linux: apt install python3.12
# Windows: Download from python.org
```

---

## Step 1: Installation

### Option A: From Source (Development)

**Recommended if you want to contribute or modify the app.**

```bash
# Clone repository
git clone https://github.com/topherhaynie/mtg_card_app.git
cd mtg_card_app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
mtg --version
```

### Option B: pip install (Coming Soon)

**Simplest method for end users.**

```bash
# Once published to PyPI:
pip install mtg-card-app

# With all providers:
pip install mtg-card-app[all]

# With specific providers:
pip install mtg-card-app[openai]
pip install mtg-card-app[anthropic]
```

**Note:** Currently only available from source. PyPI package coming in Phase 6 Track 3.

---

## Step 2: Choose Your LLM Provider

The app supports **5 LLM providers**. Choose based on your needs:

### Quick Comparison

| Provider | Cost | Speed | Quality | Best For |
|----------|------|-------|---------|----------|
| **Ollama** | FREE ⭐ | Fast | Good | Learning, offline use |
| **Gemini** | Low ($) | Fast | Excellent | Budget-conscious users |
| **Groq** | Low ($) | Fastest | Great | Speed priority |
| **OpenAI** | Medium ($$) | Medium | Excellent | General use |
| **Anthropic** | Medium ($$) | Medium | Best | Highest quality |

### Recommended Starting Path

**For most users, we recommend:**

1. **Start with Ollama** (free, works offline)
2. **Test the app and learn features**
3. **Upgrade to Gemini or Groq** if you want better quality (still cheap)
4. **Consider OpenAI/Anthropic** for production use

### Provider Setup Instructions

#### Option 1: Ollama (FREE, Recommended for Beginners)

**Pros:** Free, private, works offline, no API keys  
**Cons:** Requires local installation, uses CPU/RAM

```bash
# Install Ollama (one-time)
# macOS/Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Windows:
# Download from https://ollama.ai/download

# Download model (one-time, ~4 GB)
ollama pull llama3

# Verify it works
ollama run llama3 "Hello!"
# Should respond with a greeting

# Configure app to use Ollama
mtg config set llm.provider ollama
mtg config set llm.model llama3
```

**Done!** Ollama is ready to use.

#### Option 2: Google Gemini (Low Cost, Fast)

**Pros:** Cheap ($0.50/1M tokens), fast, high quality  
**Cons:** Requires Google account, API key, internet

```bash
# 1. Get API key (free tier available)
# Visit: https://makersuite.google.com/app/apikey
# Click "Create API Key"
# Copy the key (starts with "AI...")

# 2. Install Gemini support
pip install mtg-card-app[gemini]

# 3. Set API key (environment variable recommended)
export GEMINI_API_KEY="AIza..."  # Add to ~/.zshrc to persist

# 4. Configure app
mtg config set llm.provider gemini
mtg config set llm.model gemini-1.5-flash

# 5. Test connection
mtg stats  # Should show "✅ Connected"
```

#### Option 3: Groq (Low Cost, Fastest)

**Pros:** Extremely fast (~500 tokens/sec), cheap, good quality  
**Cons:** Requires API key, rate limits on free tier

```bash
# 1. Get API key
# Visit: https://console.groq.com/
# Sign up (free)
# Create API key
# Copy the key (starts with "gsk_...")

# 2. Install Groq support
pip install mtg-card-app[groq]

# 3. Set API key
export GROQ_API_KEY="gsk_..."  # Add to ~/.zshrc to persist

# 4. Configure app
mtg config set llm.provider groq
mtg config set llm.model llama3-70b-8192

# 5. Test connection
mtg stats
```

#### Option 4: OpenAI (Medium Cost, Excellent Quality)

**Pros:** Reliable, excellent quality, large context  
**Cons:** More expensive ($0.50-$15/1M tokens depending on model)

```bash
# 1. Get API key
# Visit: https://platform.openai.com/api-keys
# Sign up (requires payment method)
# Create API key
# Copy the key (starts with "sk-...")

# 2. Install OpenAI support
pip install mtg-card-app[openai]

# 3. Set API key
export OPENAI_API_KEY="sk-..."  # Add to ~/.zshrc to persist

# 4. Configure app
mtg config set llm.provider openai
mtg config set llm.model gpt-4o-mini  # Cheaper option
# or: mtg config set llm.model gpt-4o  # Better quality

# 5. Test connection
mtg stats
```

#### Option 5: Anthropic Claude (Medium Cost, Best Quality)

**Pros:** Best reasoning, excellent for complex queries  
**Cons:** Most expensive, requires API key

```bash
# 1. Get API key
# Visit: https://console.anthropic.com/
# Sign up (requires payment method)
# Create API key
# Copy the key (starts with "sk-ant-...")

# 2. Install Anthropic support
pip install mtg-card-app[anthropic]

# 3. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."  # Add to ~/.zshrc to persist

# 4. Configure app
mtg config set llm.provider anthropic
mtg config set llm.model claude-3-5-sonnet-20241022

# 5. Test connection
mtg stats
```

### Cost Estimates

**For typical usage (~100 queries/day):**

- **Ollama**: FREE
- **Gemini**: ~$0.05/month
- **Groq**: ~$0.10/month
- **OpenAI (GPT-4o-mini)**: ~$2/month
- **OpenAI (GPT-4o)**: ~$15/month
- **Anthropic (Claude 3.5 Sonnet)**: ~$20/month

**Note:** Actual costs vary based on query length and frequency.

---

## Step 3: Download Card Data

The app needs Magic card data to function. This is a **one-time download** of ~40 MB.

### Automatic Setup (Recommended)

```bash
# Run the setup wizard
mtg setup
```

The wizard will:
1. Show your current configuration
2. Let you choose/configure LLM provider
3. **Automatically download card data if missing**
4. Generate embeddings for semantic search (~8 minutes)
5. Test your configuration

### Manual Download

If you prefer manual control:

```bash
# Download and import cards
mtg update

# This will:
# 1. Download Oracle cards from Scryfall (~40 MB, ~2 min)
# 2. Import into SQLite database (~1 min)
# 3. Generate embeddings (~8 min)
# Total time: ~10 minutes
```

**Progress bars show:**
- Download progress (MB, speed, ETA)
- Import progress (% complete, card count)
- Embedding progress (% complete, batches)

### Verify Data Downloaded

```bash
mtg stats
```

Should show:
```
📊 Database:
  • Cards: 35,402 ✅
  • Combos: 1,247 ✅
  • Embeddings: 35,402 ✅
```

---

## Step 4: Test Your Setup

### Quick Test

```bash
# Check system status
mtg stats

# Should show:
# ✅ Cards: 35,402
# ✅ LLM: Connected
# ✅ Cache: Enabled
```

### Try a Simple Query

```bash
# Get info about a card
mtg card "Lightning Bolt"

# Should display card details in a nice panel
```

### Try Chat Mode

```bash
# Start interactive chat
mtg

# Then type:
# You: What are the best burn spells?
# Assistant: [Lists Lightning Bolt, Lava Spike, etc.]

# Exit with Ctrl+D or /exit
```

### Try a Combo Search

```bash
# Find combos with a card
mtg combo find "Thassa's Oracle"

# Should show Thoracle + Consultation, Thoracle + Tainted Pact, etc.
```

### Try Building a Deck

```bash
# Build a budget commander deck
mtg deck new commander --commander "Krenko, Mob Boss" --budget 100

# Should generate a 100-card deck and save to krenko_mob_boss_deck.json
```

---

## Step 5: Your First Real Query

Now that everything is set up, let's do something useful!

### Example: Build a Budget Deck

```bash
# 1. Start by exploring a theme
mtg

You: I want to build a graveyard deck in Golgari colors under $150. What commander should I use?Assistant: For a budget Golgari graveyard deck, I'd recommend:
  • Meren of Clan Nel Toth (~$3) - Excellent recursion
  • Golgari Grave-Troll - Enables dredge strategy
  • Jarad, Golgari Lich Lord - Sacrifice outlet + win con

You: Build me a Meren deck under $150

# 2. Exit chat and use direct command
/exit

# 3. Generate the deck
mtg deck new commander --commander "Meren of Clan Nel Toth" --budget 150 --theme "graveyard"

# 4. Analyze it
mtg deck analyze meren_of_clan_nel_toth_deck.json

# 5. Get suggestions for improvements
mtg deck suggest meren_of_clan_nel_toth_deck.json --budget 25

# 6. Export to Moxfield
mtg deck export meren_of_clan_nel_toth_deck.json moxfield
```

---

## Next Steps

### Learn the Commands

Check out the full command reference:

```bash
# Quick reference
mtg --help

# Detailed guide
# Read: docs/CLI_GUIDE.md
```

### Explore Features

Try these workflows:

1. **Combo Discovery**
   ```bash
   mtg combo budget 50
   mtg combo find "infinite mana"
   ```

2. **Card Research**
   ```bash
   mtg search "legendary dragons"
   mtg card "Tiamat"
   ```

3. **Deck Optimization**
   ```bash
   mtg deck validate your_deck.json
   mtg deck analyze your_deck.json --detailed
   mtg deck suggest your_deck.json --budget 100
   ```

### Join the Community

- **Report bugs**: [GitHub Issues](https://github.com/topherhaynie/mtg_card_app/issues)
- **Feature requests**: [GitHub Discussions](https://github.com/topherhaynie/mtg_card_app/discussions)
- **Contribute**: See [CONTRIBUTING.md](../../CONTRIBUTING.md) (coming soon)

### Keep Data Updated

Run weekly to get new cards:

```bash
mtg update
```

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'mtg_card_app'"

**Cause:** App not installed properly  
**Solution:**
```bash
pip install -e .  # From project root
```

#### "Card database is empty"

**Cause:** Data not downloaded  
**Solution:**
```bash
mtg update
```

#### "LLM provider not available"

**Cause:** Provider dependencies not installed  
**Solution:**
```bash
# Install for your chosen provider
pip install mtg-card-app[openai]
pip install mtg-card-app[anthropic]
pip install mtg-card-app[gemini]
pip install mtg-card-app[groq]

# Or install all
pip install mtg-card-app[all]
```

#### "API key error"

**Cause:** API key not set  
**Solution:**
```bash
# Set as environment variable (recommended)
export OPENAI_API_KEY="sk-..."  # Add to ~/.zshrc

# Or set in config
mtg config set llm.openai.api_key "sk-..."
```

#### "Ollama model not found"

**Cause:** Model not downloaded  
**Solution:**
```bash
ollama pull llama3
```

#### "Slow performance"

**Cause:** First query builds cache (normal)  
**Solution:** Subsequent queries will be fast. Check cache hit rate:
```bash
mtg stats  # Look for cache hit rate ~70-80%
```

### Getting Help

1. **Check stats:** `mtg stats` shows system health
2. **Run setup:** `mtg setup` reconfigures everything
3. **Read docs:** `docs/CLI_GUIDE.md` has detailed examples
4. **Check logs:** `~/.mtg/logs/` (if enabled)
5. **Ask in chat:** Use `mtg` and ask questions about the app itself!

---

## Configuration Reference

### Config File Location

```bash
~/.mtg/config.toml
```

### Example Config

```toml
[llm]
provider = "ollama"
model = "llama3"
temperature = 0.7
max_tokens = 2048

[llm.ollama]
base_url = "http://localhost:11434"

[llm.openai]
api_key = "${OPENAI_API_KEY}"  # Use environment variable

[cache]
enabled = true
ttl = 3600
max_size = 1000

[data]
cards_db = "~/.mtg/data/cards.db"
combos_json = "~/.mtg/data/combos.json"
chroma_dir = "~/.mtg/data/chroma"
```

### Environment Variables

```bash
# Provider settings
export MTG_LLM_PROVIDER=openai
export MTG_LLM_MODEL=gpt-4o-mini

# API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
export GROQ_API_KEY="gsk_..."

# Paths
export MTG_CONFIG_PATH=~/.mtg/config.toml
export MTG_DATA_DIR=~/.mtg/data
```

---

## Summary Checklist

Use this to verify your setup:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] App installed (`mtg --version` works)
- [ ] LLM provider chosen and configured
- [ ] API key set (if not using Ollama)
- [ ] Card data downloaded (`mtg stats` shows 35,402 cards)
- [ ] Embeddings generated (`mtg stats` shows 35,402 embeddings)
- [ ] Test query successful (`mtg card "Lightning Bolt"`)
- [ ] Chat mode working (`mtg` then ask a question)

**All checked?** You're ready to go! 🎉

---

## What's Next?

### Learn Advanced Features

- **Combo discovery** - Find infinite combos and synergies
- **Deck building** - AI-powered deck construction
- **Deck optimization** - Improve existing decklists
- **Format validation** - Check legality across all formats

### Explore Examples

Check out `examples/` directory for Python scripting examples:

```bash
cd examples/
python usage_example.py
python combo_demo.py
python deck_builder_demo.py
```

### Read Full Documentation

- **README.md** - Project overview and features
- **docs/CLI_GUIDE.md** - Complete command reference
- **CONTEXT_QUICKSTART.md** - Quick reference for new sessions
- **docs/architecture/** - System design documentation

---

**Congratulations!** You're now set up and ready to build amazing Magic decks! 🎴✨

**Quick Start Command:** `mtg`

**For help:** `mtg --help` or just ask questions in chat mode!

---

**Last Updated:** October 21, 2025  
**Version:** Phase 6 Tracks 1 & 2 Complete
