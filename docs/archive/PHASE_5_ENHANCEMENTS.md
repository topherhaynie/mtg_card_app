# Phase 5: Deck Builder Enhancements

**Date:** October 21, 2025  
**Status:** ✅ Complete

## Overview

Enhanced the deck builder suggestion system with robust combo detection, advanced ranking, and flexible user controls via MCP/CLI.

---

## Implemented Features

### 1. Advanced Ranking Factors

The combo ranking system now considers **10 weighted factors**:

1. **Archetype Fit** (+10 points): Matches deck theme/tags
2. **Commander Synergy** (+15 points): Combo includes the commander
3. **Color Identity Overlap** (+5 points per matching color): Fits deck colors
4. **Budget Fit** (+10 points if under budget, penalty if over)
5. **Power Level Fit** (+8 points if combo power matches deck power level)
6. **Complexity** (+5 for low, -3 for high): Simpler combos are preferred
7. **Ease of Assembly** (+8 for 2-card, +4 for 3-card, penalty for 4+)
8. **Disruptibility Penalty** (-2 per documented weakness)
9. **Infinite Combo Boost** (+12 points for infinite combos)
10. **Popularity Boost** (+5 * popularity_score)

### 2. Flexible User Controls

New constraint options for `suggest_cards`:

```python
constraints = {
    # Existing
    "theme": "control",
    "budget": 200.0,
    "power": 7,  # 1-10 scale
    "banned": ["Card Name"],
    "n_results": 10,
    
    # New combo controls
    "combo_mode": "focused",  # or "broad"
    "combo_limit": 3,  # max combos per suggestion
    "combo_types": ["infinite_mana", "engine"],  # filter by type
    "exclude_cards": ["Unwanted Card"],  # exclude from combos
    "sort_by": "power",  # or "price", "popularity", "complexity"
    "explain_combos": True,  # LLM-powered explanations
}
```

### 3. Combo Type Filtering

Users can specify which combo types to include:
- `infinite_mana`
- `infinite_draw`
- `infinite_damage`
- `infinite_life`
- `infinite_tokens`
- `infinite_mill`
- `lock`
- `one_shot`
- `engine`
- `synergy`
- `other`

### 4. Sorting Options

Four sorting modes for combo results:
- **power** (default): By calculated ranking score
- **price**: Cheapest combos first
- **popularity**: Most popular combos first
- **complexity**: Simplest combos first

### 5. LLM-Powered Explanations

When `explain_combos: True`, each combo receives an LLM-generated explanation covering:
- How it synergizes with the deck
- What makes it powerful or fun
- When to use it in gameplay

### 6. Exclusion Lists

Users can exclude specific cards from combo searches, useful for:
- Avoiding banned cards in specific playgroups
- Filtering out disliked or overused cards
- Testing deck variants

### 7. Exhaustive Combo Detection

The system now checks:
- Suggested card + every deck card
- Suggested card + commander
- Suggested card + other suggestions
- Applies all filters (theme, format, colors, budget, legality, types)

---

## Technical Details

### Combo Search Query

```python
combo_query = {
    "card_ids": [card1_id, card2_id],
    "tags": [theme],  # if specified
    "legal_formats": [deck.format],  # if specified
    "max_price": budget,  # if specified
    "colors": deck_colors,  # if specified
    "combo_types": combo_types_filter,  # if specified
}
```

### Output Format

Each suggestion now includes:

```json
{
    "name": "Sol Ring",
    "score": 0.99,
    "synergy": 1,
    "weaknesses": ["May not fit theme"],
    "reason": "Matches theme 'control'",
    "combos": [
        {
            "id": "...",
            "name": "Infinite Mana",
            "card_names": ["Sol Ring", "..."],
            "combo_types": ["infinite_mana"],
            "total_price_usd": 5.0,
            "complexity": "low",
            "popularity_score": 0.9,
            "llm_explanation": "This combo works by..."  // if explain_combos=true
        }
    ]
}
```

---

## Usage Examples

### Example 1: Focused, Budget-Friendly Combos

```python
suggestions = manager.suggest_cards(deck, {
    "theme": "control",
    "budget": 50.0,
    "combo_mode": "focused",
    "combo_limit": 3,
    "sort_by": "price"
})
```

### Example 2: All Infinite Combos with Explanations

```python
suggestions = manager.suggest_cards(deck, {
    "combo_mode": "broad",
    "combo_types": ["infinite_mana", "infinite_damage"],
    "explain_combos": True,
    "sort_by": "power"
})
```

### Example 3: Exclude Overused Cards

```python
suggestions = manager.suggest_cards(deck, {
    "exclude_cards": ["Thassa's Oracle", "Demonic Consultation"],
    "combo_mode": "focused"
})
```

---

## Performance Considerations

- **Combo search complexity**: O(n * m) where n = suggested cards, m = deck cards
- **Optimization opportunities**:
  - Cache combo search results per deck
  - Limit exhaustive checks to top-N suggestions (configurable)
  - Batch combo queries if database supports it
  - Precompute popular combos for common formats

---

## Future Enhancements

- **ML-powered impact prediction**: Train model on win rates and user feedback
- **Async combo lookups**: Parallelize searches for better performance
- **Combo assembly difficulty**: Calculate based on mana requirements and board state
- **Format-specific penalties**: Adjust for disruptibility in specific metas
- **User feedback loop**: Learn from accepted/rejected suggestions

---

## Testing

Unit test coverage:
- ✅ Combo detection with mocked services
- ✅ Constraint parsing and filtering
- ✅ Exclusion list handling
- ✅ Budget and theme matching

End-to-end test coverage:
- ⏳ MCP integration (pending)
- ⏳ CLI integration (pending)
- ⏳ LLM explanation generation (pending)

---

## Documentation Updates Needed

- [ ] Update MCP schema for new constraint options
- [ ] Update CLI help text for new flags
- [ ] Add examples to README
- [ ] Document combo ranking algorithm
- [ ] Add performance tuning guide

---

**Status:** Core features implemented and tested. Ready for integration with MCP/CLI.
