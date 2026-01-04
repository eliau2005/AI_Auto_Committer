# Spec Requirements: MVC Architectural Refactor

## Initial Description
The current `gui.py` file mixes UI definition, business logic, and state management (God Object).
Refactor `gui.py` into separate modules following an MVC pattern:
*   `views/`: UI layout (CustomTkinter).
*   `controllers/`: Logic and interaction handling.
*   `models/`: Application state management.

## Requirements Discussion

### First Round Questions

**Q1:** I assume we will keep the current functionality exactly as is, just refactoring the code structure. Is that correct, or are there any UI/Behavioral changes you want to slip in during this refactor?
**Answer:** Correct (Keep functionality exactly as is).

**Q2:** I'm thinking of the following structure:
   - `views/`: `main_window.py`, `diff_view.py`, `commit_view.py`
   - `controllers/`: `main_controller.py` (orchestrates services and views)
   - `models/`: `app_state.py` (holds repo path, selected files, commit message)
   Does this breakdown align with your vision?
**Answer:** Correct.

**Q3:** I assume we should continue using `CustomTkinter` for all UI components. Correct?
**Answer:** Correct.

**Q4:** For the `main.py` entry point, should it strictly be responsible for instantiating the `App` (or `MainController`) and nothing else?
**Answer:** Correct.

**Q5:** I'm assuming we should write tests for the new Controllers/Models as we go, or are there existing tests we need to migrate/update?
**Answer:** Correct (Update/Write tests).

### Existing Code to Reference
No similar existing features identified for reference.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Refactor the monolithic `gui.py` into a modular MVC architecture.
- **Models**: Create `models/app_state.py` to manage application state (repository path, selected files, commit messages, etc.).
- **Views**: Create `views/` directory containing:
    - `main_window.py`: Main container.
    - `diff_view.py`: Component for displaying diffs.
    - `commit_view.py`: Component for commit message inputs and actions.
- **Controllers**: Create `controllers/main_controller.py` to handle business logic, user input, and communication between Views and Services (GitService, AIService).
- **Entry Point**: Update `main.py` to simply initialize the Controller/App.
- **Behavior**: Maintain exact parity with current functionality. No new user-facing features.

### Reusability Opportunities
- Reuse existing logic from `gui.py` but move it to appropriate Controllers/Models.
- Reuse `git_service.py`, `ai_service.py`, `config.py`.

### Scope Boundaries
**In Scope:**
- Code restructuring of the GUI layer.
- Updating `main.py`.
- Updating/Creating unit tests for the new structure.

**Out of Scope:**
- Adding new features (like settings UI, new AI providers, etc.).
- Changing the visual design (look and feel should remain identical).

### Technical Considerations
- **Framework**: CustomTkinter.
- **Testing**: Ensure `pytest` passes for the new structure.
- **Dependencies**: `git_service.py` and `ai_service.py` should likely be injected into or instantiated by the Controller.
