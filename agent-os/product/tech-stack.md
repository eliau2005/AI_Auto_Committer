# Tech Stack

### Application Runtime
- **Language:** Python 3.x
- **GUI Framework:** CustomTkinter — A modern, dark-themed wrapper around Tkinter for a professional Windows-native look.

### Git Integration
- **Library:** GitPython & Subprocess — Used for robust interaction with Git repositories and executing system commands.

### AI & API
- **AI Providers:** OpenAI, Anthropic (Claude), Google (Gemini), and Ollama (Local).
- **LLM Integration:** Direct SDKs or LiteLLM for unified access.
- **Context Management:** Tiktoken (or equivalent) for smart diff truncation and token counting.

### Architecture
- **Pattern:** MVC (Model-View-Controller) / MVVM — Decoupling UI from business logic for stability and easier testing.

### Configuration & Storage
- **Format:** JSON (`settings.json`) for persistent user preferences.
- **Validation:** Pydantic or custom schema validation for configuration integrity.

### Testing & Quality
- **Framework:** Pytest for unit and integration testing.
- **Linting:** Flake8 / Black for code style consistency.