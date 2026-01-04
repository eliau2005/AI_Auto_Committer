import threading
import os
from models.app_state import AppState

class MainController:
    def __init__(self, app_state: AppState, main_window, git_service, ai_service):
        self.state = app_state
        self.view = main_window
        self.git = git_service
        self.ai = ai_service
        
        # bind view events
        self.view.on_select_repo = self.select_directory
        self.view.on_push = self.push_repo
        self.view.on_pull = self.pull_repo
        self.view.on_settings = self.open_settings
        
        # bind sub-view events
        self.view.commit_view.on_generate = self.generate_commit_message
        self.view.commit_view.on_commit = self.perform_commit
        self.view.commit_view.on_selection_change = self.on_file_selection_change
        
    def start(self):
        # Initial checks or loads
        pass

    def select_directory(self):
        path = self.view.ask_directory()
        if path:
            self.state.repo_path = path
            self.view.update_repo_path(path)
            self.refresh_repo()

    def refresh_repo(self):
        path = self.state.repo_path
        if not path: return
        
        def _task():
            try:
                if not self.git.is_valid_repo(path):
                    self._update_ui_safe(lambda: self.view.update_branch("Invalid"))
                    self._update_ui_safe(lambda: self.view.commit_view.set_file_list([]))
                    return

                # Get branch
                # Update: git_service methods might use cwd if not passed path? 
                # gui.py passed path to is_valid, but git_service init usually sets repo? 
                # In gui.py: self.git_service = GitService(). 
                # And is_valid_repo(path) checks it.
                # But to run commands, we might need to set cwd or init repo in service.
                # Assuming GitService handles cwd or we set it. 
                # gui.py doesn't seem to set it explicitly other than os.chdir?
                # Wait, gui.py does `os.chdir(path)`? No.
                # git_service.py likely uses os.getcwd() or takes path.
                # Let's check git_service.py content if needed. 
                # For now, let's assume we need to change dir or service handles it.
                # To be safe, let's chdir if service relies on it.
                os.chdir(path)
                
                branch = self.git.get_current_branch()
                files = self.git.get_changed_files()
                
                # Update State
                self.state.current_branch = branch
                self.state.changed_files = files
                # Reset selection to all? or keep? gui.py defaulted to True.
                self.state.selected_files = set(files)
                
                # Update UI
                self._update_ui_safe(lambda: self.view.update_branch(branch))
                self._update_ui_safe(lambda: self.view.commit_view.set_file_list(files, self.state.selected_files))
                
                # Update diffs for initial selection
                self._update_diffs_for_selection()
                
            except Exception as e:
                self._update_ui_safe(lambda: self.view.show_error("Error", str(e)))
            finally:
                self._update_ui_safe(lambda: self.view.set_loading(False))

        self.view.set_loading(True, "Loading repo...")
        threading.Thread(target=_task, daemon=True).start()

    def on_file_selection_change(self, selected_files):
        self.state.selected_files = set(selected_files)
        self._update_diffs_for_selection()

    def _update_diffs_for_selection(self):
        # We need to fetch diffs for selected files.
        # This might be slow if many files, so maybe run in thread?
        # gui.py fetched one by one in tab adding.
        # Here we'll fetch for top 8 or something.
        
        # For responsiveness, let's run in thread
        selected = list(self.state.selected_files)
        
        def _task():
            # Limit to 8 for performance/display
            display_files = selected[:8]
            diff_map = {}
            for f in display_files:
                diff = self.git.get_diff(files=[f])
                diff_map[f] = diff
            
            self._update_ui_safe(lambda: self.view.diff_view.update_diffs(diff_map))
        
        threading.Thread(target=_task, daemon=True).start()

    def generate_commit_message(self):
        files = list(self.state.selected_files)
        if not files:
            self.view.show_error("No files", "Please select files.")
            return

        def _task():
            try:
                diff = self.git.get_diff(files=files)
                msg = self.ai.generate_commit_message(diff)
                
                # Parsing logic from gui.py
                msg = msg.strip()
                if msg.startswith('```'):
                    lines = msg.split('\n')
                    if lines[0].strip().startswith('```'): lines = lines[1:]
                    if lines and lines[-1].strip() == '```': lines = lines[:-1]
                    msg = '\n'.join(lines).strip()
                
                lines = msg.split('\n')
                title = lines[0].strip() if lines else ""
                desc_lines = []
                for i, line in enumerate(lines[1:], 1):
                    if i == 1 and not line.strip(): continue
                    desc_lines.append(line)
                desc = '\n'.join(desc_lines).strip()
                
                self.state.commit_title = title
                self.state.commit_description = desc
                
                self._update_ui_safe(lambda: self.view.commit_view.set_commit_message(title, desc))
                
            except Exception as e:
                self._update_ui_safe(lambda: self.view.show_error("AI Error", str(e)))
            finally:
                self._update_ui_safe(lambda: self.view.set_loading(False))

        self.view.set_loading(True, "Generating...")
        threading.Thread(target=_task, daemon=True).start()

    def perform_commit(self):
        title, desc = self.view.commit_view.get_commit_message()
        files = list(self.state.selected_files)
        
        if not files or not title:
            self.view.show_error("Incomplete", "Select files and provide a title.")
            return
            
        full_msg = f"{title}\n\n{desc}" if desc else title
        
        def _task():
            try:
                self.git.stage_files(files)
                self.git.commit_changes(full_msg)
                
                # Clear form logic?
                self._update_ui_safe(lambda: self.view.commit_view.set_commit_message("", ""))
                
                # Refresh
                self.refresh_repo() # This starts another thread/task
                
            except Exception as e:
                self._update_ui_safe(lambda: self.view.show_error("Commit Error", str(e)))
            finally:
                self._update_ui_safe(lambda: self.view.set_loading(False))
                
        self.view.set_loading(True, "Committing...")
        threading.Thread(target=_task, daemon=True).start()

    def push_repo(self):
        def _task():
            try:
                self.git.push_changes()
                self._update_ui_safe(lambda: self.view.set_status("Push complete."))
            except Exception as e:
                self._update_ui_safe(lambda: self.view.show_error("Push Error", str(e)))
            finally:
                self._update_ui_safe(lambda: self.view.set_loading(False))
        
        self.view.set_loading(True, "Pushing...")
        threading.Thread(target=_task, daemon=True).start()

    def pull_repo(self):
        def _task():
            try:
                self.git.pull_changes()
                self._update_ui_safe(lambda: self.view.set_status("Pull complete."))
                self.refresh_repo()
            except Exception as e:
                self._update_ui_safe(lambda: self.view.show_error("Pull Error", str(e)))
            finally:
                self._update_ui_safe(lambda: self.view.set_loading(False))
        
        self.view.set_loading(True, "Pulling...")
        threading.Thread(target=_task, daemon=True).start()

    def open_settings(self):
        # We pass a save callback that reloads config if needed? 
        # gui.py: on_save_callback=lambda: self.log("Configuration updated.")
        # SettingsDialog calls ai_service.reload_config().
        self.view.show_settings(self.ai, lambda: print("Config saved"))

    def _update_ui_safe(self, callback):
        self.view.after(0, callback)
