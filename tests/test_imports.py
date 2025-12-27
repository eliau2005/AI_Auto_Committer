import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui import AutoCommitterApp, ErrorDialog
    from ai_service import AIService
    from exceptions import APIKeyError, AIServiceError
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
