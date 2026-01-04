import pytest
import os
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch
from git import Repo
from models.app_state import AppState
from controllers.main_controller import MainController
from git_service import GitService

@pytest.fixture
def temp_git_repo():
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)
    
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("Initial")
    
    repo.index.add([file_path])
    repo.index.commit("Initial commit")
    
    with open(file_path, "w") as f:
        f.write("Modified")
        
    repo.close()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@patch('controllers.main_controller.threading.Thread')
def test_mvc_full_flow(mock_thread, temp_git_repo):
    # Use real GitService
    git_service = GitService()
    
    # Mock AIService
    ai_service = MagicMock()
    ai_service.generate_commit_message.return_value = ("feat: integration test\n\ndetails", False)
    
    # Mock View
    window = MagicMock()
    # Mock after to run immediately
    def after_side_effect(ms, func, *args):
        func(*args)
    window.after.side_effect = after_side_effect
    
    # Mock ask_directory to return temp repo
    window.ask_directory.return_value = temp_git_repo
    
    # Mock View sub-components
    window.commit_view = MagicMock()
    window.commit_view.get_commit_message.return_value = ("feat: integration test", "details")
    window.diff_view = MagicMock()
    
    # State
    state = AppState()
    
    # Controller
    controller = MainController(state, window, git_service, ai_service)
    
    # Mock threading to run sync, respecting args
    def side_effect(*args, **kwargs):
        target = kwargs.get('target')
        t_args = kwargs.get('args', ())
        t_kwargs = kwargs.get('kwargs', {})
        
        if target:
            target(*t_args, **t_kwargs)
        return MagicMock()
    
    mock_thread.side_effect = side_effect
    
    # 1. Select Directory
    controller.select_directory() # calls ask_directory -> returns temp_git_repo
    
    # Check for errors
    if window.show_error.called:
        args, _ = window.show_error.call_args
        pytest.fail(f"Show error called with: {args}")

    assert state.repo_path == temp_git_repo
    assert state.current_branch != "", f"Branch is empty. Valid repo: {git_service.is_valid_repo(temp_git_repo)}"
    assert "test.txt" in state.changed_files
    
    # 2. Generate Message
    controller.generate_commit_message()
    
    assert state.commit_title == "feat: integration test"
    
    # 3. Perform Commit
    controller.perform_commit()
    
    # Verify via Git
    repo = Repo(temp_git_repo)
    assert repo.head.commit.message.strip() == "feat: integration test\n\ndetails"
    assert not repo.is_dirty()
    repo.close()