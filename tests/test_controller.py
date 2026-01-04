import pytest
from unittest.mock import MagicMock, patch, ANY
from models.app_state import AppState
from controllers.main_controller import MainController

@pytest.fixture
def mock_deps():
    window = MagicMock()
    # Mock after to execute callback immediately
    def after_side_effect(ms, func, *args):
        func(*args)
    window.after.side_effect = after_side_effect
    
    git_service = MagicMock()
    ai_service = MagicMock()
    state = AppState()
    return window, git_service, ai_service, state

@patch('controllers.main_controller.os.chdir')
@patch('controllers.main_controller.threading.Thread')
def test_refresh_repo_flow(mock_thread, mock_chdir, mock_deps):
    window, git_service, ai_service, state = mock_deps
    
    # Configure Thread mock to run target immediately
    def side_effect(target, daemon=False):
        target()
        return MagicMock()
    mock_thread.side_effect = side_effect
    
    # Setup services
    git_service.is_valid_repo.return_value = True
    git_service.get_current_branch.return_value = "main"
    git_service.get_changed_files.return_value = ["file1.py", "file2.py"]
    git_service.get_diff.return_value = "diff"
    
    controller = MainController(state, window, git_service, ai_service)
    
    # Set initial state
    state.repo_path = "/path/to/repo"
    
    # Action
    controller.refresh_repo()
    
    # Verification
    assert state.current_branch == "main"
    assert state.changed_files == ["file1.py", "file2.py"]
    
    window.update_branch.assert_called_with("main")
    
    window.commit_view.set_file_list.assert_called()
    args, _ = window.commit_view.set_file_list.call_args
    assert args[0] == ["file1.py", "file2.py"]

@patch('controllers.main_controller.threading.Thread')
def test_generate_message_flow(mock_thread, mock_deps):
    window, git_service, ai_service, state = mock_deps
    
    def side_effect(target, daemon=False):
        target()
        return MagicMock()
    mock_thread.side_effect = side_effect
    
    state.selected_files = {"file1.py"}
    git_service.get_diff.return_value = "diff content"
    ai_service.generate_commit_message.return_value = ("feat: title\n\ndescription", False)
    
    controller = MainController(state, window, git_service, ai_service)
    
    # Action
    controller.generate_commit_message()
    
    # Verify
    ai_service.generate_commit_message.assert_called_with("diff content")
    
    # Verify view update
    window.commit_view.set_commit_message.assert_called_with("feat: title", "description")

@patch('controllers.main_controller.os.chdir')
@patch('controllers.main_controller.threading.Thread')
def test_commit_flow(mock_thread, mock_chdir, mock_deps):
    window, git_service, ai_service, state = mock_deps
    
    def side_effect(target, daemon=False):
        target()
        return MagicMock()
    mock_thread.side_effect = side_effect
    
    state.repo_path = "/path/to/repo"
    state.selected_files = {"file1.py"}
    window.commit_view.get_commit_message.return_value = ("feat: title", "description")
    
    # Mock validation
    git_service.is_valid_repo.return_value = True

    controller = MainController(state, window, git_service, ai_service)
    
    # Action
    controller.perform_commit()
    
    # Verify
    git_service.stage_files.assert_called_with(["file1.py"])
    git_service.commit_changes.assert_called_with("feat: title\n\ndescription")
    
    # Verify UI clear
    window.commit_view.set_commit_message.assert_called_with("", "")
    # Should trigger refresh
    git_service.get_current_branch.assert_called()