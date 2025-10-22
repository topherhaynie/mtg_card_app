# CLI Testing Implementation Plan

## Current Status
- **Completed**: 3/8 commands (37.5%)
- **Tests Passing**: 28/28 ✅
- **Test Files Created**: 3 (test_card.py, test_search.py, test_stats.py)
- **Commit**: `3a144c3` - "test: Add comprehensive CLI command tests (28 passing)"

## Remaining Commands

### Priority 1: Core Commands

#### 1. Update Command (`test_update.py`)
**Complexity**: Low  
**Estimated Tests**: 6-8  
**File**: `mtg_card_app/ui/cli/commands/update.py`

**Test Cases**:
- [ ] Basic update execution
- [ ] Update with specific sources
- [ ] Update all data
- [ ] Update card data only
- [ ] Update combos only
- [ ] Progress display
- [ ] Error handling (network failures, permission issues)
- [ ] Successful completion message

**Mock Needs**:
- Mock data update methods
- Mock progress callbacks

---

#### 2. Setup Command (`test_setup.py`)
**Complexity**: Medium  
**Estimated Tests**: 8-10  
**File**: `mtg_card_app/ui/cli/commands/setup.py`

**Test Cases**:
- [ ] Setup wizard start
- [ ] Interactive prompts (if testable)
- [ ] Default configuration
- [ ] Custom configuration
- [ ] Database initialization
- [ ] Data download options
- [ ] LLM provider selection
- [ ] Setup completion
- [ ] Skip existing setup
- [ ] Error handling

**Mock Needs**:
- Mock user input (if interactive)
- Mock configuration manager
- Mock data initialization

---

### Priority 2: Feature Commands

#### 3. Combo Command (`test_combo.py`)
**Complexity**: Medium-High  
**Estimated Tests**: 12-15  
**File**: `mtg_card_app/ui/cli/commands/combo.py`

**Subcommands**:

##### `combo find` (4 tests)
- [ ] Find combos by card name
- [ ] Multiple card search
- [ ] No results found
- [ ] Error handling

##### `combo search` (4 tests)
- [ ] Search by colors
- [ ] Search by power level
- [ ] Search with filters
- [ ] Error handling

##### `combo add` (3 tests)
- [ ] Add new combo
- [ ] Interactive combo creation
- [ ] Error handling

##### `combo remove` (3 tests)
- [ ] Remove combo by name
- [ ] Confirmation prompt
- [ ] Error handling

**Mock Needs**:
- `find_combos_by_card()`
- `search_combos()`
- `create_combo()`
- Combo deletion methods

---

#### 4. Deck Command (`test_deck.py`)
**Complexity**: High  
**Estimated Tests**: 18-22  
**File**: `mtg_card_app/ui/cli/commands/deck.py`

**Subcommands**:

##### `deck build` (4 tests)
- [ ] Build commander deck
- [ ] Build with theme
- [ ] Build with constraints
- [ ] Error handling

##### `deck validate` (3 tests)
- [ ] Valid deck
- [ ] Invalid deck (errors)
- [ ] Error handling

##### `deck analyze` (4 tests)
- [ ] Full deck analysis
- [ ] Analysis output formats
- [ ] Detailed stats display
- [ ] Error handling

##### `deck suggest` (3 tests)
- [ ] Get improvement suggestions
- [ ] Budget constraints
- [ ] Error handling

##### `deck export` (3 tests)
- [ ] Export to different formats (text, Arena, MTGO)
- [ ] File output
- [ ] Error handling

##### `deck load` (3 tests)
- [ ] Load from file
- [ ] Load from different formats
- [ ] Error handling

**Mock Needs**:
- `build_deck()`
- `validate_deck()`
- `analyze_deck()`
- `suggest_cards()`
- `export_deck()`
- File I/O mocking

---

#### 5. Config Command (`test_config.py`)
**Complexity**: Medium  
**Estimated Tests**: 12-15  
**File**: `mtg_card_app/ui/cli/commands/config.py`

**Subcommands**:

##### `config get` (3 tests)
- [ ] Get specific setting
- [ ] Setting not found
- [ ] Error handling

##### `config set` (3 tests)
- [ ] Set setting value
- [ ] Invalid value
- [ ] Error handling

##### `config list` (2 tests)
- [ ] List all settings
- [ ] Error handling

##### `config provider` (4 tests)
- [ ] List LLM providers
- [ ] Set active provider
- [ ] Configure provider settings
- [ ] Error handling

##### `config reset` (3 tests)
- [ ] Reset all settings
- [ ] Reset specific setting
- [ ] Error handling

**Mock Needs**:
- Configuration manager methods
- Config file I/O

---

## Implementation Strategy

### Phase 1: Simple Commands (Week 1)
**Goal**: Complete update and setup tests  
**Estimated Time**: 2-4 hours

1. Create `test_update.py` (6-8 tests)
2. Create `test_setup.py` (8-10 tests)
3. Run tests and fix issues
4. Commit: "test: Add update and setup command tests"

**Outcome**: 42-46 total tests

---

### Phase 2: Feature Commands Part 1 (Week 1-2)
**Goal**: Complete combo and partial deck tests  
**Estimated Time**: 3-5 hours

1. Create `test_combo.py` (12-15 tests)
2. Start `test_deck.py` (build, validate, analyze - 11 tests)
3. Run tests and fix issues
4. Commit: "test: Add combo and deck command tests (partial)"

**Outcome**: 65-72 total tests

---

### Phase 3: Feature Commands Part 2 (Week 2)
**Goal**: Complete all remaining tests  
**Estimated Time**: 3-4 hours

1. Complete `test_deck.py` (suggest, export, load - 9 tests)
2. Create `test_config.py` (12-15 tests)
3. Run tests and fix issues
4. Commit: "test: Complete all CLI command tests"

**Outcome**: 86-96 total tests

---

### Phase 4: Polish & Coverage (Week 2)
**Goal**: Ensure quality and coverage  
**Estimated Time**: 1-2 hours

1. Run full test suite
2. Generate coverage report
3. Add missing edge cases
4. Update documentation
5. Final commit: "test: CLI test suite complete with coverage report"

**Outcome**: ~100 tests, 80%+ coverage

---

## Test File Template

```python
"""Tests for the [COMMAND] command."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from mtg_card_app.ui.cli.commands.[COMMAND] import [COMMAND]

if TYPE_CHECKING:
    from click.testing import CliRunner


class Test[Command]Command:
    """Test suite for the [COMMAND] command."""

    def test_[COMMAND]_basic(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test basic [COMMAND] command functionality."""
        # Setup
        mock_interactor.[METHOD].return_value = [EXPECTED]

        # Execute
        with patch(
            "mtg_card_app.ui.cli.commands.[COMMAND].Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke([COMMAND], [ARGS])

        # Assert
        assert result.exit_code == 0
        assert [EXPECTED] in result.output

    def test_[COMMAND]_error_handling(
        self, cli_runner: CliRunner, mock_interactor: Mock,
    ) -> None:
        """Test [COMMAND] command error handling."""
        mock_interactor.[METHOD].side_effect = Exception("Error")

        with patch(
            "mtg_card_app.ui.cli.commands.[COMMAND].Interactor",
            return_value=mock_interactor,
        ):
            result = cli_runner.invoke([COMMAND], [ARGS])

        assert "Error:" in result.output or "error" in result.output.lower()
```

---

## Success Criteria

### Test Quality
- ✅ All commands have comprehensive test coverage
- ✅ All output formats tested (where applicable)
- ✅ Error handling tested for each command
- ✅ Edge cases covered
- ✅ Mock isolation maintains test independence

### Coverage Goals
- **Minimum**: 75% coverage for CLI module
- **Target**: 80-85% coverage for CLI module
- **100% passing**: All tests must pass

### Documentation
- ✅ All test files have clear docstrings
- ✅ Test purposes are self-evident from names
- ✅ Mock fixtures documented in conftest
- ✅ Progress tracking updated

---

## Potential Issues & Solutions

### Issue 1: Click Group Commands
**Problem**: Combo, deck, and config use Click groups with subcommands  
**Solution**: Test each subcommand separately, verify group registration

### Issue 2: Interactive Prompts
**Problem**: Setup wizard may have interactive prompts  
**Solution**: Use CliRunner's `input` parameter or mock prompt functions

### Issue 3: File I/O in deck load/export
**Problem**: Commands may read/write files  
**Solution**: Mock file operations or use temporary files with `tmp_path` fixture

### Issue 4: Complex Mock Return Values
**Problem**: Some commands expect complex nested data structures  
**Solution**: Create specific fixtures for complex responses

---

## Next Session Checklist

When you continue with CLI testing:

1. **Review this plan** - Understand the scope and approach
2. **Choose starting point** - Recommend: Update command (simplest)
3. **Read command file** - Understand what the command does
4. **Create test file** - Use template above
5. **Run tests** - Verify they pass
6. **Iterate** - Add more test cases as needed
7. **Commit** - Save progress incrementally

---

## Resources

### Test Fixtures Available
- `cli_runner` - Click test runner
- `mock_interactor` - Fully mocked Interactor
- `mock_interactor_factory` - Custom mock creation
- `sample_deck` - Sample deck data
- `sample_combo` - Sample combo data

### Command Files
- `mtg_card_app/ui/cli/commands/update.py`
- `mtg_card_app/ui/cli/commands/setup.py`
- `mtg_card_app/ui/cli/commands/combo.py`
- `mtg_card_app/ui/cli/commands/deck.py`
- `mtg_card_app/ui/cli/commands/config.py`

### Test Files to Create
- `tests/unit/cli/commands/test_update.py`
- `tests/unit/cli/commands/test_setup.py`
- `tests/unit/cli/commands/test_combo.py`
- `tests/unit/cli/commands/test_deck.py`
- `tests/unit/cli/commands/test_config.py`

---

## Estimated Timeline

| Phase | Tasks | Tests | Time | Completion |
|-------|-------|-------|------|------------|
| **Current** | card, search, stats | 28 | - | ✅ Complete |
| **Phase 1** | update, setup | 14-18 | 2-4 hrs | 📋 Next |
| **Phase 2** | combo, deck (partial) | 23-26 | 3-5 hrs | 📋 Pending |
| **Phase 3** | deck (complete), config | 21-24 | 3-4 hrs | 📋 Pending |
| **Phase 4** | polish, coverage | +10 | 1-2 hrs | 📋 Pending |
| **Total** | All commands | ~100 | 9-15 hrs | 37.5% |

---

## Final Notes

- **Don't rush**: Quality over quantity - each test should be meaningful
- **Test behavior, not implementation**: Focus on what commands do, not how
- **Keep mocks simple**: Only mock what's necessary
- **Run tests frequently**: Catch issues early
- **Commit often**: Save progress incrementally
- **Update tracking**: Keep CLI_TESTING_PROGRESS.md current

The foundation is solid. The remaining commands follow the same patterns established in the first three test files. Good luck! 🚀
