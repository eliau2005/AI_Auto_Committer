# Specification: Smart Diff Truncation & Token Management

## Goal
Replace raw character slicing with token-aware truncation using `tiktoken` to ensure AI prompts stay within limits while preserving the most important code changes through intelligent prioritization and summarization.

## User Stories
- As a developer, I want the AI to prioritize logic changes over boilerplate or lock files so that generated commit messages are more accurate.
- As a developer, I want to be notified when a diff is too large and has been summarized or truncated so that I am aware the AI has incomplete context.

## Specific Requirements

**Token-Aware Counting**
- Use `tiktoken` with the `cl100k_base` encoding (compatible with most modern OpenAI and compatible models) to accurately measure context size.
- Replace all character-based string slicing in the diff processing pipeline with token-based limits.

**File Prioritization**
- Categorize files into LOGIC, CONFIG, DOCS, LOCK, and IGNORED based on extension and path patterns.
- Automatically deprioritize or exclude `tests/`, `dist/`, `vendor/`, and `node_modules/` directories by mapping them to the lowest priority category.
- Priority order (highest to lowest): LOGIC > CONFIG > DOCS > UNKNOWN > LOCK > IGNORED.

**Multi-Stage Summarization**
- When a diff exceeds the token limit (default 4000 tokens), perform summarization on "less important" categories first.
- Categories are sacrificed in order: IGNORED -> LOCK -> UNKNOWN -> DOCS -> CONFIG -> LOGIC.
- Within each category, target the largest files for summarization first to maximize token reduction.
- Summarized chunks must include a clear header (e.g., `[SUMMARIZED]`) and a brief AI-generated summary of the file's changes.

**Proportional Budgeting**
- Implement a mechanism to prevent a single large file from consuming the entire token budget when multiple files are changed.
- If the diff remains over-limit after category-based summarization, apply a per-file token cap to ensure at least a partial view of all modified files is included.

**UI Truncation Indicator**
- Display a prominent warning label (e.g., "⚠️ Some files were truncated or summarized due to size limits") in the `DiffView` when the AI context is modified.
- Ensure the indicator state is correctly managed in `AppState` and updated in the UI when diffs are refreshed or generated.

**Error Handling & Fallbacks**
- Gracefully handle `tiktoken` encoding errors or summarization API failures.
- If summarization fails or is unavailable, fall back to hard token-based truncation with a clear placeholder (e.g., `...[Remaining Diff Truncated]...`).

## Visual Design

**`planning/visuals/`**
- No visual assets provided. Use existing styling in `views/styles.py` for UI elements.

## Existing Code to Leverage

**`token_management.py`**
- Contains `TokenManager` for counting/truncating and `FilePrioritizer` for categorizing files. These should remain the single source of truth for token logic.

**`diff_processor.py`**
- Implements `DiffProcessor` which already has logic for parsing diffs and category-based sacrifice. This needs refinement for the proportional budgeting requirement.

**`ai_service.py`**
- Provides `generate_commit_message` which integrates with `DiffProcessor` and `summarize_file_diff` which provides the summarization logic.

**`views/diff_view.py`**
- Already contains a `warning_label` and `set_warning` method for visual feedback.

## Out of Scope
- Implementing support for multiple `tiktoken` encodings (e.g., `p50k_base`).
- Allowing users to manually select which files to summarize via the UI.
- Summarizing logic files if the total diff is already within the token budget.