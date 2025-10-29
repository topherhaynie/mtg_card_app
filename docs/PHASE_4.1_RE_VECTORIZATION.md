# Phase 4.1: Re-Vectorization with Enriched Text

**Date**: October 28, 2025  
**Status**: In Progress  
**Goal**: Improve semantic search by enriching card embeddings with contextual metadata

## Problem Identified

During hybrid scoring implementation testing, we discovered that **Dramatic Reversal** (a famous combo piece with Isochron Scepter) was not findable through semantic search, even with targeted queries:

### Failed Queries:
- `"untap all permanents"` → Dramatic Reversal NOT in top 10
- `"untap all nonland permanents"` → Dramatic Reversal NOT in top 10 (EXACT Oracle text!)
- `"instant untap permanents"` → Dramatic Reversal NOT in top 10
- `"Untap permanents"` → Dramatic Reversal NOT in top 10

### Root Cause:
Dramatic Reversal's Oracle text is extremely short: `"Untap all nonland permanents you control."`

When embedded as-is, this 41-character text doesn't provide enough semantic context for the embedding model to capture:
1. That it's an **instant spell** (important for combo context)
2. That it's a **mass untap effect** (not single-target)
3. Its **mana value** (CMC 2 = cheap enough for many combos)
4. Its **mechanical category** (untap effects are combo-relevant)

## Solution: Enriched Card Text

Instead of embedding just the Oracle text, we now embed an **enriched representation** that includes:

### Before (Original):
```
Name: Dramatic Reversal | Type: Instant | Text: Untap all nonland permanents you control. | Colors: U
```
**Length**: 97 characters

### After (Enriched):
```
Name: Dramatic Reversal | Type: Instant | Card types: instant spell | Text: Untap all nonland permanents you control. | Mechanics: mass untap effect | Colors: U | Mana value: 2
```
**Length**: 176 characters (+81% more context)

## Enrichment Categories

### 1. Card Type Expansion
Extracts card types from type line and adds semantic labels:
- "Instant" → "instant spell"
- "Creature" → "creature permanent"
- "Artifact" → "artifact permanent"
- etc.

**Why**: Helps queries like "instant untap" match instant cards specifically

### 2. Mechanic Detection
Analyzes Oracle text to identify common mechanics:
- "untap all/each" → "mass untap effect"
- "untap target" → "untap effect"
- "draw...card" → "card draw"
- "copy" → "copy effect"
- "enters the battlefield" → "enters the battlefield trigger"
- "counter target" → "counterspell"
- "destroy" → "removal"
- "search your library" → "tutor effect"
- etc.

**Why**: Adds mechanical categories that connect cards by function, not just text similarity

### 3. Mana Value
Explicitly includes CMC: "Mana value: 2"

**Why**: Helps queries like "cheap instant" or "mana value 2" find appropriate cards

## Implementation Changes

### File: `mtg_card_app/managers/rag/manager.py`

**Method**: `_build_card_text(card: Card)`

**Changes**:
1. Extract card types from type line
2. Detect mechanics from Oracle text
3. Add enriched metadata to embedding text
4. Increase text length for cards with short Oracle text

## Expected Impact

### Better Semantic Matching:
- **"instant untap"** should now match Dramatic Reversal (has "instant spell" + "mass untap effect")
- **"instant mana value 2"** should match it (has "instant spell" + "Mana value: 2")
- **"mass untap"** should match it (has "mass untap effect")

### Maintains Novel Discovery:
- Enrichment is purely additive - doesn't remove any original text
- Still uses LLM-generated queries for semantic search
- Novel combos still discoverable through mechanical analysis

### Improved Precision:
- Card type labels help distinguish instants from artifacts/creatures with similar effects
- Mechanic categories create semantic bridges between functionally similar cards

## Re-Vectorization Process

### Steps:
1. ✅ Update `_build_card_text()` with enrichment logic
2. ✅ Clear old vector database (`data/chroma/`)
3. ⏳ Run `scripts/vectorize_cards.py` to re-embed all 35,402 cards (~17 minutes)
4. ⏳ Test with Dramatic Reversal + Isochron Scepter query
5. ⏳ Validate that enrichment improves recall without harming precision

### Command:
```bash
# Clear old database
rm -rf data/chroma/96e4cd89-1829-4aad-bff7-3c287be14695
rm data/chroma/chroma.sqlite3

# Re-vectorize with enriched text
python scripts/vectorize_cards.py
```

## Testing Plan

### Test Case 1: Isochron Scepter → Dramatic Reversal
```python
# Should now find Dramatic Reversal in top 10
interactor.find_combo_pieces("Isochron Scepter", n_results=10)
```

**Expected**: Dramatic Reversal appears (enriched with "instant spell" + "mass untap effect")

### Test Case 2: Direct Query Test
```python
# Test if enriched queries work
queries = [
    "instant untap permanents",
    "instant mass untap",
    "instant untap mana value 2"
]
```

**Expected**: Dramatic Reversal in top 5 for at least 2/3 queries

### Test Case 3: Novel Discovery
```python
# Ensure we still find novel combos
interactor.find_combo_pieces("Entrancing Lyre", n_results=5)
```

**Expected**: Still finds creative combos, not degraded by enrichment

## Philosophical Alignment

This approach maintains our core philosophy:

✅ **Not a database lookup**: Enrichment adds semantic context, not combo lists  
✅ **Enables discovery**: Better embeddings = better semantic search = finding novel synergies  
✅ **LLM-powered**: Still uses LLM to generate targeted queries  
✅ **Honest about limitations**: Won't find EVERY famous combo, but improves success rate  

## Alternative Approaches Considered

### ❌ Hardcode Known Combos
Rejected - violates "no database lookup" philosophy

### ❌ Manual Query Expansion
Rejected - doesn't scale, requires manual tuning per card

### ✅ Enriched Embeddings
**Selected** - scales automatically, improves all cards, maintains discovery focus

## Next Steps After Re-Vectorization

1. **Test & Validate**: Verify Dramatic Reversal is now findable
2. **Commit Changes**: Document Phase 4.1 completion
3. **Update Documentation**: Add enrichment details to architecture docs
4. **Consider Priority 2**: If enrichment works well, move to Graph Database for usage-based learning

## Technical Notes

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Max Tokens**: 256 (enriched text well within limits)

### Vector Database
- **Storage**: ChromaDB
- **Location**: `data/chroma/`
- **Size**: ~77MB (before re-vectorization)
- **Total Cards**: 35,402

### Performance
- **Vectorization Speed**: ~35 cards/second
- **Total Time**: ~17 minutes for full re-vectorization
- **Search Latency**: <100ms (unchanged)

## Success Criteria

Phase 4.1 is successful if:
1. ✅ Dramatic Reversal findable via "instant untap" type queries
2. ✅ No degradation in novel combo discovery
3. ✅ Enrichment improves recall for cards with short Oracle text
4. ✅ System still honest about what it finds (no hallucination)

---

**Status**: Round 2 of re-vectorization in progress

## Round 1 Results (Disappointing)

After first re-vectorization with enriched text at the END:
- Query "instant untap permanents" → Dramatic Reversal NOT found
- Query "instant spell mass untap effect" (EXACT enrichment) → Dramatic Reversal NOT found
- Only findable when searching "Dramatic Reversal untap" (with name)

**Problem**: Enriched tags at the END get diluted by other text in the embedding.

## Round 2 Strategy: Mechanics-First Enrichment

### Key Change:
Put enriched mechanics and card types AT THE BEGINNING for maximum semantic weight.

### Before (Round 1):
```
Name: Dramatic Reversal | Type: Instant | Card types: instant spell | Text: Untap all nonland permanents you control. | Mechanics: mass untap effect | Colors: U | Mana value: 2
```

### After (Round 2):
```
instant instant spell mass untap untap all untap effect | Name: Dramatic Reversal | Type: Instant | Text: Untap all nonland permanents you control. | Colors: U | Mana value: 2
```

**Why This Works Better**:
- Embedding models weight EARLIER text more heavily
- Leading with "instant instant spell mass untap untap all untap effect" creates strong semantic match
- Redundancy ("instant" twice, "untap" three times) reinforces the signal
- Name and Oracle text still included for fallback matching

### Mechanic Repetition Strategy:
For "mass untap" effects, we now tag with:
- "mass untap" (category)
- "untap all" (specific pattern)
- "untap effect" (general category)

This creates multiple semantic hooks for queries like:
- "instant untap"
- "mass untap"
- "untap all"
- "instant spell untap"

---

**Status**: Awaiting Round 2 re-vectorization completion (ETA: ~15 minutes)
