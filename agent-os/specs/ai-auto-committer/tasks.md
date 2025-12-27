# Task Breakdown: AI Auto-Committer

## Overview
Total Tasks: 15

## Task List

### Configuration & Core

#### Task Group 1: Setup & Configuration
**Dependencies:** None

- [x] 1.0 Complete Setup & Config
  - [x] 1.1 Write 2-4 focused tests for Configuration loading
    - Test loading from `.env` or `config.json`
    - Test missing config file handling
    - Test default values
  - [x] 1.2 Create Project Structure & Dependency Setup
    - Initialize Python project
    - Create `requirements.txt` (customtkinter, gitpython, openai/requests, python-dotenv)
    - Create main entry point `main.py`
  - [x] 1.3 Implement Configuration Manager
    - Create `config.py` module
    - Implement loading `API_KEY` and `MODEL_NAME`
    - simple validation of keys
  - [x] 1.4 Ensure Config tests pass
    - Run ONLY the 2-4 tests written in 1.1

**Acceptance Criteria:**
- Project structure created
- Dependencies installable
- Config loads correctly from file
- Tests pass

### Backend Logic (Git & AI)

#### Task Group 2: Git Integration Service
**Dependencies:** Task Group 1

- [x] 2.0 Complete Git Integration
  - [x] 2.1 Write 3-5 focused tests for Git operations (mocked)
    - Test detecting valid/invalid git repo
    - Test parsing `git status` output
    - Test `git commit` command construction
  - [x] 2.2 Implement GitService class
    - wrapper around `gitpython` or `subprocess`
    - `is_valid_repo(path)`
    - `get_status(path)`
    - `get_diff(path)` (handle staged + unstaged)
  - [x] 2.3 Implement Commit functions
    - `stage_all(path)` (`git add .`)
    - `commit_changes(path, message)`
  - [x] 2.4 Ensure Git Service tests pass
    - Run ONLY the 3-5 tests written in 2.1

**Acceptance Criteria:**
- Can detect git repos
- Can extract diffs
- Can execute add/commit commands
- Tests pass

#### Task Group 3: AI Message Generation Service
**Dependencies:** Task Group 2

- [x] 3.0 Complete AI Service
  - [x] 3.1 Write 2-4 focused tests for AI Service (mocked response)
    - Test prompt construction
    - Test API call error handling
    - Test response parsing
  - [x] 3.2 Implement AIService class
    - Integration with OpenAI/Claude API
    - Implement `generate_commit_message(diff_text)`
  - [x] 3.3 Implement Prompt Logic
    - Construct system prompt as per spec
    - Implement truncation logic for large diffs (>4000 chars)
  - [x] 3.4 Ensure AI Service tests pass
    - Run ONLY the 2-4 tests written in 3.1

**Acceptance Criteria:**
- Correctly formats prompts
- Handles API errors gracefully
- Returns message string from mocked API
- Tests pass

### Frontend (GUI)

#### Task Group 4: User Interface Implementation
**Dependencies:** Task Group 3

- [x] 4.0 Complete GUI
  - [x] 4.1 Write 2-4 focused tests for UI Logic (if possible, or plan manual)
    - Test state updates (e.g. updating path variable)
    - Test event handlers (button clicks triggers service)
  - [x] 4.2 Create Main Window & Layout
    - Setup `customtkinter` window
    - Apply Dark Mode / Theme
    - Grid/Pack layout structure
  - [x] 4.3 Implement Directory Selection
    - Path Input Field (Entry)
    - Browse Button (FileDialog)
    - Validation logic on selection (calls `GitService.is_valid_repo`)
  - [x] 4.4 Implement Terminal & Preview Areas
    - Read-only Textbox for logs (Terminal)
    - Editable Textbox for Message Preview
  - [x] 4.5 Implement Action Buttons & Wiring
    - "Generate & Commit" button
    - Connect button to:
      1. `GitService.get_diff`
      2. `AIService.generate`
      3. Update Preview
      4. (On confirm/second click? Or single flow?) - Wait, spec says "Generate & Commit" triggers full process BUT "Message Preview... allowing user to refine".
      - *Refined Logic*: Button "Generate" -> Populates Preview. Button "Commit" -> Executes commit.
      - Let's implement distinct "Generate" vs "Commit" or a two-step flow as per spec "User Flow" Phase C.
      - Impl logic: Generate button -> Preview. Commit Button (enabled after generate) -> Commit.
  - [x] 4.6 Ensure UI tests pass / Manual Verify
    - Verify layout matches description
    - Verify buttons trigger correct console logs (mocked backend)

**Acceptance Criteria:**
- Application launches
- Can select directory
- Visuals match "Dark Mode" terminal aesthetic
- Buttons trigger backend logic

### Testing & Verification

#### Task Group 5: Integration & Gap Analysis
**Dependencies:** Task Groups 1-4

- [x] 5.0 Review and Fill Gaps
  - [x] 5.1 Manual End-to-End Verification
    - Run app against a dummy git repo
    - Verify `git add .` and `git commit` actually happened
    - Verify AI response (using real or mock key)
  - [x] 5.2 Error Handling Verification
    - Test "No Git Repo" scenario
    - Test "No Changes" scenario
    - Test "API Error"
  - [x] 5.3 Polish & Packaging (Optional)
    - Add icon
    - Final code cleanup

**Acceptance Criteria:**
- Full user flow works (Select -> Generate -> Commit)
- All error cases handled gracefully in UI
- No critical bugs

## Execution Order

Recommended implementation sequence:
1. Setup & Config
2. Backend (Git Service)
3. Backend (AI Service)
4. Frontend (GUI)
5. Integration Verification
