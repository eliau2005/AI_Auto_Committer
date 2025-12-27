# Specification: AI Auto-Committer

## Goal
Create a Windows GUI productivity tool that automates the Git commit process by detecting changes, generating professional commit messages using AI, and executing commits with a minimalist "Dark Mode" interface.

## User Stories
- As a developer, I want to automatically generate concise and descriptive commit messages from my code changes to save time and ensure consistency.
- As a developer, I want to review and refine the generated commit message before finalizing the commit to ensure accuracy.
- As a developer, I want a simple, dark-themed GUI to select repositories and verify status without using complex terminal commands.

## Specific Requirements

**GUI Implementation**
- Build a desktop application using Python with `customtkinter` (or `tkinter`) for a modern, minimalist, dark-themed interface ("Dark Mode").
- Include a "Path Input Field" and "Browse" button to select and display the target local Git repository path.
- Implement a "Terminal Output Window" (read-only, black bg, green/white text) to display Git command outputs and status messages.

**Git Integration**
- Use `gitpython` or `subprocess` to interact with the local git repository.
- Validate that the selected directory is a valid Git repository (check for `.git`).
- Implement `git status` checks and `git diff` extraction (both staged and unstaged changes) for the AI prompt.

**AI Message Generation**
- Integrate with an AI provider (e.g., OpenAI/Claude) via `requests` or an official SDK.
- Use a system prompt that enforces: short summary (<50 chars), one empty line, and a concise bulleted list of changes in present tense.
- Truncate large diffs (e.g., >4000 chars) or send file lists to avoid token limits.

**Workflow Logic**
- "Generate" interaction: Analyze changes -> Send to AI -> Display result in "Message Preview" area.
- "Commit" interaction: Allow user to edit the previewed message, then execute `git add .` and `git commit -m "..."` upon confirmation.
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
- Pushing commits to a remote repository (`git push`).
- Branch creation, switching, or merging capabilities.
- Viewing git log or history.
- Staging individual files (tool will run `git add .`).
- In-app authentication for Git (assumed pre-configured in environment).
