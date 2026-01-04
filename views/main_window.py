import customtkinter as ctk
import os
import sys
from views import styles
from views.commit_view import CommitView
from views.diff_view import DiffView
from views.settings_dialog import SettingsDialog
from views.error_dialog import ErrorDialog

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Auto-Committer")
        self.minsize(600, 500)
        
        # Icon setup
        try:
            # Assuming icon is in root or relative to main script. 
            # We'll try to find it.
            icon_path = os.path.abspath("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(default=icon_path)
        except Exception:
            pass
            
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0) # Status bar
        self.grid_columnconfigure(0, weight=1)
        
        # State placeholders for header
        self.repo_path = ctk.StringVar()
        self.status_message = ctk.StringVar(value="Ready")
        
        # Callbacks
        self.on_select_repo = None
        self.on_push = None
        self.on_pull = None
        self.on_settings = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        # --- Header ---
        header_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        self.repo_btn = ctk.CTkButton(
            header_frame, 
            text="Select Repo...", 
            command=self._on_select_repo_click,
            width=180, 
            font=styles.get_font_main(),
            fg_color="transparent",
            border_width=1,
            text_color=styles.COLOR_TEXT
        )
        self.repo_btn.pack(side="left", padx=(5, 10))
        
        self.branch_lbl = ctk.CTkButton(
            header_frame, 
            text="Branch: HEAD", 
            fg_color="transparent", 
            border_width=1, 
            border_color="gray", 
            width=120,
            hover=False,
            text_color=styles.COLOR_HEADER_BTN_TEXT,
            font=styles.get_font_branch()
        )
        self.branch_lbl.pack(side="left")
        
        self.btn_push = ctk.CTkButton(
            header_frame, 
            text="Push origin", 
            width=100, 
            command=self._on_push_click, 
            fg_color="transparent", 
            border_width=1, 
            font=styles.get_font_main(), 
            text_color=styles.COLOR_TEXT
        )
        self.btn_push.pack(side="right", padx=5)
        
        self.btn_pull = ctk.CTkButton(
            header_frame, 
            text="Fetch origin", 
            width=100, 
            command=self._on_pull_click, 
            fg_color="transparent", 
            border_width=1, 
            font=styles.get_font_main(), 
            text_color=styles.COLOR_TEXT
        )
        self.btn_pull.pack(side="right", padx=5)

        self.btn_settings = ctk.CTkButton(
            header_frame, 
            text="⚙", 
            width=30, 
            command=self._on_settings_click, 
            fg_color="transparent", 
            font=styles.get_font_main(), 
            text_color=styles.COLOR_TEXT
        )
        self.btn_settings.pack(side="right", padx=5)
        
        # --- Main Area ---
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_split.grid_rowconfigure(0, weight=1)
        main_split.grid_columnconfigure(0, minsize=320, weight=0) 
        main_split.grid_columnconfigure(1, weight=1)

        # Sidebar (Commit View)
        # We initialize it with empty callbacks, controller will assign them
        self.commit_view = CommitView(
            main_split, 
            on_generate_callback=None, 
            on_commit_callback=None
        )
        self.commit_view.grid(row=0, column=0, sticky="nsew")
        
        # Diff View
        self.diff_view = DiffView(main_split)
        self.diff_view.grid(row=0, column=1, sticky="nsew")
        
        # --- Status Bar ---
        status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color=styles.COLOR_STATUS_BAR)
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.grid_columnconfigure(1, weight=1)

        self.status_lbl = ctk.CTkLabel(
            status_bar, 
            textvariable=self.status_message, 
            font=styles.get_font_small(), 
            text_color="gray"
        )
        self.status_lbl.grid(row=0, column=0, padx=10, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_bar, height=8, width=200)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=10)
        self.progress_bar.grid_remove()

    # --- Event Handlers ---
    def _on_select_repo_click(self):
        if self.on_select_repo: self.on_select_repo()

    def _on_push_click(self):
        if self.on_push: self.on_push()

    def _on_pull_click(self):
        if self.on_pull: self.on_pull()

    def _on_settings_click(self):
        if self.on_settings: self.on_settings()

    # --- Public API ---
    def update_repo_path(self, path):
        self.repo_path.set(path)
        # Maybe update title or something?
        # Update button text to show folder name?
        if path:
            name = os.path.basename(path) or path
            self.repo_btn.configure(text=name)
        else:
            self.repo_btn.configure(text="Select Repo...")

    def update_branch(self, branch):
        self.branch_lbl.configure(text=f"Branch: {branch}")
        # Update commit button text too?
        self.commit_view.commit_btn.configure(text=f"Commit to {branch}")

    def set_loading(self, is_loading, message=""):
        if is_loading:
            self.progress_bar.grid()
            self.progress_bar.start()
            self.status_message.set(message)
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self.status_message.set(message or "Ready")
        
        self.commit_view.set_loading(is_loading)
        # Disable header buttons?
        state = "disabled" if is_loading else "normal"
        self.repo_btn.configure(state=state)
        self.btn_push.configure(state=state)
        self.btn_pull.configure(state=state)

    def show_error(self, title, message):
        ErrorDialog(self, title, message)

    def show_settings(self, ai_service, on_save_callback):
        SettingsDialog(self, ai_service, on_save_callback)

    def ask_directory(self):
        from tkinter import filedialog
        return filedialog.askdirectory()
