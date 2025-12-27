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
        self.geometry("1100x850")
        self.minsize(900, 700)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.git_service = GitService()
        self.ai_service = AIService()
        
        self.repo_path = ctk.StringVar()
        self.current_branch = ctk.StringVar(value="HEAD")
        self.status_message = ctk.StringVar(value="Ready")
        self.file_vars = {} # Map path -> BooleanVar
        
        # Interactive elements to disable during async work
        self.interactive_elements = []

        # Configure Main Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=0) # Progress/Status
        self.grid_rowconfigure(2, weight=1) # Main Content
        
        self._setup_ui()
        
        # Check API Key on startup
        self.after(100, self.check_api_key)
        self.after(200, self.load_recent_repos)

    def _setup_ui(self):
        # --- 1. Header (Repo Selection & Global Actions) ---
        header_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_STD, pady=(PADDING_STD, 0))
        header_frame.grid_columnconfigure(1, weight=1) # Path entry expands

        # Recent Repos
        self.recent_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["Select Repo..."],
            command=self.on_recent_repo_select,
            width=160,
            font=FONT_MAIN
        )
        self.recent_menu.grid(row=0, column=0, padx=(0, 10))
        self.interactive_elements.append(self.recent_menu)

        # Path Entry
        self.path_entry = ctk.CTkEntry(
            header_frame, 
            textvariable=self.repo_path, 
            placeholder_text="Select Repository Path...",
            font=FONT_MAIN,
            height=35
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.interactive_elements.append(self.path_entry)
        
        # Browse Button
        browse_btn = ctk.CTkButton(
            header_frame, text="Browse", width=90, height=35,
            command=self.select_directory, font=FONT_MAIN
        )
        browse_btn.grid(row=0, column=2, padx=(0, 10))
        self.interactive_elements.append(browse_btn)

        # Settings Button
        settings_btn = ctk.CTkButton(
            header_frame, text="⚙ Settings", width=100, height=35,
            command=self.open_settings, font=FONT_MAIN,
            fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE")
        )
        settings_btn.grid(row=0, column=3)
        self.interactive_elements.append(settings_btn)

        # --- 2. Status & Progress Bar ---
        status_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        status_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_STD, pady=(10, 5))
        status_frame.grid_columnconfigure(0, weight=1)

        # Progress Bar (Indeterminate when active)
        self.progress_bar = ctk.CTkProgressBar(status_frame, height=10, corner_radius=5)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove() # Hidden by default

        # Status LabelOverlay? Or just text. Let's put text below or beside.
        # Actually let's put branch info and status text in a toolbar below this.

        # --- 3. Toolbar (Branch Info & Sync Actions) ---
        toolbar_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray17"), corner_radius=8)
        toolbar_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_STD, pady=(0, PADDING_STD))
        
        # Branch Info
        lbl_branch_title = ctk.CTkLabel(toolbar_frame, text="BRANCH:", font=("Segoe UI", 12, "bold"), text_color="gray")
        lbl_branch_title.pack(side="left", padx=(15, 5), pady=8)
        
        lbl_branch_val = ctk.CTkLabel(toolbar_frame, textvariable=self.current_branch, font=("Consolas", 14, "bold"))
        lbl_branch_val.pack(side="left", padx=(0, 20), pady=8)

        # Status Message (Center)
        self.lbl_status = ctk.CTkLabel(toolbar_frame, textvariable=self.status_message, font=("Segoe UI", 12))
        self.lbl_status.pack(side="left", fill="x", expand=True)

        # Right Action Buttons
        self.btn_pull = ctk.CTkButton(toolbar_frame, text="⬇ Pull", width=80, height=32, command=self.pull_repo, fg_color="#455a64")
        self.btn_pull.pack(side="right", padx=(5, 10), pady=5)
        self.interactive_elements.append(self.btn_pull)
        
        self.btn_push = ctk.CTkButton(toolbar_frame, text="⬆ Push", width=80, height=32, command=self.push_repo, fg_color="#455a64")
        self.btn_push.pack(side="right", padx=5, pady=5)
        self.interactive_elements.append(self.btn_push)
        
        self.btn_refresh = ctk.CTkButton(toolbar_frame, text="⟳", width=40, height=32, command=self.refresh_status, fg_color="#00897b")
        self.btn_refresh.pack(side="right", padx=5, pady=5)
        self.interactive_elements.append(self.btn_refresh)


        # --- 4. Main Content (Split) ---
        self.grid_rowconfigure(3, weight=1) # Main content row
        
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.grid(row=3, column=0, sticky="nsew", padx=PADDING_STD, pady=(0, PADDING_STD))
        
        # Use Grid for split
        split_frame.grid_columnconfigure(0, weight=1, uniform="group1") # Staging
        split_frame.grid_columnconfigure(1, weight=2, uniform="group1") # Editor
        split_frame.grid_rowconfigure(0, weight=1)

        # === LEFT COLUMN: Staging ===
        staging_container = ctk.CTkFrame(split_frame, corner_radius=10)
        staging_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        staging_container.grid_rowconfigure(2, weight=1)
        staging_container.grid_columnconfigure(0, weight=1)

        # Staging Header
        stage_header = ctk.CTkLabel(staging_container, text="Changed Files", font=FONT_HEADER)
        stage_header.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        # Select All / None
        sel_frame = ctk.CTkFrame(staging_container, fg_color="transparent")
        sel_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        btn_all = ctk.CTkButton(sel_frame, text="All", width=50, height=24, font=("Segoe UI", 11), command=lambda: self.toggle_all_files(True))
        btn_all.pack(side="left", padx=(0, 5))
        
        btn_none = ctk.CTkButton(sel_frame, text="None", width=50, height=24, font=("Segoe UI", 11), command=lambda: self.toggle_all_files(False))
        btn_none.pack(side="left")
        self.interactive_elements.extend([btn_all, btn_none])

        # File List
        self.file_list_frame = ctk.CTkScrollableFrame(staging_container, fg_color="transparent")
        self.file_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # === RIGHT COLUMN: Editor & Terminal ===
        editor_container = ctk.CTkFrame(split_frame, fg_color="transparent")
        editor_container.grid(row=0, column=1, sticky="nsew")
        editor_container.grid_rowconfigure(0, weight=0) # Inputs
        editor_container.grid_rowconfigure(1, weight=1) # Terminal
        editor_container.grid_columnconfigure(0, weight=1)

        # Input Area
        input_frame = ctk.CTkFrame(editor_container, corner_radius=10)
        input_frame.grid(row=0, column=0, sticky="new", pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)

        # Commit Title
        self.title_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Commit Summary (Subject)", 
            font=("Segoe UI", 14), 
            height=45
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        self.interactive_elements.append(self.title_entry)

        # Commit Description
        self.desc_text = ctk.CTkTextbox(
            input_frame, 
            font=FONT_MONO, 
            height=150,
            fg_color=("gray95", "gray20")
        )
        self.desc_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.interactive_elements.append(self.desc_text)

        # Action Buttons
        actions_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        actions_frame.grid_columnconfigure(0, weight=1)

        self.gen_btn = ctk.CTkButton(
            actions_frame, 
            text="✨ Generate with AI", 
            command=self.generate_message_thread, 
            height=45, 
            fg_color="#5c6bc0", 
            font=("Segoe UI", 13, "bold")
        )
        self.gen_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.interactive_elements.append(self.gen_btn)
        
        self.commit_btn = ctk.CTkButton(
            actions_frame, 
            text="✓ Commit Changes", 
            command=self.commit_changes, 
            height=45, 
            fg_color=COLOR_SUCCESS,
            font=("Segoe UI", 13, "bold")
        )
        self.commit_btn.grid(row=0, column=1, sticky="ew")
        self.interactive_elements.append(self.commit_btn)

        # Terminal Area
        term_frame = ctk.CTkFrame(editor_container, corner_radius=10)
        term_frame.grid(row=1, column=0, sticky="nsew")
        term_frame.grid_columnconfigure(0, weight=1)
        term_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(term_frame, text="Activity Log", font=("Segoe UI", 12, "bold"), text_color="gray").grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.terminal_text = ctk.CTkTextbox(
            term_frame, 
            fg_color="#1e1e1e", 
            text_color="#00e676", 
            font=("Consolas", 12),
            wrap="none" # Scroll horizontally for long lines
        )
        self.terminal_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.terminal_text.configure(state="disabled")

        # Tags
        self.terminal_text.tag_config("diff_add", foreground="#66bb6a")
        self.terminal_text.tag_config("diff_rem", foreground="#ef5350")
        self.terminal_text.tag_config("info", foreground="#90caf9")
        self.terminal_text.tag_config("error", foreground=COLOR_ERROR)


    # --- Unified Busy State Management ---
    def set_busy(self, busy, message=""):
        if busy:
            self.progress_bar.grid()
            self.progress_bar.start()
            self.status_message.set(message)
            for widget in self.interactive_elements:
                try:
                    widget.configure(state="disabled")
                except: pass
            
            # Disable file checkboxes
            for chk in self.file_list_frame.winfo_children():
                 try: chk.configure(state="disabled")
                 except: pass

        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self.status_message.set(message or "Ready")
            for widget in self.interactive_elements:
                try:
                    widget.configure(state="normal")
                except: pass
            
            # Enable file checkboxes
            for chk in self.file_list_frame.winfo_children():
                 try: chk.configure(state="normal")
                 except: pass


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
            options = ["Select Repo..."] + repos
            self.recent_menu.configure(values=options)

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

    def toggle_all_files(self, select=True):
        if not self.file_vars: return
        for var in self.file_vars.values():
            var.set(select)

    def refresh_status(self):
        # This is fast enough to run on main thread usually, 
        # but good practice to wrap if git status is slow. For now, keep sync.
        path = self.repo_path.get()
        if not path: return
        
        if not self.git_service.is_valid_repo(path):
            self.log("Invalid Repository", "error")
            self.current_branch.set("Invalid")
            self.status_message.set("Invalid Repository")
            self._clear_staging()
            return
            
        self.current_branch.set(self.git_service.get_current_branch())
        self.log(f"Repo loaded: {path}", "info")
        self.status_message.set("Repository loaded")
        self._refresh_file_list()

    def _clear_staging(self):
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        self.file_vars = {}

    def _refresh_file_list(self):
        self._clear_staging()
        files = self.git_service.get_changed_files()
        
        if not files:
            lbl = ctk.CTkLabel(self.file_list_frame, text="No changes detected", text_color="gray")
            lbl.pack(pady=10)
            return
        
        # Sort files?
        files.sort()

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
        
        def _task():
            try:
                self.after(0, lambda: self.log("Pulling changes...", "info"))
                self.git_service.pull_changes()
                self.after(0, lambda: self.log("Pull complete.", "info"))
                self.after(0, self.refresh_status)
            except Exception as e:
                self.after(0, lambda: self.log(f"Pull failed: {e}", "error"))
                self.after(0, lambda: self.show_error("Pull Failed", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready"))

        self.set_busy(True, "Pulling changes from remote...")
        threading.Thread(target=_task, daemon=True).start()

    def push_repo(self):
        path = self.repo_path.get()
        if not path: return
        
        def _task():
            try:
                self.after(0, lambda: self.log("Pushing changes...", "info"))
                self.git_service.push_changes()
                self.after(0, lambda: self.log("Push complete.", "info"))
            except Exception as e:
                self.after(0, lambda: self.log(f"Push failed: {e}", "error"))
                self.after(0, lambda: self.show_error("Push Failed", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready"))

        self.set_busy(True, "Pushing changes to remote...")
        threading.Thread(target=_task, daemon=True).start()

    def generate_message_thread(self):
        path = self.repo_path.get()
        if not path:
             self.show_error("Selection Required", "Please select a git repository first.")
             return

        selected = self.get_selected_files()
        if not selected:
             self.show_error("No Files", "Please select at least one file to generate a message for.")
             return

        self.set_busy(True, "Generating AI Commit Message...")
        self.log(f"Generating message for {len(selected)} files...", "info")
        threading.Thread(target=self._generate_task, args=(selected,), daemon=True).start()

    def _generate_task(self, selected):
        try:
            diff = self.git_service.get_diff(files=selected)
            if not diff:
                self.after(0, lambda: self.log("Diff empty or no changes found.", "error"))
                self.after(0, lambda: self.set_busy(False, "Ready"))
                return
            
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
        finally:
            self.after(0, lambda: self.set_busy(False, "Ready"))

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

        def _task():
            try:
                 self.after(0, lambda: self.log(f"Staging {len(selected)} files...", "info"))
                 self.git_service.stage_files(selected)
                 
                 self.after(0, lambda: self.log("Committing...", "info"))
                 self.git_service.commit_changes(full_message)
                 
                 self.after(0, lambda: self.log("Success! Commit created.", "info"))
                 self.after(0, lambda: self.title_entry.delete(0, END))
                 self.after(0, lambda: self.desc_text.delete("0.0", END))
                 
                 self.after(0, self.refresh_status)
            except Exception as e:
                 self.after(0, lambda: self.log(f"Commit Error: {e}", "error"))
                 self.after(0, lambda: self.show_error("Commit Failed", str(e)))
            finally:
                 self.after(0, lambda: self.set_busy(False, "Ready"))

        self.set_busy(True, "Committing changes...")
        threading.Thread(target=_task, daemon=True).start()

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
