# Phase 4 – MCP Interface: Status and Next Steps

Updated: October 21, 2025

## What’s done

- Transport and framing
  - JSON-RPC 2.0 over stdio with MCP-style Content-Length framing
  - Legacy single-line JSON mode maintained for simple piping/smoke
- Manager and dispatch
  - Unified manager handles legacy and JSON-RPC requests
  - JSON Schema validation for tool params; negative-path tests
  - Session history with timestamp, duration_ms, and request id (legacy and JSON-RPC)
  - Tools implemented and wired to Interactor:
    - query_cards, search_cards, find_combo_pieces
    - explain_card, compare_cards (prompt-backed)
  - Output schema advertised for search_cards; initialize includes capabilities and schemas
  - Fixed JSON serialization for Card entities (search_cards now returns dicts)
- Official MCP adapter
  - Optional official server mode with CLI switch: `--server classic|official` (default: classic)
- Tests and smoke
  - Framing tests (Content-Length)
  - Manager dispatch tests (legacy + JSON-RPC)
  - Tool and validation tests; suite is green (MCP: 13 tests)
  - Classic CLI smoke validates initialize and search_cards

## What remains for Phase 4 completion

- Initialize polish
  - Add descriptions/examples per tool and ensure version/capabilities are complete
- Output validation (optional, toggleable)
  - Validate results against advertised outputSchema where enabled
- Error contract alignment
  - Legacy error shape alignment with JSON-RPC error structure
- History/observability improvements
  - Filtered retrieval already in place (tool, since, id, error_only); add size limits/settings
- Claude Desktop integration
  - Config docs/sample config; quick start; run-through smoke
- End-to-end tests
  - Golden-path JSON-RPC sessions per tool; schema checks
- Performance sanity checks
  - Ensure <100ms for simple ops; document known slow paths (LLM)

## Scale to full card database (pre-Phase 5)

Goal: import Oracle (unique) cards and embed them for RAG.

Steps:
1) Import Scryfall oracle_cards bulk into local DB
   - Script: `scripts/import_oracle_cards.py` (downloads once and upserts)
2) Vectorize all cards
   - Script: `scripts/vectorize_cards.py` (embeds into ChromaDB)
3) Verify
   - Check `data/cards.json` size and DB stats
   - Spot-check semantic search queries

Expected outcome: ~27k cards (Oracle set) imported and embedded; RAG queries work at scale.

## Done criteria for Phase 4

- JSON-RPC + legacy paths both stable with tests
- initialize returns tools, input schemas, and output schemas where applicable
- History supports id/timestamp/duration and filtered retrieval
- Official server mode operable; documented usage
- Basic smoke validated; E2E tests for JSON-RPC added
- Full card database imported and vectorized; performance noted
