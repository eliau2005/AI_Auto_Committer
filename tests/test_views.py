import sys
from unittest.mock import MagicMock

# Create dummy classes for ctk to allow inheritance
class MockCTk:
    def __init__(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def iconbitmap(self, *args, **kwargs): pass
    def geometry(self, *args, **kwargs): return "800x600"
    def title(self, *args, **kwargs): pass
    def minsize(self, *args, **kwargs): pass
    def mainloop(self): pass
    def after(self, *args, **kwargs): pass

class MockCTkFrame:
    def __init__(self, *args, **kwargs): 
        self.winfo_children = MagicMock(return_value=[])
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def destroy(self): pass

class MockCTkLabel:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass

class MockCTkButton:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass

class MockCTkEntry:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass
    def insert(self, *args, **kwargs): pass
    def get(self): return ""
    def configure(self, *args, **kwargs): pass

class MockCTkTextbox:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def tag_config(self, *args, **kwargs): pass
    def insert(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass
    def get(self, *args, **kwargs): return ""
    def configure(self, *args, **kwargs): pass

class MockCTkTabview:
    def __init__(self, *args, **kwargs): 
        self._tab_dict = {}
        self.tab = MagicMock(return_value=MockCTkFrame())
    def grid(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass

class MockCTkCheckBox:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass

class MockCTkProgressBar:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def start(self): pass
    def stop(self): pass
    def grid_remove(self): pass

class MockCTkOptionMenu:
    def __init__(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass

class MockCTkScrollableFrame(MockCTkFrame):
    pass

class MockCTkToplevel(MockCTk):
    def attributes(self, *args, **kwargs): pass
    def transient(self, *args, **kwargs): pass
    def grab_set(self): pass
    def update_idletasks(self): pass

# Setup the mock module
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockCTkFrame
mock_ctk.CTkLabel = MagicMock(side_effect=MockCTkLabel) # Use side_effect to return instance
mock_ctk.CTkButton = MagicMock(side_effect=MockCTkButton)
mock_ctk.CTkEntry = MagicMock(side_effect=MockCTkEntry)
mock_ctk.CTkTextbox = MagicMock(side_effect=MockCTkTextbox)
mock_ctk.CTkTabview = MagicMock(side_effect=MockCTkTabview)
mock_ctk.CTkCheckBox = MagicMock(side_effect=MockCTkCheckBox)
mock_ctk.CTkProgressBar = MagicMock(side_effect=MockCTkProgressBar)
mock_ctk.CTkOptionMenu = MagicMock(side_effect=MockCTkOptionMenu)
mock_ctk.CTkScrollableFrame = MockCTkScrollableFrame
mock_ctk.CTkToplevel = MockCTkToplevel
mock_ctk.StringVar = MagicMock(return_value=MagicMock(get=MagicMock(return_value=""), set=MagicMock()))
mock_ctk.BooleanVar = MagicMock(return_value=MagicMock(get=MagicMock(return_value=True), set=MagicMock()))
mock_ctk.CTkFont = MagicMock()
mock_ctk.set_appearance_mode = MagicMock()
mock_ctk.set_default_color_theme = MagicMock()

# Clean sys.modules to force reload of views with OUR mocks
for module in list(sys.modules.keys()):
    if module.startswith("views") or module == "customtkinter" or module == "tkinter":
        del sys.modules[module]

sys.modules["customtkinter"] = mock_ctk
sys.modules["tkinter"] = MagicMock()

import pytest
from views.main_window import MainWindow
from views.commit_view import CommitView
from views.diff_view import DiffView

def test_mainwindow_structure():
    # Instantiate MainWindow
    window = MainWindow()
    
    # Check if CommitView and DiffView are created
    assert hasattr(window, "commit_view")
    assert hasattr(window, "diff_view")
    
    assert isinstance(window.commit_view, CommitView)
    assert isinstance(window.diff_view, DiffView)

def test_mainwindow_api():
    window = MainWindow()
    
    # Re-inject MagicMocks into the window instance for the widgets we want to test
    window.repo_btn = MagicMock()
    window.branch_lbl = MagicMock()
    window.commit_view.commit_btn = MagicMock()
    window.progress_bar = MagicMock()
    
    # Test update_repo_path
    window.update_repo_path("/path/to/repo")
    window.repo_btn.configure.assert_called_with(text="repo")
    
    # Test update_branch
    window.update_branch("main")
    window.branch_lbl.configure.assert_called_with(text="Branch: main")
    window.commit_view.commit_btn.configure.assert_called_with(text="Commit to main")
    
    # Test set_loading
    window.set_loading(True, "Working...")
    window.progress_bar.grid.assert_called()
    
    window.set_loading(False)
    window.progress_bar.stop.assert_called()
