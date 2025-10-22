# Documentation Index

This directory contains all project documentation organized by category.

---

## 📁 Directory Structure

### `/architecture` - System Design & Architecture
Core architectural decisions, design patterns, and system structure.

- **ARCHITECTURE_FLOW.md** - System architecture and data flow
- **ARCHITECTURE_REFACTOR_IMPACT.md** - Impact analysis of refactoring decisions
- **RAG_ARCHITECTURE_DIAGRAM.md** - RAG (Retrieval-Augmented Generation) architecture
- **DEPENDENCY_INJECTION_REFACTORING.md** - DI pattern implementation
- **SERVICE_ABSTRACTION_COMPLETE.md** - Service layer abstraction
- **CARD_DATA_SERVICE_ABSTRACTION.md** - Card data service design
- **RAG_SERVICE_ABSTRACTION.md** - RAG service design

### `/testing` - Test Strategy & Results
Testing approach, strategies, and test execution results.

- **TESTING_REFACTORING_COMPLETE.md** - Test suite refactoring summary
- **TEST_COVERAGE_ANALYSIS.md** - Coverage assessment vs original goals
- **TEST_REFACTORING_PLAN.md** - Original test refactoring strategy
- **TEST_STRATEGY_ANALYSIS.md** - Test pyramid and strategy analysis
- **E2E_TEST_ANALYSIS.md** - E2E test quality assessment (9.1/10)
- **E2E_TEST_RESULTS.md** - Complete E2E test run results
- **E2E_RETRY_MECHANISM.md** - Retry implementation for LLM non-determinism
- **E2E_RETRY_IMPLEMENTATION_COMPLETE.md** - Retry system summary
- **PROTOCOL_BASED_TESTING.md** - Protocol-based testing approach
- **TEST_AUDIT_REPORT.md** - Test audit findings (108 tests analyzed)
- **TEST_ANALYSIS_SUMMARY.md** - High-level test analysis summary
- **TEST_PERFORMANCE_FIX.md** - Test performance optimization

### `/phases` - Development Phase Summaries
Completion status and summaries for each development phase.

- **PHASE_1_MOCK_INFRASTRUCTURE_COMPLETE.md** - Mock LLM infrastructure (Phase 1)
- **PHASE_2A_RAG_COMPLETE.md** - RAG integration (Phase 2A)
- **PHASE_2_COMPLETE.md** - Additional unit tests (Phase 2)
- **PHASE_2_PROGRESS.md** - Phase 2 progress tracking
- **PHASE_3_COMPLETE.md** - E2E test reorganization (Phase 3)
- **PHASE_4_MIGRATION_COMPLETE.md** - PostgreSQL to SQLite migration (Phase 4)
- **PHASE_4_STATUS.md** - Phase 4 status and decisions
- **PHASE_5_COMPLETE.md** - Performance optimization (Phase 5)
- **PHASE_5.1_COMPLETE.md** - Caching implementation (Phase 5.1)
- **SQLITE_MIGRATION_COMPLETE.md** - SQLite migration details

### `/performance` - Performance Analysis & Optimization
Performance benchmarks, optimization plans, and results.

- **PHASE_4_PERFORMANCE.md** - Phase 4 performance metrics
- **PHASE_5.1_PERFORMANCE_PLAN.md** - Phase 5.1 optimization strategy
- **PHASE_5.1_CACHING_RESULTS.md** - Caching performance results
- **PERFORMANCE_DATA_ISSUE.md** - Performance issue analysis

### `/setup` - Setup & Environment Guides
Installation, setup, and environment configuration instructions.

- **QUICKSTART.md** - Quick start guide for developers
- **SETUP_ENVIRONMENT.md** - Environment setup instructions
- **SETUP_SUMMARY.md** - Setup process summary
- **SSL_FIX_MACOS.md** - macOS SSL certificate fix
- **DATA_LAYER_SETUP.md** - Data layer setup guide

### `/archive` - Archived Documentation
Historical documentation, superseded plans, and completed checklists.

- Completed session summaries
- Old architecture documents
- Superseded plans and checklists
- Migration records

---

## 🚀 Quick Links

### For New Developers
1. Start with **[QUICKSTART.md](setup/QUICKSTART.md)**
2. Read **[ARCHITECTURE_FLOW.md](architecture/ARCHITECTURE_FLOW.md)**
3. Review **[TEST_COVERAGE_ANALYSIS.md](testing/TEST_COVERAGE_ANALYSIS.md)**

### For Testing
1. **[TESTING_REFACTORING_COMPLETE.md](testing/TESTING_REFACTORING_COMPLETE.md)** - Test suite overview
2. **[E2E_TEST_RESULTS.md](testing/E2E_TEST_RESULTS.md)** - Latest E2E results
3. **[E2E_RETRY_MECHANISM.md](testing/E2E_RETRY_MECHANISM.md)** - Handling LLM non-determinism

### For Architecture Understanding
1. **[ARCHITECTURE_FLOW.md](architecture/ARCHITECTURE_FLOW.md)** - System overview
2. **[RAG_ARCHITECTURE_DIAGRAM.md](architecture/RAG_ARCHITECTURE_DIAGRAM.md)** - RAG system
3. **[SERVICE_ABSTRACTION_COMPLETE.md](architecture/SERVICE_ABSTRACTION_COMPLETE.md)** - Service layer

### For Performance Analysis
1. **[PHASE_5.1_CACHING_RESULTS.md](performance/PHASE_5.1_CACHING_RESULTS.md)** - Caching results
2. **[PHASE_4_PERFORMANCE.md](performance/PHASE_4_PERFORMANCE.md)** - Database performance

---

## 📊 Project Status

**Current Phase:** Phase 5.1 Complete  
**Test Suite:** 183 tests (165 unit + 18 E2E)  
**Test Status:** ✅ All passing  
**Database:** SQLite (35,402 cards)  
**Vector Store:** ChromaDB (35,402 embeddings)  
**LLM:** Ollama (llama3)

---

## 📝 Recent Updates

- ✅ E2E retry mechanism implemented (3-attempt system)
- ✅ Test refactoring complete (100x speed improvement)
- ✅ SQLite migration complete (21.9x faster queries)
- ✅ Caching system implemented (100% hit rate after warmup)
- ✅ Documentation reorganized (52 files → organized structure)

---

## 🔗 External Resources

- **Root README:** [../README.md](../README.md)
- **Project Roadmap:** [../PROJECT_ROADMAP.md](../PROJECT_ROADMAP.md)
- **License:** [../LICENSE](../LICENSE)

---

**Last Updated:** October 21, 2025
