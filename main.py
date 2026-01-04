from models.app_state import AppState
from views.main_window import MainWindow
from controllers.main_controller import MainController
from git_service import GitService
from ai_service import AIService
import sys

def main():
    print("Starting AI Auto-Committer (MVC)...")
    
    # Initialize Services
    try:
        git_service = GitService()
        ai_service = AIService()
    except Exception as e:
        print(f"Error initializing services: {e}")
        sys.exit(1)
        
    # Initialize Model
    app_state = AppState()
    
    # Initialize View
    # Note: MainWindow init doesn't require arguments now
    app = MainWindow()
    
    # Initialize Controller
    # Controller binds itself to the view events
    controller = MainController(app_state, app, git_service, ai_service)
    
    # Start (load initial state, etc)
    controller.start()
    
    # Start Event Loop
    app.mainloop()

if __name__ == "__main__":
    main()