import pytest
from unittest.mock import MagicMock, patch
from models.app_state import AppState
from controllers.main_controller import MainController

def test_app_state_truncation_property():
    state = AppState()
    assert state.truncation_warning is False
    state.truncation_warning = True
    assert state.truncation_warning is True
    
    with pytest.raises(TypeError):
        state.truncation_warning = "NotBoolean"

@patch('controllers.main_controller.threading.Thread') # Mock threading to run synchronously or just verify thread creation
def test_controller_sets_warning_on_generate(mock_thread, ):
    # Setup
    state = AppState()
    view = MagicMock()
    git = MagicMock()
    ai = MagicMock()
    
    controller = MainController(state, view, git, ai)
    
    # Mock AI response with truncation = True
    ai.generate_commit_message.return_value = ("Commit Msg", True)
    
    # Mock git diff
    git.get_diff.return_value = "diff"
    
    # Select some files
    state.selected_files = {"file.py"}
    
    # Trigger generate
    # The controller runs this in a thread. 
    # We can inspect the target function passed to thread or mock _update_ui_safe to run immediately if we extract the logic.
    # Ideally, we call the logic directly if possible, or simulate the thread execution.
    
    controller.generate_commit_message()
    
    # Get the target function passed to thread
    target = mock_thread.call_args[1]['target']
    
    # Execute the target function (the worker task)
    # The worker task calls `_update_ui_safe`.
    # We need to mock `_update_ui_safe` to execute the callback immediately or capture it.
    
    with patch.object(controller, '_update_ui_safe', side_effect=lambda cb: cb()):
        target()
    
    # Verify state updated
    assert state.truncation_warning is True
    
    # Verify view update called
    # view.diff_view.set_warning(True)
    view.diff_view.set_warning.assert_called_with(True)

@patch('controllers.main_controller.threading.Thread')
def test_controller_clears_warning_on_refresh(mock_thread):
    state = AppState()
    state.truncation_warning = True
    view = MagicMock()
    git = MagicMock()
    ai = MagicMock()
    
    controller = MainController(state, view, git, ai)
    
    # Mock git
    state.repo_path = "/tmp/repo"
    git.is_valid_repo.return_value = True
    git.get_changed_files.return_value = []
    git.get_current_branch.return_value = "main"
    
    controller.refresh_repo()
    
    target = mock_thread.call_args[1]['target']
    
    with patch.object(controller, '_update_ui_safe', side_effect=lambda cb: cb()):
        target()
        
    assert state.truncation_warning is False
    view.diff_view.set_warning.assert_called_with(False)
