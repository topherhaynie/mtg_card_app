# Architecture Documentation

**Last Updated:** October 21, 2025  
**Status:** Current and Verified

---

## 📖 Primary Reference

**[ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)** - Complete architecture reference

This is the **single source of truth** for the application's architecture. It includes:

- Complete layer breakdown (Interface → Business Logic → Managers → Services → Storage)
- Component inventory (all 16 Interactor methods, all managers, all services)
- Data flow patterns with examples
- Dependency injection system
- Storage architecture (SQLite, JSON, ChromaDB)
- Performance metrics
- Phase 6 extension points (CLI, LLM providers, Web UI)
- Testing strategy

**Use this document when:**
- Starting a new conversation (provides complete context)
- Planning new features (shows extension points)
- Understanding data flow (has 3 detailed examples)
- Debugging issues (shows all dependencies)

---

## 📚 Historical Documents

These documents have been archived as they're superseded by ARCHITECTURE_OVERVIEW.md:

- `docs/archive/ARCHITECTURE_FLOW.md` - Original flow diagrams (Oct 2025)
- `docs/archive/ARCHITECTURE_REFACTOR_IMPACT.md` - Phase 3.5 refactor analysis (Oct 20, 2025)
- `docs/archive/ARCHITECTURE_CLEANUP_STATUS.md` - Cleanup tracking
- `docs/archive/ARCHITECTURE_MIGRATION_COMPLETE.md` - SQLite migration

**Refer to archive documents only for:**
- Understanding historical decisions
- Reviewing past refactorings
- Comparing before/after states

---

## 🎯 Quick Reference

### Current Architecture State (Phase 5.1 Complete)

```
Interface Layer (MCP ✅, CLI 📋, Web 📋)
      ↓
Business Logic (Interactor - 16 public methods)
      ↓
Dependency Injection (ManagerRegistry + DependencyManager)
      ↓
Managers (CardData, RAG, LLM, Database, DeckBuilder, MCP)
      ↓
Services (SQLite, JSON, ChromaDB, Scryfall, Ollama)
      ↓
Storage (cards.db, combos.json, chroma/, Scryfall API, Ollama)
```

### Key Metrics

- **Cards:** 35,402 in SQLite database
- **Performance:** <1ms card lookups, <5ms semantic search
- **Tests:** 169 unit tests passing, 18 integration tests
- **Code Quality:** 0 linting errors, modern type annotations

### Extension Points for Phase 6

**CLI Commands:**
- Location: `mtg_card_app/ui/cli/commands/`
- Pattern: Import registry, call `interactor.method()`, format output

**LLM Providers:**
- Location: `mtg_card_app/managers/llm/services/`
- Pattern: Implement `LLMService` protocol, add to config

**Web API:**
- Location: `mtg_card_app/ui/web/backend/routes/`
- Pattern: FastAPI routes call `interactor.method()`, return JSON

---

## 🔗 Related Documentation

- **[PROJECT_ROADMAP.md](../../PROJECT_ROADMAP.md)** - Overall project plan (Phases 1-7)
- **[PHASE_6_PLAN.md](../phases/PHASE_6_PLAN.md)** - CLI & Infrastructure plan
- **[PHASE_7_PLAN.md](../phases/PHASE_7_PLAN.md)** - Web UI plan
- **[docs/testing/](../testing/)** - Testing strategy and guidelines

---

## 💡 Tips for New Context Windows

When starting a new conversation, share **ARCHITECTURE_OVERVIEW.md** to provide:

1. **Complete system understanding** - All layers and components
2. **Current capabilities** - All 16 Interactor methods documented
3. **Extension points** - Where to add new features
4. **Performance baseline** - Current metrics
5. **Testing approach** - Unit/integration/E2E strategy

This single document contains everything needed to continue development without needing to explore the codebase.

---

**Maintained by:** Project Lead  
**Review Schedule:** After each phase completion  
**Next Review:** After Phase 6 implementation
