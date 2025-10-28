# Chat Interface Improvement Plan

**Date**: October 28, 2025  
**Issue**: Chat responses are disconnected, hallucinating cards, and not showing card details to users

## Problems Identified

### 1. **LLM Hallucination** ❌
- **Observed**: LLM inventing fake cards ("Nearby Planet", "Chocobo Racetrack")
- **Root Cause**: LLM generating free-form text without being forced to use only provided cards
- **Impact**: Users can't trust the responses, combos are nonsensical

### 2. **No Card Text Display** ❌
- **Observed**: Users can't see oracle text, mana costs, or verify cards exist
- **Root Cause**: Chat only shows LLM's prose response, not structured card data
- **Impact**: Users can't validate suggestions or learn what cards actually do

### 3. **Context Loss** ❌
- **Observed**: Later messages don't remember earlier conversation
- **Root Cause**: No conversation history being passed to LLM
- **Impact**: Feels disconnected, can't build on previous answers

### 4. **RAG Not Used Effectively** ⚠️
- **Observed**: RAG finds relevant cards but LLM ignores them
- **Root Cause**: Prompt doesn't enforce using ONLY the provided cards
- **Impact**: RAG system becomes pointless decoration

### 5. **No Combo Validation** ❌
- **Observed**: Nonsensical combo suggestions that don't work mechanically
- **Root Cause**: No validation that cards interact as described
- **Impact**: Misleading advice, wastes users' time

## Current Flow

```
User Query
    ↓
RAG Search (finds 5 relevant cards)
    ↓
Fetch Full Card Details (name, type, cmc, colors, text, score)
    ↓
Pass to LLM with loose prompt
    ↓
LLM generates free-form response (ignoring provided cards)
    ↓
Display only LLM text
```

## Proposed Improvements

### Phase 1: Show Card Details (Quick Win)

**Goal**: Display actual card information alongside LLM response

**Changes**:
1. **Format Card Display**: Show cards in rich panels with:
   ```
   ╭─────────────────────────────────────╮
   │ Lightning Bolt                      │
   │ Instant - {R}                       │
   │ CMC: 1                              │
   ├─────────────────────────────────────┤
   │ Lightning Bolt deals 3 damage to   │
   │ any target.                         │
   │                                     │
   │ Relevance: 0.95                     │
   ╰─────────────────────────────────────╯
   ```

2. **Show Before Response**: Display cards FIRST, then LLM commentary

3. **Add Card References**: Let LLM reference cards by number [1], [2], etc.

**Benefits**:
- Users can verify cards exist
- Learn actual oracle text
- Validate LLM suggestions
- Build trust in the system

### Phase 2: Constrain LLM (Medium Priority)

**Goal**: Force LLM to only use provided cards

**Changes**:
1. **Stricter Prompt**:
   ```
   You are a Magic: The Gathering expert. Answer using ONLY the cards provided below.
   
   DO NOT invent or mention cards not in this list.
   DO NOT make up abilities or card names.
   Reference cards by their [number] in the list.
   
   Available cards:
   [1] Lightning Bolt - {R} - Instant
       "Lightning Bolt deals 3 damage to any target."
   [2] Counterspell - {U}{U} - Instant
       "Counter target spell."
   ...
   
   User question: "{query}"
   
   Respond using ONLY the cards listed above.
   ```

2. **Post-Process Validation**: Check if LLM mentioned cards not in the provided list

3. **Retry on Hallucination**: If fake cards detected, regenerate with stricter prompt

**Benefits**:
- No more invented cards
- Responses grounded in actual data
- RAG system becomes meaningful

### Phase 3: Add Conversation Memory (Medium Priority)

**Goal**: Maintain context across messages

**Changes**:
1. **Store Conversation History**:
   ```python
   conversation_history = [
       {"role": "user", "content": "What combos use Thassa's Oracle?"},
       {"role": "assistant", "content": "[Response with cards]"},
       {"role": "user", "content": "How do I protect that combo?"},
   ]
   ```

2. **Include in Prompt**: Pass last 5 messages to LLM for context

3. **Show History Command**: `/history` to review conversation

**Benefits**:
- Build on previous answers
- Natural conversation flow
- Follow-up questions work

### Phase 4: Combo Validation (Advanced)

**Goal**: Verify combos actually work

**Changes**:
1. **Rules Engine**: Basic check if cards can interact:
   - Mana costs compatible?
   - Colors align?
   - Timing makes sense?

2. **Combo Database**: Pre-validated known combos

3. **Confidence Scoring**: Rate how likely combo actually works

**Benefits**:
- Fewer bad suggestions
- Educational for users
- Builds expertise

## Implementation Priority

### Immediate (This Session)
1. ✅ **Display Card Details** (1-2 hours) - COMPLETE
   - Show cards in panels before LLM response
   - Include oracle text, mana cost, type
   - Add relevance scores

2. ✅ **Constrain LLM Prompt** (30 minutes) - COMPLETE
   - Rewrite prompt to enforce "ONLY these cards"
   - Add numbered card references
   - Warn against hallucination

### Short-term (Next Session)
3. ✅ **Conversation Memory** (2-3 hours) - COMPLETE
   - Store history in session
   - Pass to LLM with each query
   - Add `/history` and `/clear` commands

4. **Card Verification** (1 hour) - PENDING
   - Post-process check for fake cards
   - Regenerate if hallucination detected

### Medium-term (Phase 7)
5. **Combo Validation** (4-6 hours)
   - Basic rules checking
   - Known combo database
   - Confidence scoring

6. **Enhanced Display** (2-3 hours)
   - Card images (Scryfall)
   - Color-coded mana symbols
   - Price information
   - Legality indicators

## Example: Improved Response Format

**Before** (Current):
```
Response:
I think I can help you with that!

For a unique combo using a set-specific land like Snow-Capped Mountains,
I'd recommend combining Nearby Planet with Mountain Valley...
[All hallucinated nonsense]
```

**After** (Improved):
```
╭─────────────── Found Cards ───────────────╮
│                                           │
│ [1] Mountain Valley                       │
│     Land                                  │
│     Mountain Valley enters tapped.        │
│     {T}, Sacrifice Mountain Valley:       │
│     Search your library for a Mountain    │
│     or Forest card...                     │
│     Relevance: 0.89                       │
│                                           │
│ [2] Snow-Covered Mountain                 │
│     Basic Snow Land - Mountain            │
│     ({T}: Add {R})                        │
│     Relevance: 0.76                       │
│                                           │
╰───────────────────────────────────────────╯

Response:
Based on the cards found, here's a combo suggestion:

[1] Mountain Valley is a fetch land that can search for
Mountains or Forests. Combined with snow lands like [2]
Snow-Covered Mountain, you can build a snow-matters deck.

Some cards that work well with snow lands:
- Skred (removal that scales with snow permanents)
- Scrying Sheets (card advantage with snow mana)
- Frost Titan (powerful creature in snow decks)

Would you like me to search for specific snow-synergy cards?
```

## Technical Changes Needed

### Files to Modify

1. **`mtg_card_app/ui/cli/chat.py`**
   - Add `_display_cards()` function
   - Modify `_handle_query()` to show cards first
   - Add card panels before response

2. **`mtg_card_app/core/interactor.py`**
   - Rewrite `answer_natural_language_query()` prompt
   - Add conversation history parameter
   - Add post-processing validation

3. **New: `mtg_card_app/ui/cli/card_display.py`**
   - Rich formatting for cards
   - Panel layouts
   - Mana symbol rendering

4. **New: `mtg_card_app/core/conversation.py`** (Phase 3)
   - Conversation history management
   - Context window sliding
   - Memory cleanup

## Success Metrics

- **Hallucination Rate**: 0% (no fake cards)
- **User Trust**: Cards are verifiable
- **Context Retention**: Follow-up questions work
- **Combo Accuracy**: Basic validation passes

## Next Steps

1. Implement card display panels
2. Rewrite LLM prompt to constrain output
3. Test with same queries from session
4. Iterate based on results

Would you like me to start with Phase 1 (card display) now?
