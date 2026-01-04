import sys
from unittest.mock import MagicMock

# Mock tkinter and customtkinter before importing views
sys.modules["tkinter"] = MagicMock()
sys.modules["customtkinter"] = MagicMock()

import pytest
from views.settings_dialog import SettingsDialog
from views.error_dialog import ErrorDialog

def test_error_dialog_instantiation():
    parent = MagicMock()
    # Mock winfo methods used in centering
    parent.winfo_x.return_value = 0
    parent.winfo_y.return_value = 0
    parent.winfo_width.return_value = 100
    parent.winfo_height.return_value = 100
    
    dialog = ErrorDialog(parent, "Title", "Message")
    
    # Verify title was set
    # Note: since CTkToplevel is mocked, we check the mock's calls if we want.
    # But mostly we just want to ensure it runs without error.
    assert dialog is not None

def test_settings_dialog_instantiation():
    parent = MagicMock()
    # Mock winfo methods
    parent.winfo_x.return_value = 0
    parent.winfo_y.return_value = 0
    parent.winfo_width.return_value = 100
    parent.winfo_height.return_value = 100
    
    ai_service = MagicMock()
    # Setup config mocks
    ai_service.config.get_provider.return_value = "gemini"
    ai_service.config.api_key = "123"
    ai_service.config.model_name = "flash"
    ai_service.config.get_system_prompt.return_value = "prompt"
    ai_service.config.get_theme.return_value = "Dark"
    
    dialog = SettingsDialog(parent, ai_service)
    
    assert dialog is not None
