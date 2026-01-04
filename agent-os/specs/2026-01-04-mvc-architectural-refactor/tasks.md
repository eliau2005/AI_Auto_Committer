# Task Breakdown: MVC Architectural Refactor

## Overview
Total Tasks: 25

## Task List

### Model Layer

#### Task Group 1: Application State
**Dependencies:** None

- [x] 1.0 Complete Model Layer
  - [x] 1.1 Write 2-4 focused tests for `AppState`
    - Test initial state values
    - Test state update methods (e.g., `update_repo_path`, `set_selected_files`)
    - Test observer/notification mechanism if applicable (or simple state retrieval)
  - [x] 1.2 Create `models/app_state.py`
    - Class `AppState`
    - Properties: `repo_path` (str), `current_branch` (str), `changed_files` (List[str]), `selected_files` (Set[str]), `commit_title` (str), `commit_description` (str), `is_loading` (bool)
    - Methods: setters that strictly type-check and update these values
  - [x] 1.3 Ensure Model layer tests pass
    - Run ONLY the tests written in 1.1

**Acceptance Criteria:**
- `AppState` class exists and holds all necessary application state.
- State updates are correctly reflected.
- Tests pass.

### View Layer

#### Task Group 2: Shared UI Assets & Dialogs
**Dependencies:** Task Group 1

- [x] 2.0 Complete Shared UI Assets
  - [x] 2.1 Create `views/styles.py`
    - Extract colors, fonts, and padding constants from `gui.py`
  - [x] 2.2 Create `views/settings_dialog.py`
    - Port `SettingsDialog` logic from `gui.py`
    - Update to use `views/styles.py`
  - [x] 2.3 Create `views/error_dialog.py`
    - Port error dialog logic (if any custom logic exists, otherwise ensure `messagebox` usage is wrapped/standardized)
  - [x] 2.4 Write 2 focused tests for Dialog instantiation
    - Ensure they can be instantiated without errors (mocking parent window)

**Acceptance Criteria:**
- Shared styles are centralized.
- Dialog classes are isolated in their own files.

#### Task Group 3: Core Views
**Dependencies:** Task Group 2

- [x] 3.0 Complete Core Views
  - [x] 3.1 Create `views/diff_view.py`
    - Port diff tabview logic
    - Class `DiffView(ctk.CTkFrame)`
    - Method `update_diffs(diff_text: str)` or similar
  - [x] 3.2 Create `views/commit_view.py`
    - Port commit form sidebar logic
    - Class `CommitView(ctk.CTkFrame)`
    - Constructor should accept callbacks: `on_generate`, `on_commit`
    - Methods: `get_commit_message()`, `set_commit_message()`, `set_loading(bool)`
  - [x] 3.3 Create `views/main_window.py`
    - Port `App` class layout logic from `gui.py`
    - Class `MainWindow(ctk.CTk)`
    - Initialize `CommitView` and `DiffView`
    - Setup layout grid/pack
  - [x] 3.4 Write 2-4 focused tests for Main Window structure
    - Verify `MainWindow` contains `CommitView` and `DiffView`
    - Verify layout structure (basic existence check)

**Acceptance Criteria:**
- All UI components are ported to `views/` directory.
- `gui.py` UI logic is fully replicated in Views.
- Views accept callbacks for user actions.

### Controller Layer

#### Task Group 4: Main Controller & Orchestration
**Dependencies:** Task Groups 1-3

- [x] 4.0 Complete Controller Layer
  - [x] 4.1 Write 2-4 focused tests for `MainController` logic
    - Mock `GitService` and `AIService`
    - Test `load_repo` updates `AppState`
    - Test `generate_message` triggers `AIService` and updates `AppState`
  - [x] 4.2 Create `controllers/main_controller.py`
    - Class `MainController`
    - Init: `AppState`, `MainWindow`, `GitService`, `AIService`, `ConfigManager`
    - Implement `_run_async` and `_task` pattern (threading)
    - Implement methods: `select_directory`, `refresh_repo`, `generate_commit_message`, `perform_commit`
  - [x] 4.3 Wire Controller to View Events
    - Pass controller methods to `MainWindow` -> `CommitView`/`DiffView` as callbacks
    - Ensure `AppState` changes trigger UI updates (e.g., `MainWindow.update_from_state(state)`)
  - [x] 4.4 Ensure Controller tests pass
    - Run ONLY tests from 4.1

**Acceptance Criteria:**
- `MainController` orchestrates all services and UI.
- Async operations work as expected.
- Application logic is decoupled from UI code.

### Integration & Verification

#### Task Group 5: Entry Point & Cleanup
**Dependencies:** Task Group 4

- [x] 5.0 Integration
  - [x] 5.1 Update `main.py`
    - Instantiate `AppState`, Services, `MainController`, `MainWindow`
    - Start the app loop
  - [x] 5.2 Manual Verification of UI Parity (Visual Check)
    - Verify diffs load
    - Verify commit generation works
    - Verify settings dialog opens
  - [x] 5.3 Delete `gui.py`
    - Once confirmed, remove the old file
  - [x] 5.4 Run existing integration tests
    - Ensure `tests/test_integration.py` pass (may need minor updates if it imported `gui.py` classes directly)

**Acceptance Criteria:**
- `main.py` is clean.
- `gui.py` is removed.
- App functions exactly as before.

#### Task Group 6: Test Gap Analysis
**Dependencies:** Task Group 5

- [x] 6.0 Final Test Review
  - [x] 6.1 Review coverage for critical paths
    - Focus on new Controller logic
  - [x] 6.2 Add up to 5 additional integration tests if needed
    - e.g., End-to-end flow from `load_repo` to `commit` via Controller
  - [x] 6.3 Run all tests
    - Ensure green suite

**Acceptance Criteria:**
- Test suite passes.
- Critical paths covered.

## Execution Order
1. Model Layer (Task Group 1)
2. View Layer (Task Group 2 & 3)
3. Controller Layer (Task Group 4)
4. Integration & Verification (Task Group 5 & 6)
