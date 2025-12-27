# Product Mission

## Pitch
AI Auto-Committer is a Windows GUI productivity tool that helps developers automate the Git commit process by providing AI-generated, meaningful commit messages and executing git commands with a single click.

## Users

### Primary Customers
- **Software Developers**: Professionals or hobbyists working in a Windows environment who want to streamline their workflow.
- **Open Source Contributors**: Users who need to make frequent, well-documented commits.

### User Personas
**The Efficient Developer** (25-45)
- **Role:** Full-stack or Backend Developer
- **Context:** Works on multiple projects, frequent context switching.
- **Pain Points:** Writing repetitive commit messages, context switching to terminal for simple git operations.
- **Goals:** Save time on administrative tasks, maintain a clean and professional commit history.

## The Problem

### Friction in Git Workflow
Writing descriptive commit messages breaks flow and takes time. Context switching between IDE and terminal for standard add/commit operations adds cognitive load. This often results in lazy commit messages like "fix" or "update".

**Our Solution:** An always-ready GUI that analyzes changes, writes the message for you using AI, and handles the git commands in one go.

## Differentiators

### Streamlined Windows Experience
Unlike command-line aliases or complex IDE plugins, we provide a dedicated, lightweight, terminal-like GUI specifically designed for the Windows environment.
This results in a frictionless, "one-click" commit experience that feels professional and native.

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
