import pytest
from unittest.mock import MagicMock, patch
from gui import AutoCommitterApp

@pytest.fixture
def app():
    with patch('customtkinter.CTk'):
        app = AutoCommitterApp()
        # Mock services
        app.git_service = MagicMock()
        app.ai_service = MagicMock()
        return app

def test_on_browse(app):
    with patch('customtkinter.filedialog.askdirectory') as mock_ask:
        mock_ask.return_value = "/path/to/repo"
        app.git_service.is_valid_repo.return_value = True
        
        app.select_directory() # Trigger browse logic
        
        assert app.repo_path.get() == "/path/to/repo"
        app.git_service.is_valid_repo.assert_called_with("/path/to/repo")

def test_on_generate_click(app):
    app.repo_path.set("/path/to/repo")
    app.git_service.get_diff.return_value = "diff"
    app.ai_service.generate_commit_message.return_value = "msg from ai"
    
    # Mock text widget methods
    app.preview_text = MagicMock()
    
    app.generate_message()
    
    app.git_service.get_diff.assert_called()
    app.ai_service.generate_commit_message.assert_called_with("diff")
    # Verify it inserts into text widget
    app.preview_text.insert.assert_called_with("0.0", "msg from ai")

def test_on_commit_click(app):
    app.repo_path.set("/path/to/repo")
    app.preview_text = MagicMock()
    app.preview_text.get.return_value = "final msg"
    
    app.commit_changes()
    
    app.git_service.stage_all.assert_called()
    app.git_service.commit_changes.assert_called_with("final msg")
