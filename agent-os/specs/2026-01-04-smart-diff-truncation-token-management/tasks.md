# Task Breakdown: Smart Diff Truncation & Token Management

## Overview
Total Tasks: 15

## Task List

### Core Logic (Backend)

#### Task Group 1: Diff Processor Refinement
**Dependencies:** None

- [x] 1.0 Complete DiffProcessor logic
  - [x] 1.1 Write 2-8 focused tests for sacrifice order and proportional budgeting
    - Test correct sacrifice order (Ignored -> Lock -> Unknown -> Docs -> Config -> Logic)
    - Test proportional budgeting (multiple files getting capped instead of one being wiped)
  - [x] 1.2 Fix sacrifice order in `DiffProcessor`
    - Update `sacrifice_order` list to match spec exactly
    - Ensure `UNKNOWN` category is handled in correct order
  - [x] 1.3 Implement Proportional Budgeting
    - Add logic to calculate per-file budget if categorization sacrifice isn't enough
    - Cap each file's tokens proportionally to its size relative to total
    - Ensure at least a partial view of all files remains
  - [x] 1.4 Ensure DiffProcessor tests pass
    - Run ONLY the tests written in 1.1

**Acceptance Criteria:**
- Sacrifice order matches: IGNORED -> LOCK -> UNKNOWN -> DOCS -> CONFIG -> LOGIC
- Proportional budgeting ensures all files get some representation if space permits
- Tests pass

### Service Layer

#### Task Group 2: AI Service Integration
**Dependencies:** Task Group 1

- [x] 2.0 Integrate DiffProcessor into AI Service
  - [x] 2.1 Write 2-8 focused tests for AI Service integration
    - Test `generate_commit_message` uses `DiffProcessor`
    - Test `summarize_file_diff` is called correctly as a callback
    - Test fallback when summarization fails
  - [x] 2.2 Update `ai_service.py` to use `DiffProcessor`
    - Instantiate `DiffProcessor` with `TokenManager`, `FilePrioritizer`, and `summarize_file_diff`
    - Replace manual string slicing with `diff_processor.process_diff`
  - [x] 2.3 Implement/Verify `summarize_file_diff`
    - Ensure it calls the AI provider with a specific summarization prompt
    - Handle errors gracefully
  - [x] 2.4 Ensure AI Service tests pass
    - Run ONLY the tests written in 2.1

**Acceptance Criteria:**
- `generate_commit_message` respects token limits via `DiffProcessor`
- Summarization is attempted for large files
- Fallbacks work

### Application State & UI

#### Task Group 3: State Management & UI Feedback
**Dependencies:** Task Group 2

- [x] 3.0 Wire up UI Truncation Warning
  - [x] 3.1 Write 2-8 focused tests for AppState and UI updates
    - Test `AppState` storing `is_truncated` flag
    - Test `DiffView` showing/hiding warning based on flag
  - [x] 3.2 Update `AppState` model
    - Add `diff_is_truncated` boolean property (or similar)
    - Add method to update this state
  - [x] 3.3 Update Controller/Service to set state
    - Ensure `ai_service` returns truncation status
    - Update `main_controller` to set `AppState.diff_is_truncated`
  - [x] 3.4 Connect `DiffView` to AppState
    - Ensure `DiffView` observes `diff_is_truncated`
    - Call `set_warning` appropriately
  - [x] 3.5 Ensure State/UI tests pass
    - Run ONLY the tests written in 3.1

**Acceptance Criteria:**
- `AppState` accurately reflects if the current diff was truncated
- `DiffView` displays warning banner when truncated
- Warning clears when a new non-truncated diff is generated

### Verification

#### Task Group 4: Final Verification
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review and Verify
  - [x] 4.1 Review tests from Groups 1-3
    - Ensure critical paths are covered
  - [x] 4.2 Analyze test coverage gaps
    - Focus on edge cases (e.g., empty diffs, 100% ignored files, API errors)
  - [x] 4.3 Write up to 10 additional integration tests
    - End-to-end flow: Large Diff -> Summarization -> UI Warning -> Commit Message
  - [x] 4.4 Run feature-specific tests
    - Verify the entire feature works as expected

**Acceptance Criteria:**
- Full feature works end-to-end
- UI accurately reflects backend state
- Token limits are strictly enforced using `tiktoken`
