# Specification: MVC Architectural Refactor

## Goal
Refactor the monolithic `gui.py` into a modular MVC (Model-View-Controller) architecture to improve maintainability, testability, and separation of concerns while maintaining 100% functional parity.

## User Stories
- As a developer, I want a clear separation between UI and logic so that I can easily maintain and extend the application.
- As a developer, I want the application state to be managed independently of the UI components so that I can implement unit tests for the business logic.

## Specific Requirements

**Models: Application State Management**
- Create `models/app_state.py` to encapsulate all application-level state.
- State should include: `repo_path`, `current_branch`, `changed_files` (list of strings), `selected_files` (set of strings), `commit_title`, and `commit_description`.
- Implement methods to update state and potentially notify listeners (using callbacks or an observable pattern).

**Views: UI Modularization**
- Create `views/` directory for all `CustomTkinter` related components.
- `views/main_window.py`: The root window inheriting from `ctk.CTk`. It should manage the high-level layout (header, sidebar, main area, status bar).
- `views/commit_view.py`: A specialized component for the sidebar's commit form (title entry, description textbox, generate/commit buttons).
- `views/diff_view.py`: A specialized component for the diff tabview, handling the creation and styling of diff tabs.
- `views/settings_dialog.py` and `views/error_dialog.py`: Move dialog classes from `gui.py` to their own files in `views/`.

**Controllers: Orchestration**
- Create `controllers/main_controller.py` as the central coordinator.
- The controller should hold instances of `GitService`, `AIService`, `AppState`, and `MainWindow`.
- It must handle user interactions (button clicks, repo selection) by calling appropriate services and updating the model.
- It should manage asynchronous operations (threading) to keep the UI responsive during Git or AI operations.

**View-Controller Communication**
- Views should not have direct access to services or the model.
- Use a delegate/callback pattern where the Controller passes functions to the Views for event handling.
- Views should only be responsible for rendering and capturing user input.

**Entry Point: main.py Refactor**
- Update `main.py` to initialize the `MainController` and start the application loop.
- Remove all UI definition logic from the entry point.

**Constants and Styling**
- Move UI-wide constants (colors, fonts, padding) to a shared file, e.g., `views/styles.py` or keep them in a dedicated module if they grow.

**Testing and Verification**
- Write unit tests for `MainController` and `AppState`.
- Ensure all existing integration tests pass with the new structure.
- Verify that the UI remains identical in appearance and behavior.

## Existing Code to Leverage

**gui.py Styling and Layout**
- Reuse the exact `CustomTkinter` configurations, colors, and layout logic currently in `gui.py` to ensure visual parity.

**gui.py Threading Logic**
- Replicate the `_run_async` and `_task` pattern in the `MainController` to handle long-running operations.

**Services (GitService, AIService, ConfigManager)**
- These classes are already well-separated and should be used by the Controller without modification.

**gui.py Icon and Geometry Handling**
- Move the complex icon setting logic and window geometry persistence to `MainWindow` and `MainController` respectively.

## Out of Scope
- Adding any new features or UI elements.
- Changing existing services (`GitService`, `AIService`, `ConfigManager`).
- Improving the UI design or switching to a different UI framework.
- Modifying the core business logic of commit message generation or git operations.
