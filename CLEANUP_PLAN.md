# Project Cleanup Plan - October 21, 2025

## Overview
Comprehensive cleanup before Phase 6 to organize documentation, fix linting errors, and remove unused files.

---

## Phase 1: Documentation Organization

### Current State
- **52 markdown files** in root directory (excluding README.md, LICENSE)
- Mix of architecture, testing, phase summaries, and setup docs
- Difficult to navigate and find relevant information

### Target Structure
```
docs/
├── architecture/
│   ├── ARCHITECTURE_FLOW.md
│   ├── ARCHITECTURE_REFACTOR_IMPACT.md
│   ├── RAG_ARCHITECTURE_DIAGRAM.md
│   ├── DEPENDENCY_INJECTION_REFACTORING.md
│   ├── SERVICE_ABSTRACTION_COMPLETE.md
│   ├── CARD_DATA_SERVICE_ABSTRACTION.md
│   └── RAG_SERVICE_ABSTRACTION.md
├── testing/
│   ├── TESTING_REFACTORING_COMPLETE.md
│   ├── TEST_COVERAGE_ANALYSIS.md
│   ├── TEST_REFACTORING_PLAN.md
│   ├── TEST_STRATEGY_ANALYSIS.md
│   ├── E2E_TEST_ANALYSIS.md
│   ├── E2E_TEST_RESULTS.md
│   ├── E2E_RETRY_MECHANISM.md
│   ├── E2E_RETRY_IMPLEMENTATION_COMPLETE.md
│   ├── PROTOCOL_BASED_TESTING.md
│   ├── TEST_AUDIT_REPORT.md
│   ├── TEST_ANALYSIS_SUMMARY.md
│   └── TEST_PERFORMANCE_FIX.md
├── phases/
│   ├── PHASE_1_MOCK_INFRASTRUCTURE_COMPLETE.md
│   ├── PHASE_2A_RAG_COMPLETE.md
│   ├── PHASE_2_COMPLETE.md
│   ├── PHASE_2_PROGRESS.md
│   ├── PHASE_3_COMPLETE.md
│   ├── PHASE_4_MIGRATION_COMPLETE.md
│   ├── PHASE_4_STATUS.md
│   ├── PHASE_5_COMPLETE.md
│   ├── PHASE_5.1_COMPLETE.md
│   └── SQLITE_MIGRATION_COMPLETE.md
├── performance/
│   ├── PHASE_4_PERFORMANCE.md
│   ├── PHASE_5.1_PERFORMANCE_PLAN.md
│   ├── PHASE_5.1_CACHING_RESULTS.md
│   └── PERFORMANCE_DATA_ISSUE.md
├── setup/
│   ├── QUICKSTART.md
│   ├── SETUP_ENVIRONMENT.md
│   ├── SETUP_SUMMARY.md
│   ├── SSL_FIX_MACOS.md
│   └── DATA_LAYER_SETUP.md
└── archive/
    ├── ARCHITECTURE_CLEANUP_STATUS.md
    ├── ARCHITECTURE_MIGRATION_COMPLETE.md
    ├── DATA_LAYER_COMPLETE.md
    ├── ORCHESTRATOR_MIGRATION_PLAN.md
    ├── PHASE_5_ARCHITECTURE_PLAN.md
    ├── PHASE_5_CHECKLIST.md
    ├── PHASE_5_DOCUMENTATION_UPDATE.md
    ├── PHASE_5_ENHANCEMENTS.md
    ├── PHASE_5_EXPORT_COMPLETE.md
    ├── PHASE_5_SESSION_SUMMARY.md
    ├── PHASE_5_TASKS.md
    ├── POLISH_COMPLETE.md
    ├── PRE_SCALE_SUMMARY.md
    ├── PROJECT_PROGRESS_SUMMARY.md
    ├── REFACTORING_COMPLETE.md
    ├── TESTING_SETUP_COMPLETE.md
    ├── TESTING_COMMIT_MESSAGE.txt
    ├── VALIDATION_RESULTS.md
    └── RAG_STORAGE_REQUIREMENTS.md

Root (keep):
- README.md (main entry point)
- LICENSE
- PROJECT_ROADMAP.md (current roadmap)
- pyproject.toml
- requirements.txt
- requirements-dev.txt
- uv.lock
- setup.sh
- .gitignore
```

---

## Phase 2: Scripts Cleanup

### Scripts to Keep (Essential)
1. ✅ **`bulk_import_cards.py`** - Production: Import cards from JSON
2. ✅ **`import_oracle_cards.py`** - Production: Import from Scryfall
3. ✅ **`vectorize_cards.py`** - Production: Create embeddings
4. ✅ **`demo_features.py`** - Documentation: Feature demonstration

### Scripts to Remove (Obsolete/Debug)
1. ❌ **`benchmark_cache.py`** - Debug: Cache benchmarking
2. ❌ **`benchmark_performance.py`** - Debug: Performance benchmarking  
3. ❌ **`check_cache_stats.py`** - Debug: Cache statistics
4. ❌ **`migrate_cards_to_sqlite.py`** - Obsolete: One-time migration (done)
5. ❌ **`profile_performance.py`** - Debug: Profiling
6. ❌ **`test_cache_behavior.py`** - Debug: Cache testing
7. ❌ **`test_no_combos.py`** - Debug: Manual testing
8. ❌ **`test_queries.py`** - Debug: Manual testing
9. ❌ **`test_sqlite_performance.py`** - Debug: SQLite benchmarking
10. ❌ **`test_sqlite_service.py`** - Debug: Service testing
11. ❌ **`validate_polish.py`** - Obsolete: Phase 5 validation (done)

### Benchmark Data to Remove
1. ❌ **`benchmark_results.json`** - Old benchmark data
2. ❌ **`cache_benchmark_results.json`** - Old cache data

---

## Phase 3: Linting Error Fixes

### Areas to Address
1. **Type Annotations**
   - Add missing type hints
   - Fix `Any` types where possible
   - Add return type annotations

2. **Import Organization**
   - Fix `collections.abc` imports
   - Remove unused imports
   - Sort imports properly

3. **Code Style**
   - Fix magic numbers (extract to constants)
   - Remove print statements (use logging)
   - Fix assert usage in production code
   - Fix boolean function parameters

4. **Test Files**
   - Add type annotations to fixtures
   - Fix missing docstrings
   - Remove dead code

### Priority Order
1. **High:** Type safety issues (missing annotations, `Any` types)
2. **Medium:** Import organization, code style
3. **Low:** Docstring formatting, naming conventions

---

## Phase 4: File Cleanup

### Files to Remove
1. ❌ `.pytest_cache/` (can be regenerated)
2. ❌ `mtg_card_app.egg-info/` (can be regenerated)
3. ❌ `__pycache__/` directories (can be regenerated)
4. ❌ Any `.pyc` files
5. ❌ Any temporary files

### Files to Keep
- All source code in `mtg_card_app/`
- All tests in `tests/`
- All data in `data/` (cards.json, combos.json, chroma/)
- Configuration files (pyproject.toml, requirements.txt, etc.)

---

## Execution Steps

### Step 1: Create Documentation Structure
```bash
mkdir -p docs/architecture
mkdir -p docs/testing
mkdir -p docs/phases
mkdir -p docs/performance
mkdir -p docs/setup
mkdir -p docs/archive
```

### Step 2: Move Documentation Files
- Move files to appropriate directories
- Update any cross-references
- Create `docs/README.md` as index

### Step 3: Remove Obsolete Scripts
```bash
cd scripts
rm benchmark_cache.py benchmark_performance.py check_cache_stats.py
rm migrate_cards_to_sqlite.py profile_performance.py
rm test_cache_behavior.py test_no_combos.py test_queries.py
rm test_sqlite_performance.py test_sqlite_service.py validate_polish.py
```

### Step 4: Remove Benchmark Data
```bash
rm benchmark_results.json cache_benchmark_results.json
```

### Step 5: Fix Linting Errors
- Run comprehensive lint check
- Fix each file systematically
- Validate with tests after each major change

### Step 6: Clean Up Generated Files
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache/
rm -rf mtg_card_app.egg-info/
```

### Step 7: Final Validation
```bash
# Run all tests
pytest

# Run fast tests
pytest -m "not e2e"

# Verify imports
python -c "from mtg_card_app.core.interactor import Interactor; print('OK')"

# Check linting
ruff check mtg_card_app/ tests/
```

---

## Success Criteria

### Documentation
- ✅ All docs organized in `docs/` directory
- ✅ Clear directory structure (architecture, testing, phases, etc.)
- ✅ `docs/README.md` provides navigation
- ✅ Cross-references updated

### Scripts
- ✅ Only 4 essential scripts remain
- ✅ All debug/obsolete scripts removed
- ✅ Benchmark data removed

### Linting
- ✅ Zero critical linting errors
- ✅ Type annotations added where missing
- ✅ Import organization fixed
- ✅ Code style consistent

### Files
- ✅ No `__pycache__` directories
- ✅ No `.pyc` files
- ✅ Clean git status

### Validation
- ✅ All tests pass (165 unit + 18 E2E)
- ✅ Imports work correctly
- ✅ No broken references

---

## Risk Mitigation

### Before Starting
1. ✅ Commit current state: `git add -A && git commit -m "Pre-cleanup checkpoint"`
2. ✅ Create cleanup branch: `git checkout -b cleanup`

### During Cleanup
1. ✅ Make incremental commits
2. ✅ Test after each major change
3. ✅ Keep notes of any issues

### After Cleanup
1. ✅ Run full test suite
2. ✅ Verify all imports
3. ✅ Check git diff for unintended changes
4. ✅ Merge cleanup branch: `git checkout initial_build && git merge cleanup`

---

## Estimated Time

- **Documentation Organization:** 30 minutes
- **Scripts Cleanup:** 10 minutes
- **Linting Fixes:** 60-90 minutes
- **File Cleanup:** 10 minutes
- **Validation:** 20 minutes

**Total:** ~2-3 hours

---

## Next Steps After Cleanup

1. Update README.md to reference new docs structure
2. Create CONTRIBUTING.md with development guidelines
3. Proceed to Phase 6 with clean codebase

---

**Status:** 📋 PLANNED
**Ready to Execute:** ✅ YES
