# Spec Requirements: Smart Diff Truncation & Token Management

## Initial Description
Replace raw character slicing with token-aware truncation. Implement summarization for large files and prioritize meaningful code.

## Requirements Discussion

### First Round Questions

**Q1:** I assume we should use `tiktoken` as the primary library for token counting, as mentioned in the tech stack. Is that correct, or would you prefer a more provider-agnostic approach like LiteLLM's token counting?
**Answer:** all correct (Confirming `tiktoken`)

**Q2:** For very large diffs that still exceed token limits after intelligent truncation, I'm thinking of summarizing the less critical parts (like boilerplate or large data changes) while keeping the core logic changes intact. Should we implement a multi-stage process where the AI first summarizes the "less important" files?
**Answer:** all correct

**Q3:** I'm assuming "prioritizing meaningful code" means keeping changes in logic files (e.g., `.py`, `.js`, `.ts`) and truncating or summarizing changes in configuration, documentation, or large lock files (e.g., `package-lock.json`, `poetry.lock`). Is this the priority order you had in mind?
**Answer:** all correct

**Q4:** How should the system handle multiple files in a single commit? I assume we should distribute the token budget proportionally across files, or perhaps prioritize files with more significant changes. Should we set a per-file token limit?
**Answer:** all correct

**Q5:** When truncation occurs, should we provide a visual indicator in the UI (e.g., a badge or warning) letting the user know the AI is working with a partial diff?
**Answer:** all correct

**Q6:** Are there any specific file types or directory patterns (e.g., `tests/`, `dist/`, `vendor/`) that should always be prioritized for truncation or exclusion from the AI context?
**Answer:** all correct

### Existing Code to Reference
**Similar Features Identified:**
- Feature: Basic Truncation - Path: `ai_service.py`
- Components to potentially reuse: `DiffView` in `views/diff_view.py` for displaying warnings.
- Backend logic to reference: `generate_commit_message` in `ai_service.py`.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Implement token-aware counting using `tiktoken`.
- Intelligent truncation prioritizing logic files over lock files, documentation, and configuration.
- Multi-stage summarization for very large diffs where "less important" files are summarized before being sent in the final prompt.
- Proportional token budget distribution across multiple files in a commit.
- Visual indicator (badge/warning) in the UI when the AI context is truncated or summarized.
- Explicitly prioritize truncation/exclusion for `tests/`, `dist/`, and `vendor/` directories.

### Reusability Opportunities
- Use `Tiktoken` as planned in the tech stack.
- Enhance `ai_service.py` with the new logic.
- Extend `views/diff_view.py` or `views/main_window.py` for the truncation status UI.

### Scope Boundaries
**In Scope:**
- Token-aware truncation logic.
- File-priority management.
- Multi-stage summarization process.
- UI indicator for truncation status.

**Out of Scope:**
- Changing the AI provider logic (handled by other tasks).
- Full syntax highlighting (handled by a separate roadmap item).

### Technical Considerations
- Integration with `tiktoken`.
- Handling different models (GPT-4 vs others might need different encoders, though `cl100k_base` is common).
- Performance overhead of multi-stage summarization (extra API calls).
