# Product Roadmap

1. [ ] MVC Architectural Refactor — Decompose the monolithic `gui.py` into `views/`, `controllers/`, and `models/` to improve maintainability and testability. `L`
2. [ ] Git Dependency & Environment Check — Implement startup validation to ensure Git is installed and accessible. Add specific error catching for common Git issues. `S`
3. [x] Smart Diff Truncation & Token Management — Replace raw character slicing with token-aware truncation. Implement summarization for large files and prioritize meaningful code. `M`
4. [ ] Language Agnostic Support — Enhance `git_service` and `ai_service` to explicitly detect and handle various programming languages. Improve handling of large non-code files. `S`
5. [ ] Configuration Validation — Implement a robust schema validator for `settings.json` (or `config.json`) to prevent crashes due to corrupted or missing config. `XS`
6. [ ] Selective Staging UI — Implement a checklist-based file selector in the GUI to allow users to stage specific files for commit. `M`
7. [ ] Git Sync Workflow (Pull/Push) — Add dedicated buttons for Pull and Push operations. Include branch awareness and basic conflict detection. `M`
8. [ ] Enhanced AI Provider Support — Integrate LiteLLM to provide a unified interface for OpenAI, Claude, Gemini, and Local (Ollama) models. `M`
9. [ ] UI/UX Polish & Syntax Highlighting — Add syntax highlighting to the diff preview window and implement "Recent Repositories" management. `S`
10. [ ] Advanced Customization — Allow users to customize the AI System Prompt and commit message format via the settings UI. `S`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature