# Specification: AI Auto-Committer

## Goal
Create a Windows GUI productivity tool that automates the Git commit process by detecting changes, generating professional commit messages using AI, and executing commits with a minimalist "Dark Mode" interface. The tool aims to be a "Daily Driver" by supporting the full Git cycle (Pull/Push), selective file staging, and flexible AI model options.

## User Stories
- As a developer, I want to automatically generate concise and descriptive commit messages from my code changes to save time and ensure consistency.
- As a developer, I want to review and refine the generated commit message before finalizing the commit to ensure accuracy.
- As a developer, I want to select specific files to stage so I can create atomic commits and separate concerns.
- As a developer, I want to sync my changes with the remote server (Pull/Push) directly from the tool to complete my workflow.
- As a developer, I want to use local LLMs (like Ollama) to keep my code private and avoid API costs.
- As a developer, I want a simple, dark-themed GUI to select repositories, verify status, and see my current branch at a glance.

## Specific Requirements

**GUI Implementation**
- Build a desktop application using Python with `customtkinter` (or `tkinter`) for a modern, minimalist, dark-themed interface ("Dark Mode").
- Include a "Path Input Field" and "Browse" button, plus a "Recent Projects" menu for quick access.
- Display the current active Git Branch clearly in the UI.
- Implement a "Terminal Output Window" (read-only, black bg) with syntax highlighting for diffs (Green for additions, Red for deletions).
- Implement a "File Staging Area": A list of changed files with checkboxes to allow Selective Staging.

**Git Integration**
- Use `gitpython` or `subprocess` to interact with the local git repository.
- Validate that the selected directory is a valid Git repository (check for `.git`).
- Implement `git status` checks and `git diff` extraction.
- Implement "Selective Staging": Run `git add <file>` only for checked items.
- Implement `git push` and `git pull` capabilities with a dedicated UI action (e.g., "Push" button after successful commit, or "Sync" button).

**AI Message Generation**
- Integrate with multiple AI providers: OpenAI/Claude (Cloud) and Ollama (Local).
- Allow configuration of the System Prompt to support different commit styles (e.g., Conventional Commits).
- Truncate large diffs (e.g., >4000 chars) or send file lists to avoid token limits.

**Workflow Logic**
- "Generate" interaction: Analyze changes (of checked files) -> Send to AI -> Display result in "Message Preview" area.
- "Commit" interaction: Allow user to edit the previewed message, then execute `git add` (selected) and `git commit -m "..."`.
- "Full Cycle" interaction: Offer a "Push" option after a successful commit.
- *Clarification*: Ensure the user has a chance to review the message (Explicit "Generate" vs "Commit" steps or a pause in the flow).

**Configuration Management**
- Store settings in a `config.json` or `.env` file, specifically `API_KEY` and `MODEL_NAME` (e.g., `gpt-4o-mini`).
- Allow the application to read these values on startup.

**Error Handling**
- Display clear error messages in the "Terminal Window" for: No Git Repository, No Changes detected, API Errors/Connectivity issues, and Git Lock files.

## Visual Design

*No visual assets provided in `planning/visuals`.*

**Layout Reference**
- Minimalist terminal-like aesthetic.
- Components stack: Input/Browse -> Terminal Output -> Message Preview -> Action Button(s).

## Existing Code to Leverage

*No existing application code found (New Project).* 
*Standard libraries to use:*
- `tkinter` / `customtkinter` for GUI.
- `subprocess` for shell usage.
- `json` or `dotenv` for config.

## Out of Scope
- Branch creation or merging capabilities (Viewing current branch is in scope).
- Viewing git log or history (beyond simple status).
- In-app authentication for Git (assumed pre-configured in environment).
