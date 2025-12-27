# Product Mission

## Pitch
AI Auto-Committer is a robust Windows GUI productivity tool designed to be your daily driver for Git operations. It streamlines the entire workflow—from selective staging and AI-generated commit messages to syncing with remote repositories—all within a modern, minimalist interface.

## Users

### Primary Customers
- **Software Developers**: Professionals or hobbyists working in a Windows environment who want to streamline their workflow.
- **Open Source Contributors**: Users who need to make frequent, well-documented commits.

### User Personas
**The Efficient Developer** (25-45)
- **Role:** Full-stack or Backend Developer
- **Context:** Works on multiple projects, frequent context switching.
- **Pain Points:** Writing repetitive commit messages, context switching to terminal for simple git operations, managing partial commits.
- **Goals:** Save time on administrative tasks, maintain a clean and professional commit history, stay in flow.

## The Problem

### Friction in Git Workflow
Writing descriptive commit messages breaks flow and takes time. Context switching between IDE and terminal for standard add/commit/push operations adds cognitive load. This often results in lazy commit messages or "wip" commits. Furthermore, staging specific files often requires tedious command-line work or complex GUI tools that feel bloated.

**Our Solution:** An always-ready, lightweight GUI that not only writes messages for you but handles the full cycle—staging, committing, pushing, and pulling—with precision and ease.

## Differentiators

### Streamlined "Daily Driver" Experience
Unlike command-line aliases or complex IDE plugins, we provide a dedicated, lightweight, terminal-like GUI specifically designed for the Windows environment. We prioritize speed and focus, offering "just enough" control (like selective staging and branch awareness) without the bloat of full-featured Git clients.
This results in a frictionless experience that feels professional and native.

## Key Features

### Core Features
- **Smart Change Detection:** Automatically detects changes in the selected repository (`git diff`).
- **One-Click Commit:** Executes `git add` and `git commit` seamlessly.
- **Terminal-Style GUI:** A minimalist, dark-themed interface that fits the developer aesthetic.

### AI Features
- **AI Message Generation:** Uses LLMs (OpenAI/Claude) to write concise, professional commit messages based on actual code changes.
- **Message Preview:** Allows users to review and edit the generated message before committing.

### Advanced Features
- **Git Repository Validation:** Ensures operations are only performed on valid repositories.
- **Smart Diff Handling:** Manages large diffs intelligently to stay within API limits.
