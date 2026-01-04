import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies for import
sys.modules["tkinter"] = MagicMock()
sys.modules["customtkinter"] = MagicMock()

try:
    from views.main_window import MainWindow
    from views.error_dialog import ErrorDialog
    from controllers.main_controller import MainController
    from models.app_state import AppState
    from ai_service import AIService
    from exceptions import APIKeyError, AIServiceError
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)