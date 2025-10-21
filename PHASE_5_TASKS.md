# Phase 5: Deck Builder – Prioritized Development Tasks

## Priority 1: Foundation
- [x] Define `Deck` entity (format, cards, sections, metadata)
- [x] Serialization/deserialization for decks
- [x] Implement `DeckBuilderManager` with basic deck construction and validation (format rules, size)
  - [ ] Singleton/banned lists (format-specific) – deferred

## Priority 2: Core Features
- [x] Add basic mana curve/type/color analysis to `DeckBuilderManager`
- [x] Implement initial card suggestion logic (RAG-backed)
- [ ] Enhance suggestions with constraints (theme, budget, power level); add filters
- [ ] Synergy analysis and weakness detection
- [ ] Integrate combo detection and suggestions

## Priority 3: Integration
- [x] Extend `Interactor` with deck-related methods:
  - [x] `build_deck(format, card_pool, commander, constraints, metadata)`
  - [x] `suggest_cards(deck, constraints)`
  - [x] `analyze_deck(deck)`
  - [ ] `export_deck(deck, format)`
- [x] Register MCP tools and define schemas:
  - [x] `build_deck` (params + outputSchema)
  - [x] `validate_deck` (params + outputSchema)
  - [x] `analyze_deck` (params + outputSchema)
  - [x] `suggest_cards` (params + outputSchema)
  - [x] Initialize advertises descriptions/examples for deck tools

## Priority 4: User Interface
- [ ] Add CLI commands for deck building and analysis
- (Optional) Prepare for future TUI/Web integration

## Priority 5: Testing & Documentation
- [x] Unit tests for DeckBuilderManager and Interactor deck methods
- [x] E2E MCP tests for deck build/validate
- [x] JSON-RPC tests for deck analyze/suggest tools
- [ ] Sample deck validation for each format
- [x] Update architecture docs and roadmap
- [ ] Write user/developer guide for deck builder features

---

Next up (short list):
- Enhance suggestion logic with theme/budget/power constraints and RAG filters
- Add synergy/weakness analysis heuristics; format rule checks (singleton, banned, color identity)
- Wire CLI commands for build/validate/analyze/suggest

---

Tasks are ordered for efficient development: start with the data model and manager, then core features, integration, UI, and finally testing/documentation. This ensures a solid foundation and rapid iteration on user-facing features.
