import pytest
from models.app_state import AppState

def test_app_state_initialization():
    """Test that AppState initializes with default values."""
    state = AppState()
    assert state.repo_path == ""
    assert state.current_branch == ""
    assert state.changed_files == []
    assert state.selected_files == set()
    assert state.commit_title == ""
    assert state.commit_description == ""
    assert state.is_loading is False

def test_app_state_updates():
    """Test that AppState methods update the state correctly."""
    state = AppState()
    
    # Update repo path
    state.repo_path = "/path/to/repo"
    assert state.repo_path == "/path/to/repo"
    
    # Update current branch
    state.current_branch = "main"
    assert state.current_branch == "main"
    
    # Update changed files
    files = ["file1.txt", "file2.py"]
    state.changed_files = files
    assert state.changed_files == files
    
    # Update selected files
    selected = {"file1.txt"}
    state.selected_files = selected
    assert state.selected_files == selected
    
    # Update commit message
    state.commit_title = "feat: add feature"
    state.commit_description = "description"
    assert state.commit_title == "feat: add feature"
    assert state.commit_description == "description"
    
    # Update loading state
    state.is_loading = True
    assert state.is_loading is True
