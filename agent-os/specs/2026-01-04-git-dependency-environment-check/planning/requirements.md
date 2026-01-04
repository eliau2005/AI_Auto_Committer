# Spec Requirements: Git Dependency & Environment Check

## Initial Description
Implement startup validation to ensure Git is installed and accessible. Add specific error catching for common Git issues.

## Requirements Discussion

### First Round Questions

**Q1:** I assume we should check for the `git` executable in the system PATH at startup. If it's missing, should we display a blocking error dialog and exit, or allow the user to specify a custom Git path in the settings?
**Answer:** Perform an automatic check for Git in the system PATH at startup. If it is missing, display a clear error message and allow the user to define an alternative Git path before closing the application.

**Q2:** For "common Git issues," I'm thinking of checking for Git lock files (`.git/index.lock`), missing user identity (`user.name`/`user.email`), and insufficient folder permissions. Should these be proactive checks at startup, or should we just provide better error handling when they occur during an operation?
**Answer:** It is recommended to perform proactive checks at startup for lock files, user identity configuration, and folder permissions in order to reduce failures during operation.

**Q3:** I assume that if the application is started in a directory that is not a Git repository, we should show a clear warning or a "Open Repository" prompt rather than just failing. Is that correct?
**Answer:** If the directory is not a Git repository, display a friendly message with options such as “Open Existing Repository” or “Initialize New Repository.”

**Q4:** Regarding Git versions, should we enforce a minimum version (e.g., 2.0+), or just warn if the version is significantly outdated?
**Answer:** Enforce a minimum Git version (for example, 2.0 and above) and show a warning if the version is significantly outdated.

**Q5:** For the UI, would you prefer a "Health Check" status icon in the main window that updates periodically, or should these environment checks primarily be a one-time splash/notification during the application boot sequence?
**Answer:** Combine both a one-time startup check and a “Health Check” status icon that is periodically updated.

**Q6:** Are there any specific environment issues you've encountered that you definitely want to include or exclude from this validation (e.g., SSH key availability, GPG signing)?
**Answer:** Include validation for SSH key availability and GPG signing support, with an option to disable advanced checks in the settings.

### Existing Code to Reference
- `git_service.py`: Contains the core logic for Git interaction and currently handles `InvalidGitRepositoryError`.
- `views/error_dialog.py`: Can be used to display actionable error messages if dependencies are missing.
- `main.py`: The entry point where the startup sequence and initial service instantiation occur.

### Follow-up Questions

**Follow-up 1:** For the "Health Check" status icon, where should it be located in the main window? (e.g., status bar, toolbar, separate tab?)
**Answer:** The Health Check icon will be placed in the status bar of the main window, with an option to open a detailed view when clicked. This location does not interrupt the workflow while still providing continuous visibility.

**Follow-up 2:** When checking for SSH/GPG availability, should these checks be blocking (prevent app usage) or just informational/warning if they fail?
**Answer:** The SSH / GPG checks will be informational only. If a check fails, a warning and explanation will be displayed, but the application will not be blocked — except for specific operations that explicitly require these capabilities.

**Follow-up 3:** For the "allow the user to define an alternative Git path" requirement: Should this persist in the `settings.json` file immediately?
**Answer:** An alternative Git path will be saved immediately to the settings.json file, with automatic reload support and the option to modify it later through the dedicated settings screen.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- **Startup Validation:**
  - Check for `git` executable in system PATH.
  - Enforce minimum Git version (2.0+).
  - Check for valid Git repository in current directory.
  - Check for Git lock files (`.git/index.lock`).
  - Check for configured user identity (`user.name`, `user.email`).
  - Check for folder permissions (read/write).
  - Check for SSH key availability (optional/informational).
  - Check for GPG signing support (optional/informational).

- **UI/UX Interactions:**
  - **Git Missing:** Blocking dialog allowing user to specify path or exit.
  - **Not a Repo:** Friendly prompt to "Open Existing" or "Initialize New".
  - **Health Check Status:** Icon in status bar, updates periodically.
  - **Detailed View:** Clickable status icon opens detailed health report.
  - **Settings Integration:** "Git Path" setting in `settings.json`, editable via UI. Option to disable advanced checks (SSH/GPG).

- **Data Management:**
  - Persist custom Git path to `settings.json`.
  - Automatic reload of Git service when path changes.

### Reusability Opportunities
- Reuse `views/error_dialog.py` for blocking errors.
- Extend `git_service.py` with new validation methods (`check_git_version`, `check_user_identity`, etc.).
- Leverage `main.py` startup sequence to inject validation logic before main window load.

### Scope Boundaries
**In Scope:**
- Git executable detection and path configuration.
- Minimum version enforcement.
- Repository validity and health checks (locks, permissions, identity).
- SSH/GPG availability checks (informational).
- Status bar health icon and detailed view.
- "Not a Repo" handling logic.

**Out of Scope:**
- Automatic installation of Git.
- Detailed troubleshooting guides (beyond basic error messages).
- Management of SSH keys or GPG keys (creation/editing) within the app.

### Technical Considerations
- **Git Interaction:** Use `subprocess` or `gitpython` to query version and config.
- **Async Checks:** Ensure periodic health checks don't freeze the UI (run in background thread if necessary).
- **Settings Schema:** Update `settings.json` structure to support `git_path` and `enable_advanced_checks`.
