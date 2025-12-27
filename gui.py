import customtkinter as ctk
from tkinter import filedialog, END
import threading
from git_service import GitService
from ai_service import AIService
from exceptions import APIKeyError, AIServiceError, NetworkError

# --- Configuration & Constants ---
FONT_MAIN = ("Segoe UI", 14)
FONT_HEADER = ("Segoe UI", 18, "bold")
FONT_MONO = ("Consolas", 13)
PADDING_STD = 15
PADDING_INNER = 10
COLOR_ERROR = "#ef5350"  # Soft red
COLOR_SUCCESS = "#66bb6a" # Soft green

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x250")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Message area expands
        
        # Center the window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()
        
        # Title
        lbl_title = ctk.CTkLabel(
            self, 
            text=title, 
            font=FONT_HEADER, 
            text_color=COLOR_ERROR
        )
        lbl_title.grid(row=0, column=0, padx=PADDING_STD, pady=(PADDING_STD, PADDING_INNER), sticky="ew")
        
        # Message (Scrollable if long)
        msg_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        msg_frame.grid(row=1, column=0, padx=PADDING_STD, pady=PADDING_INNER, sticky="nsew")
        
        lbl_msg = ctk.CTkLabel(
            msg_frame, 
            text=message, 
            font=FONT_MAIN,
            wraplength=380,
            justify="left"
        )
        lbl_msg.pack(fill="both", expand=True)
        
        # Dismiss Button
        btn = ctk.CTkButton(
            self, 
            text="Dismiss", 
            command=self.destroy, 
            font=FONT_MAIN,
            fg_color=COLOR_ERROR, 
            hover_color="#d32f2f",
            height=40
        )
        btn.grid(row=2, column=0, padx=PADDING_STD, pady=PADDING_STD, sticky="ew")

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, ai_service, on_save_callback=None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x450")
        self.grid_columnconfigure(0, weight=1)
        
        self.ai_service = ai_service
        self.on_save_callback = on_save_callback
        
        # Center the window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 225
        self.geometry(f"+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()

        # Canvas for layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_STD, pady=PADDING_STD)
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkLabel(main_frame, text="Configuration", font=FONT_HEADER, anchor="w")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_STD))

        # Provider
        lbl_prov = ctk.CTkLabel(main_frame, text="AI Provider", font=FONT_MAIN, anchor="w")
        lbl_prov.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.provider_var = ctk.StringVar(value=self.ai_service.config.get_provider())
        self.provider_menu = ctk.CTkOptionMenu(
            main_frame, 
            values=["gemini", "ollama", "openai"],
            variable=self.provider_var,
            font=FONT_MAIN,
            height=40
        )
        self.provider_menu.grid(row=2, column=0, sticky="ew", pady=(0, PADDING_STD))

        # API Key
        key_label = ctk.CTkLabel(main_frame, text="API Key (Optional for Ollama)", font=FONT_MAIN, anchor="w")
        key_label.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        self.key_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter API Key", height=40, font=FONT_MAIN)
        self.key_entry.grid(row=4, column=0, sticky="ew", pady=(0, PADDING_STD))
        if self.ai_service.config.api_key and self.ai_service.config.api_key != "ollama":
            self.key_entry.insert(0, self.ai_service.config.api_key)

        # Model Name
        model_label = ctk.CTkLabel(main_frame, text="Model Name", font=FONT_MAIN, anchor="w")
        model_label.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        
        self.model_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g. gemini-2.0-flash", height=40, font=FONT_MAIN)
        self.model_entry.grid(row=6, column=0, sticky="ew", pady=(0, PADDING_STD))
        if self.ai_service.config.model_name:
            self.model_entry.insert(0, self.ai_service.config.model_name)
            
        # System Prompt
        prompt_label = ctk.CTkLabel(main_frame, text="Custom System Prompt (Optional)", font=FONT_MAIN, anchor="w")
        prompt_label.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        
        self.prompt_entry = ctk.CTkEntry(main_frame, placeholder_text="Override default prompt...", height=40, font=FONT_MAIN)
        self.prompt_entry.grid(row=8, column=0, sticky="ew", pady=(0, PADDING_STD*2))
        current_prompt = self.ai_service.config.get_system_prompt()
        if current_prompt:
             self.prompt_entry.insert(0, current_prompt)

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=9, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(1, weight=1) # Spacer
        
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            command=self.destroy, 
            fg_color="transparent", 
            border_width=1, 
            font=FONT_MAIN,
            height=40,
            width=100
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save Configuration", 
            command=self.save_config, 
            fg_color=COLOR_SUCCESS, 
            hover_color="#388e3c",
            font=FONT_MAIN,
            height=40,
            width=150
        )
        save_btn.grid(row=0, column=2)

    def save_config(self):
        new_key = self.key_entry.get().strip()
        new_model = self.model_entry.get().strip()
        provider = self.provider_var.get()
        prompt = self.prompt_entry.get().strip()
        
        if provider != "ollama" and not new_key:
            self.key_entry.configure(border_color=COLOR_ERROR)
            return
            
        self.ai_service.config.update_credentials(new_key, new_model)
        self.ai_service.config.set_provider(provider)
        self.ai_service.config.set_system_prompt(prompt if prompt else None)
        self.ai_service.reload_config()
        
        if self.on_save_callback:
            self.on_save_callback()
            
        self.destroy()

class AutoCommitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Auto-Committer")
        self.geometry("1000x800")
        self.minsize(800, 600)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.git_service = GitService()
        self.ai_service = AIService()
        
        self.repo_path = ctk.StringVar()
        self.current_branch = ctk.StringVar(value="HEAD")
        self.selected_files = [] # List of full paths or relative paths
        self.file_vars = {} # Map path -> BooleanVar
        
        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Path & Toolbar
        self.grid_rowconfigure(1, weight=1) # Main Content (Split view?) -> Staging | Editor
        
        self._setup_ui()
        
        # Check API Key on startup
        self.after(100, self.check_api_key)
        self.after(200, self.load_recent_repos)

    def _setup_ui(self):
        # --- 1. Top Bar ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_STD, pady=PADDING_STD)
        top_frame.grid_columnconfigure(1, weight=1) # Entry expands

        # Recent Repos Dropdown (Initially empty, populated later)
        self.recent_menu = ctk.CTkOptionMenu(
            top_frame,
            values=["Select Repo..."],
            command=self.on_recent_repo_select,
            width=150,
            font=FONT_MAIN
        )
        self.recent_menu.grid(row=0, column=0, padx=(0, 10))

        self.path_entry = ctk.CTkEntry(
            top_frame, 
            textvariable=self.repo_path, 
            placeholder_text="Select Repository Path...",
            font=FONT_MAIN,
            height=35
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            top_frame, text="Browse", width=80, height=35,
            command=self.select_directory, font=FONT_MAIN
        )
        browse_btn.grid(row=0, column=2, padx=(0, 10))

        settings_btn = ctk.CTkButton(
            top_frame, text="⚙", width=40, height=35,
            command=self.open_settings, font=FONT_MAIN
        )
        settings_btn.grid(row=0, column=3, padx=(0, 10))

        # --- 2. Action Toolbar (Push/Pull/Branch) ---
        toolbar_frame = ctk.CTkFrame(self, height=40)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_STD, pady=(0, PADDING_STD))
        
        lbl_branch = ctk.CTkLabel(toolbar_frame, text="Branch:", font=FONT_MAIN, text_color="gray")
        lbl_branch.pack(side="left", padx=(10, 5))
        
        lbl_current_branch = ctk.CTkLabel(toolbar_frame, textvariable=self.current_branch, font=("Consolas", 14, "bold"))
        lbl_current_branch.pack(side="left", padx=(0, 20))
        
        self.btn_pull = ctk.CTkButton(toolbar_frame, text="⬇ Pull", width=80, command=self.pull_repo, fg_color="#455a64")
        self.btn_pull.pack(side="left", padx=5, pady=5)
        
        self.btn_push = ctk.CTkButton(toolbar_frame, text="⬆ Push", width=80, command=self.push_repo, fg_color="#455a64")
        self.btn_push.pack(side="left", padx=5, pady=5)
        
        self.btn_refresh = ctk.CTkButton(toolbar_frame, text="⟳ Refresh", width=90, command=self.refresh_status, fg_color="#00897b")
        self.btn_refresh.pack(side="right", padx=10, pady=5)

        # --- 3. Main Split Area ---
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.grid(row=2, column=0, sticky="nsew", padx=PADDING_STD, pady=(0, PADDING_STD))
        split_frame.grid_columnconfigure(0, weight=1) # Staging
        split_frame.grid_columnconfigure(1, weight=2) # Editor
        split_frame.grid_rowconfigure(0, weight=1)

        # Left: Staging Area
        staging_frame = ctk.CTkFrame(split_frame)
        staging_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        lbl_stage = ctk.CTkLabel(staging_frame, text="Changes", font=FONT_HEADER)
        lbl_stage.pack(padx=10, pady=5, anchor="w")
        
        self.file_list_frame = ctk.CTkScrollableFrame(staging_frame, fg_color="transparent")
        self.file_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right: Editor & Output
        right_col = ctk.CTkFrame(split_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(3, weight=1) # Terminal expands

        # Title
        self.title_entry = ctk.CTkEntry(right_col, placeholder_text="Commit Title", font=FONT_MAIN, height=40)
        self.title_entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Desc
        self.desc_text = ctk.CTkTextbox(right_col, font=FONT_MONO, height=120)
        self.desc_text.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Buttons
        btns_row = ctk.CTkFrame(right_col, fg_color="transparent")
        btns_row.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        btns_row.grid_columnconfigure(0, weight=1)
        
        self.gen_btn = ctk.CTkButton(btns_row, text="✨ Generate", command=self.generate_message_thread, height=40, width=120, fg_color="#5c6bc0")
        self.gen_btn.pack(side="left", padx=(0, 10))
        
        self.commit_btn = ctk.CTkButton(btns_row, text="✓ Commit Selected", command=self.commit_changes, height=40, width=150, fg_color=COLOR_SUCCESS)
        self.commit_btn.pack(side="left")

        # Terminal
        self.terminal_text = ctk.CTkTextbox(right_col, fg_color="#1e1e1e", text_color="#00e676", font=("Consolas", 12))
        self.terminal_text.grid(row=3, column=0, sticky="nsew")
        self.terminal_text.configure(state="disabled")

        # Tags for syntax highlighting
        self.terminal_text.tag_config("diff_add", foreground="#66bb6a")
        self.terminal_text.tag_config("diff_rem", foreground="#ef5350")
        self.terminal_text.tag_config("info", foreground="#90caf9")
        self.terminal_text.tag_config("error", foreground=COLOR_ERROR)

    def log(self, message, tag=None):
        self.terminal_text.configure(state="normal")
        if tag:
            self.terminal_text.insert(END, f"> {message}\n", tag)
        else:
            self.terminal_text.insert(END, f"> {message}\n")
        self.terminal_text.see(END)
        self.terminal_text.configure(state="disabled")

    def log_diff_line(self, line):
        self.terminal_text.configure(state="normal")
        if line.startswith("+") and not line.startswith("+++"):
            self.terminal_text.insert(END, line + "\n", "diff_add")
        elif line.startswith("-") and not line.startswith("---"):
            self.terminal_text.insert(END, line + "\n", "diff_rem")
        else:
            self.terminal_text.insert(END, line + "\n")
        self.terminal_text.see(END)
        self.terminal_text.configure(state="disabled")

    def show_diff_preview(self, diff_text):
        self.terminal_text.configure(state="normal")
        self.terminal_text.delete("1.0", END)
        self.terminal_text.configure(state="disabled")
        for line in diff_text.splitlines():
            self.log_diff_line(line)

    def load_recent_repos(self):
        repos = self.ai_service.config.get_recent_repos()
        if repos:
            # prepend placeholder
            options = ["Select Repo..."] + repos
            self.recent_menu.configure(values=options)
            # If path entry is empty but we have recents, maybe don't auto-load, just let user pick.

    def on_recent_repo_select(self, choice):
        if choice and choice != "Select Repo...":
            self.repo_path.set(choice)
            self.refresh_status()

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path.set(path)
            self.ai_service.config.add_recent_repo(path)
            self.load_recent_repos()
            self.refresh_status()

    def refresh_status(self):
        path = self.repo_path.get()
        if not path: return
        
        if not self.git_service.is_valid_repo(path):
            self.log("Invalid Repository", "error")
            self.current_branch.set("Invalid")
            self._clear_staging()
            return
            
        self.current_branch.set(self.git_service.get_current_branch())
        self.log(f"Repo loaded: {path}", "info")
        self._refresh_file_list()

    def _clear_staging(self):
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        self.file_vars = {}

    def _refresh_file_list(self):
        self._clear_staging()
        files = self.git_service.get_changed_files()
        
        if not files:
            lbl = ctk.CTkLabel(self.file_list_frame, text="No changes", text_color="gray")
            lbl.pack(pady=10)
            return

        for f in files:
            var = ctk.BooleanVar(value=True) # Default checked
            self.file_vars[f] = var
            chk = ctk.CTkCheckBox(self.file_list_frame, text=f, variable=var, font=("Segoe UI", 12))
            chk.pack(anchor="w", pady=2)
            
    def get_selected_files(self):
        return [f for f, var in self.file_vars.items() if var.get()]

    def pull_repo(self):
        path = self.repo_path.get()
        if not path: return
        try:
            self.log("Pulling changes...", "info")
            self.git_service.pull_changes()
            self.log("Pull complete.", "info")
            self.refresh_status()
        except Exception as e:
            self.log(f"Pull failed: {e}", "error")
            self.show_error("Pull Failed", str(e))

    def push_repo(self):
        path = self.repo_path.get()
        if not path: return
        try:
            self.log("Pushing changes...", "info")
            self.git_service.push_changes()
            self.log("Push complete.", "info")
        except Exception as e:
            self.log(f"Push failed: {e}", "error")
            self.show_error("Push Failed", str(e))

    def generate_message_thread(self):
        threading.Thread(target=self.generate_message, daemon=True).start()

    def generate_message(self):
        path = self.repo_path.get()
        if not path:
            self.show_error("Selection Required", "Please select a git repository first.")
            return

        selected = self.get_selected_files()
        if not selected:
             self.log("No files selected for generation.", "error")
             self.show_error("No Files", "Please select at least one file to generate a message for.")
             return

        self.log(f"Generating message for {len(selected)} files...", "info")
        
        try:
            diff = self.git_service.get_diff(files=selected)
            if not diff:
                self.log("Diff empty.", "error")
                return
            
            # Show diff in terminal with colors
            self.after(0, lambda: self.show_diff_preview(diff))

            full_message = self.ai_service.generate_commit_message(diff)
            
            parts = full_message.split('\n', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            
            self.after(0, lambda: self._update_ui_with_message(title, description))
            self.after(0, lambda: self.log("AI Message generated.", "info"))

        except Exception as e:
            self.after(0, lambda: self.show_error("Error", str(e)))
            self.after(0, lambda: self.log(f"Error: {e}", "error"))

    def _update_ui_with_message(self, title, description):
        self.title_entry.delete(0, END)
        self.title_entry.insert(0, title)
        self.desc_text.delete("0.0", END)
        self.desc_text.insert("0.0", description)

    def commit_changes(self):
        path = self.repo_path.get()
        if not path: return
        
        selected = self.get_selected_files()
        if not selected:
            self.show_error("No Files", "Please select files to commit.")
            return

        title = self.title_entry.get().strip()
        description = self.desc_text.get("0.0", END).strip()
        
        if not title:
            self.show_error("Missing Info", "Commit title cannot be empty.")
            return

        full_message = f"{title}\n\n{description}" if description else title

        try:
             self.log(f"Staging {len(selected)} files...", "info")
             self.git_service.stage_files(selected)
             
             self.log("Committing...", "info")
             self.git_service.commit_changes(full_message)
             
             self.log("Success! Commit created.", "info")
             self.title_entry.delete(0, END)
             self.desc_text.delete("0.0", END)
             
             self.refresh_status() # Refresh file list (should be empty of staged)
        except Exception as e:
             self.log(f"Commit Error: {e}", "error")
             self.show_error("Commit Failed", str(e))

    def open_settings(self):
        SettingsDialog(self, self.ai_service, on_save_callback=lambda: self.log("Configuration updated.", "info"))
    
    def check_api_key(self):
        valid, msg = self.ai_service.config.validate()
        if not valid:
             self.log("Configuration missing. Please set API Key.", "error")
             self.open_settings()
             
    def show_error(self, title, message):
        ErrorDialog(self, title, message)

if __name__ == "__main__":
    app = AutoCommitterApp()
    app.mainloop()
