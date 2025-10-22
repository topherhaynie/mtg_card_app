# Phase 5: Deck Builder – Architecture Integration Plan

## 1. Current Architecture Overview

### Core Layers
- **DependencyManager**: Centralized service instantiation and lifecycle management.
- **ManagerRegistry**: Service locator for all managers/services (card data, RAG, LLM, DB, cache, etc.).
- **Interactor**: Orchestrates high-level workflows, coordinates between managers, exposes business logic.
- **MCPManager**: Protocol server, dispatches MCP (JSON-RPC) requests to Interactor methods.

### Data Flow
- MCPManager receives requests (JSON-RPC or legacy)
- MCPManager validates, dispatches to Interactor
- Interactor calls appropriate manager/service (e.g., CardDataManager, RAGManager)
- Results returned to MCPManager, then to client

### Extensibility
- New features are added by extending Interactor and ManagerRegistry
- MCPManager exposes new tools by mapping to Interactor methods
- All dependencies are injected via ManagerRegistry for testability and flexibility

## 2. Deck Builder Integration Plan

### A. New Components
- **DeckBuilderManager**: Implements deck construction, validation, optimization, and analysis logic
- **Deck entity**: Domain model for decks (format, cards, sections, metadata)

### B. Integration Points
- Add `deck_builder_manager` property to ManagerRegistry (instantiated with required dependencies)
- Extend Interactor with deck-related methods:
  - `build_deck(format, constraints, theme, commander, ...)`
  - `suggest_cards(deck, constraints)`
  - `analyze_deck(deck)`
  - `export_deck(deck, format)`
- MCPManager: Register new MCP tools (methods) for deck building:
  - `build_deck`, `suggest_cards`, `analyze_deck`, `export_deck`
  - Define input/output schemas for each tool

### C. Data Flow for Deck Building
1. Client sends MCP request (e.g., `build_deck` with format and constraints)
2. MCPManager validates and dispatches to Interactor
3. Interactor calls DeckBuilderManager, passing dependencies (card data, RAG, LLM, etc.)
4. DeckBuilderManager constructs deck, analyzes, and returns result
5. MCPManager returns result to client

### D. Example MCP Tool Registration
- Add to MCPManager:
  - `build_deck`: {"format": "Commander", "theme": "aristocrats", "budget": 200, ...}
  - `suggest_cards`: {"deck": {...}, "constraints": {...}}
  - `analyze_deck`: {"deck": {...}}
  - `export_deck`: {"deck": {...}, "format": "Arena"}

### E. Testing & Validation
- Unit tests for DeckBuilderManager and Interactor deck methods
- E2E MCP tests for deck building workflows
- Validate with sample decks and user scenarios

## 3. Architectural Fit Summary
- Deck builder fits cleanly as a new manager/service, injected via ManagerRegistry
- Interactor exposes deck building as high-level use cases
- MCPManager makes deck building available to all MCP clients (CLI, web, etc.)
- Follows existing patterns for extensibility, testability, and protocol integration

---

This plan ensures the deck builder is modular, testable, and fully integrated with the MCP protocol and existing architecture. All new features will be accessible via MCP tools and orchestrated through the Interactor and ManagerRegistry.
