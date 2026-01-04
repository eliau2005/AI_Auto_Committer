# Refactor `gui.py` (The "God Object" Problem)

The current `gui.py` file mixes UI definition, business logic, and state management. This makes maintenance difficult and the code fragile.

* **Action:** Split `gui.py` into separate modules following an MVC or MVVM pattern.
    * `views/`: Contains only UI layout code (CustomTkinter widgets).
    * `controllers/` or `viewmodels/`: Handles user interactions (button clicks) and calls the services.
    * `models/`: Manages the application state (selected files, current repo path).

* **Benefit:** Easier to test, maintain, and upgrade the UI library in the future without breaking logic.
