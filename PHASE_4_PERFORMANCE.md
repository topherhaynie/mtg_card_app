# MCP Tool Performance Check Results

Date: October 21, 2025

This document records the observed response times for core MCP tools in the MTG Card App, using the current local environment and test data. The goal is to ensure simple operations complete in <100ms, and to document any known slow paths (e.g., LLM-backed tools).

## Methodology
- Used Python's `time.perf_counter()` to measure elapsed time for each tool call via the MCPManager dispatch layer.
- Ran each tool 5 times and recorded the average and max response time.
- Used the same dummy interactor as in E2E tests for consistency.

## Results

| Tool                | Avg Time (ms) | Max Time (ms) | Notes                       |
|---------------------|---------------|---------------|-----------------------------|
| initialize          |      <5       |      <10      | Metadata only               |
| search_cards        |      <5       |      <10      | Dummy data, no DB/IO        |
| explain_card        |      <5       |      <10      | LLM stub, no real model     |
| compare_cards       |      <5       |      <10      | LLM stub, no real model     |
| query_cards         |      <5       |      <10      | LLM stub, no real model     |
| find_combo_pieces   |      <5       |      <10      | Dummy logic                 |

## Known Slow Paths
- **LLM-backed tools** (explain_card, compare_cards, query_cards):
  - In production, these will call an LLM (e.g., Ollama, Claude, OpenAI), which may take 500ms–5s depending on model and hardware.
  - Current tests use a stub, so times are not representative.
- **Large DB/Vector Search** (search_cards, find_combo_pieces):
  - With a full 27k card DB and vector search, expect 10–100ms for most queries, but complex filters or cold cache may be slower.

## Recommendations
- Monitor LLM-backed tool latency in real deployments and consider async/streaming responses for long-running queries.
- Profile DB and vector search with full data to ensure <100ms for typical queries.
- Add logging for slow requests (>500ms) in production.

## Conclusion
All core tools are fast in the current test environment. Real-world performance will depend on LLM and DB backends. No blocking slow paths identified for Phase 4 completion.
