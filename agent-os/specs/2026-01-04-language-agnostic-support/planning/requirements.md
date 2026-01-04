# Spec Requirements: Language Agnostic Support

## Initial Description
Enhance `git_service` and `ai_service` to explicitly detect and handle various programming languages. Improve handling of large non-code files.

## Requirements Discussion

### First Round Questions

**Q1:** Language Detection Strategy: Extension-based vs Content-based?
**Answer:** Extension-based detection is fully acceptable and preferred for performance.

**Q2:** Handling Non-Code/Binary Files?
**Answer:** Exclude content of binary/large files. Provide filename and short status (e.g., "Image file updated") to prevent noise.

**Q3:** Threshold for "Large" Files?
**Answer:** 100KB threshold for text files. Above this, summarize or exclude.

**Q4:** AI Prompt Context: Explicit language headers?
**Answer:** Yes, explicitly state the language and group changes by language to improve AI understanding.

**Q5:** UI Indicators?
**Answer:** Display detected language in UI.

**Q6:** Lock Files?
**Answer:** Special handling for lock files (summarize as "Dependency lock file updated").

### Existing Code to Reference

**Similar Features Identified:**
- `diff_processor.py`: Existing `DiffChunk` class, `FileCategory` enum, and `FilePrioritizer` class.
- `views/`: Existing UI components to be updated with badges.

### Follow-up Questions

**Q1:** Icons Implementation?
**Answer:** Option C: Use a text badge (e.g., `[PY]`, `[JS]`) using existing UI styling.

**Q2:** Lock File Scope?
**Answer:** (Implied Yes/Standard) Include `package-lock.json`, `yarn.lock`, `poetry.lock`, `Pipfile.lock`, `Cargo.lock`, `composer.lock`, `go.sum`.

**Q3:** Reusability/Architecture (Enum vs Attribute)?
**Answer:** (Architectural Decision) Keep `FileCategory` high-level and add a separate `language` attribute to `DiffChunk` to maintain separation of concerns.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
- **Badge Style:** Text-based badges `[PY]`, `[JS]` to be integrated into the file list.
- **Consistency:** Must match existing dark theme and UI font styles.

## Requirements Summary

### Functional Requirements
- **Language Detection:**
  - Implement extension-to-language mapping (e.g., `.py` -> Python, `.rs` -> Rust).
  - Fallback to "Text" or "Binary" for unknown types.
- **Smart Truncation & Filtering:**
  - **Binary Files:** Never send content. Send `[Binary file updated]`.
  - **Large Text Files (>100KB):** Send `[Large file updated - content omitted]`.
  - **Lock Files:** Detect standard lock files and send `[Dependency lock file updated]`.
- **AI Prompt Construction:**
  - Group diff chunks by language in the prompt.
  - Add explicit headers: `## Python Changes`, `## JavaScript Changes`.
- **UI Updates:**
  - Add a text badge (e.g., `[PY]`) next to the filename in the staging/diff view.

### Reusability Opportunities
- **DiffProcessor:** Extend the `parse_diff` method to populate the new `language` attribute.
- **FilePrioritizer:** Logic here can be augmented or referenced for the "Large/Binary" checks.

### Scope Boundaries
**In Scope:**
- Updating `diff_processor.py` logic.
- Updating `ai_service.py` prompt generation.
- Updating `views/` to render badges.
- Supporting common languages (Python, JS/TS, Rust, Go, Java, C++, C#, PHP, Ruby).
- Supporting common lock files.

**Out of Scope:**
- Content-based language detection (shebang parsing).
- Syntax highlighting in the diff view (this is a separate roadmap item).
- Complex custom language mapping configuration (hardcoded map is fine for now).

### Technical Considerations
- **Performance:** Extension checks are O(1) and fast.
- **Architecture:** 
  - `DiffChunk` dataclass gets `language: str` field.
  - `FileCategory` remains for semantic priority (Logic vs Docs vs Config).
  - New `LanguageDetector` service or helper class might be useful to keep logic clean.
