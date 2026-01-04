# Recommended Improvements for AI Auto-Committer

## 1. Architecture & Code Structure (Priority: High)
### Refactor `gui.py` (The "God Object" Problem)
The current `gui.py` file mixes UI definition, business logic, and state management. This makes maintenance difficult and the code fragile.
* **Action:** Split `gui.py` into separate modules following an MVC or MVVM pattern.
    * `views/`: Contains only UI layout code (CustomTkinter widgets).
    * `controllers/` or `viewmodels/`: Handles user interactions (button clicks) and calls the services.
    * `models/`: Manages the application state (selected files, current repo path).
* **Benefit:** Easier to test, maintain, and upgrade the UI library in the future without breaking logic.

## 2. AI Service & Context Management (Priority: High)
### Smart Diff Truncation
Currently, the diff is arbitrarily cut off at 4000 characters (`diff_text[:4000]`). This can result in broken context or missing critical changes.
* **Action:** Implement a smarter token/character management strategy.
    * Use a token counter (approximate) instead of raw characters.
    * Summarize large files separately if needed.
    * Prioritize "meaningful" code over auto-generated files (e.g., ignore `package-lock.json` or `.map` files in the prompt context).

## 3. Robustness & Error Handling (Priority: Medium)
### Specific Error Catching
The code currently uses broad `try...except Exception` blocks, which hide specific issues (like Permission Errors).
* **Action:** Catch specific exceptions (e.g., `git.exc.NoSuchPathError`, `PermissionError`) and provide distinct user feedback for each.

### Git Dependency Check
The app assumes Git is installed and available in the system PATH.
* **Action:** Add a startup check to verify `git` is accessible. If not, display a friendly dialog guiding the user to install Git.

## 4. Feature Requests & Enhancements
### 🌍 Universal Code File Support (Language Agnostic)
Ensure the application explicitly supports and handles all types of code files, not just Python.
* **Action:** * Verify `git_service.py` does not unintentionally filter out non-Python extensions.
    * Update the System Prompt in `ai_service.py` to explicitly ask the AI to identify the programming language of the diff and format the commit message accordingly (e.g., "Fix (JS): ...").
    * Add handling for large non-code files (images, binaries) to prevent them from consuming the AI context window.

### Configuration Validation
* **Action:** Improve `config.py` to validate the structure of `settings.json` on load, preventing crashes if the file is corrupted.