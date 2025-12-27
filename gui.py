import customtkinter as ctk
from tkinter import filedialog, END
import threading
from git_service import GitService
from ai_service import AIService
from exceptions import APIKeyError, AIServiceError, NetworkError

# --- Configuration & Constants ---
# We define fonts as helper functions or lazy properties to avoid init issues

def get_font_main(): return ctk.CTkFont(family="Segoe UI", size=14)
def get_font_header(): return ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
def get_font_mono(): return ctk.CTkFont(family="Consolas", size=13)

# Color constants
COLOR_SUCCESS = "#4caf50"
COLOR_ERROR = "#f44336"

# Padding constants
PADDING_STD = 20
PADDING_INNER = 10

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x250")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()
        
        lbl_title = ctk.CTkLabel(
            self, 
            text=title, 
            font=get_font_header(), 
            text_color=COLOR_ERROR
        )
        lbl_title.grid(row=0, column=0, padx=PADDING_STD, pady=(PADDING_STD, PADDING_INNER), sticky="ew")
        
        msg_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        msg_frame.grid(row=1, column=0, padx=PADDING_STD, pady=PADDING_INNER, sticky="nsew")
        
        lbl_msg = ctk.CTkLabel(
            msg_frame, 
            text=message, 
            font=get_font_main(),
            wraplength=380,
            justify="left"
        )
        lbl_msg.pack(fill="both", expand=True)
        
        btn = ctk.CTkButton(
            self, 
            text="Dismiss", 
            command=self.destroy, 
            font=get_font_main(),
            fg_color=COLOR_ERROR, 
            hover_color="#d32f2f",
            height=40
        )
        btn.grid(row=2, column=0, padx=PADDING_STD, pady=PADDING_STD, sticky="ew")

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, ai_service, on_save_callback=None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        
        self.ai_service = ai_service
        self.on_save_callback = on_save_callback
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 400
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        self.geometry(f"+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_STD, pady=PADDING_STD)
        main_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(main_frame, text="Configuration", font=get_font_header(), anchor="w")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_STD))

        lbl_prov = ctk.CTkLabel(main_frame, text="AI Provider", font=get_font_main(), anchor="w")
        lbl_prov.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.provider_var = ctk.StringVar(value=self.ai_service.config.get_provider())
        self.provider_menu = ctk.CTkOptionMenu(
            main_frame, 
            values=["gemini", "ollama", "openai"],
            variable=self.provider_var,
            font=get_font_main(),
            height=40
        )
        self.provider_menu.grid(row=2, column=0, sticky="ew", pady=(0, PADDING_STD))

        key_label = ctk.CTkLabel(main_frame, text="API Key (Optional for Ollama)", font=get_font_main(), anchor="w")
        key_label.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        self.key_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter API Key", height=40, font=get_font_main())
        self.key_entry.grid(row=4, column=0, sticky="ew", pady=(0, PADDING_STD))
        if self.ai_service.config.api_key and self.ai_service.config.api_key != "ollama":
            self.key_entry.insert(0, self.ai_service.config.api_key)

        model_label = ctk.CTkLabel(main_frame, text="Model Name", font=get_font_main(), anchor="w")
        model_label.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        
        self.model_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g. gemini-2.0-flash", height=40, font=get_font_main())
        self.model_entry.grid(row=6, column=0, sticky="ew", pady=(0, PADDING_STD))
        if self.ai_service.config.model_name:
            self.model_entry.insert(0, self.ai_service.config.model_name)
            
        prompt_label = ctk.CTkLabel(main_frame, text="Custom System Prompt (Optional)", font=get_font_main(), anchor="w")
        prompt_label.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        
        self.prompt_entry = ctk.CTkEntry(main_frame, placeholder_text="Override default prompt...", height=40, font=get_font_main())
        self.prompt_entry.grid(row=8, column=0, sticky="ew", pady=(0, PADDING_STD*2))
        current_prompt = self.ai_service.config.get_system_prompt()
        if current_prompt:
             self.prompt_entry.insert(0, current_prompt)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=9, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(1, weight=1) 
        
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            command=self.destroy, 
            fg_color="transparent", 
            border_width=1, 
            font=get_font_main(),
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
            font=get_font_main(),
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
        self.minsize(600, 500)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.git_service = GitService()
        self.ai_service = AIService()
        
        # Restore geometry
        geo = self.ai_service.config.get_window_geometry()
        w, h = geo.get("width", 800), geo.get("height", 600)
        self.geometry(f"{w}x{h}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.repo_path = ctk.StringVar()
        self.current_branch = ctk.StringVar(value="HEAD")
        self.status_message = ctk.StringVar(value="Ready")
        self.file_vars = {} 
        self.interactive_elements = []
        self.recent_repo_map = {}

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        self._setup_ui()
        
        self.after(100, self.check_api_key)
        self.after(200, self.load_recent_repos)

    def _setup_ui(self):
        header_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        self.recent_menu = ctk.CTkOptionMenu(
            header_frame, values=["Select Repo..."], command=self.on_recent_repo_select, width=180, font=get_font_main()
        )
        self.recent_menu.pack(side="left", padx=(5, 10))
        self.interactive_elements.append(self.recent_menu)
        
        self.branch_lbl = ctk.CTkButton(
            header_frame, 
            text="Branch: HEAD", 
            fg_color="transparent", 
            border_width=1, 
            border_color="gray", 
            width=120,
            hover=False,
            text_color=("gray10", "#DCE4EE"),
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold")
        )
        self.branch_lbl.pack(side="left")
        
        self.btn_push = ctk.CTkButton(header_frame, text="Push origin", width=100, command=self.push_repo, fg_color="transparent", border_width=1, font=get_font_main())
        self.btn_push.pack(side="right", padx=5)
        self.interactive_elements.append(self.btn_push)
        
        self.btn_pull = ctk.CTkButton(header_frame, text="Fetch origin", width=100, command=self.pull_repo, fg_color="transparent", border_width=1, font=get_font_main())
        self.btn_pull.pack(side="right", padx=5)
        self.interactive_elements.append(self.btn_pull)

        ctk.CTkButton(header_frame, text="⚙", width=30, command=self.open_settings, fg_color="transparent", font=get_font_main()).pack(side="right", padx=5)
        
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_split.grid_rowconfigure(0, weight=1)
        
        main_split.grid_columnconfigure(0, minsize=320, weight=0) 
        main_split.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(main_split, corner_radius=0, fg_color=("gray95", "#2b2b2b"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        sidebar_header = ctk.CTkFrame(self.sidebar, height=40, fg_color="transparent")
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(sidebar_header, text="Changes", font=get_font_header()).pack(side="left")
        
        self.file_list_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.file_list_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        form_frame = ctk.CTkFrame(self.sidebar, fg_color=("gray90", "#232323"), corner_radius=0)
        form_frame.grid(row=2, column=0, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Summary (required)", height=35, font=ctk.CTkFont(family="Segoe UI", size=13))
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))
        self.interactive_elements.append(self.title_entry)

        self.desc_text = ctk.CTkTextbox(form_frame, height=100, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.desc_text.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.interactive_elements.append(self.desc_text)

        self.gen_btn = ctk.CTkButton(
            form_frame, 
            text="✨ Generate AI Message", 
            command=self.generate_message_thread, 
            fg_color="#5c6bc0", 
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.gen_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.interactive_elements.append(self.gen_btn)

        self.commit_btn = ctk.CTkButton(
            form_frame, 
            text="Commit to master", 
            command=self.commit_changes, 
            fg_color=COLOR_SUCCESS, 
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.commit_btn.grid(row=3, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.interactive_elements.append(self.commit_btn)

        diff_container = ctk.CTkFrame(main_split, corner_radius=0, fg_color=("white", "#1e1e1e"))
        diff_container.grid(row=0, column=1, sticky="nsew")
        diff_container.grid_rowconfigure(0, weight=1)
        diff_container.grid_columnconfigure(0, weight=1)

        self.diff_text = ctk.CTkTextbox(
            diff_container, 
            font=get_font_mono(), 
            wrap="none", 
            fg_color="transparent",
            text_color=("black", "#d4d4d4")
        )
        self.diff_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.diff_text.configure(state="disabled")
        
        self.diff_text.tag_config("diff_add", foreground="#22863a", background="#f0fff4")
        self.diff_text.tag_config("diff_rem", foreground="#cb2431", background="#ffeef0")
        self.diff_text.tag_config("diff_header", foreground="#6f42c1")
        
        self.diff_text.tag_config("diff_add", foreground="#4cd964", background="#1a2e1e") 
        self.diff_text.tag_config("diff_rem", foreground="#ff5252", background="#2e1a1a")

        status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color=("gray80", "#252526"))
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.grid_columnconfigure(1, weight=1)

        self.status_lbl = ctk.CTkLabel(status_bar, textvariable=self.status_message, font=ctk.CTkFont(family="Segoe UI", size=11), text_color="gray")
        self.status_lbl.grid(row=0, column=0, padx=10, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(status_bar, height=8, width=200)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=10)
        self.progress_bar.grid_remove()


    # --- Logic ---

    def set_busy(self, busy, message=""):
        if busy:
            self.progress_bar.grid()
            self.progress_bar.start()
            self.status_message.set(message)
            for w in self.interactive_elements:
                try: w.configure(state="disabled")
                except: pass
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            self.status_message.set(message or "Ready")
            for w in self.interactive_elements:
                try: w.configure(state="normal")
                except: pass

    def log(self, message, tag=None):
        # Deprecated: Log to status bar essentially
        print(f"[LOG] {message}") # Keep terminal for debug
        self.status_message.set(message)

    def load_recent_repos(self):
        import os
        repos = self.ai_service.config.get_recent_repos()
        self.recent_repo_map = {}
        display_names = []
        
        for path in repos:
            name = os.path.basename(path)
            if not name: name = path # Root or empty
            
            # Handle duplicates
            if name in self.recent_repo_map and self.recent_repo_map[name] != path:
                # Append part of path to disambiguate? For now just keep original mapping
                # or use full path if duplicate name
                # Simple fallback: use full path for duplicates
                # But to keep logic simple for this user request:
                name = f"{name} ({path})"
            
            self.recent_repo_map[name] = path
            display_names.append(name)
            
        options = ["Browse..."] + display_names
        self.recent_menu.configure(values=options)

    def on_recent_repo_select(self, choice):
        if choice == "Browse...":
            self.select_directory()
        elif choice and choice != "Select Repo...":
            path = self.recent_repo_map.get(choice)
            if path:
                self.repo_path.set(path)
                self.refresh_repo()

    def select_directory(self):
        import os
        path = filedialog.askdirectory()
        if path:
            self.repo_path.set(path)
            self.ai_service.config.add_recent_repo(path)
            self.load_recent_repos()
            
            # Find the display name for this path
            # We just reloaded, so check map
            for name, p in self.recent_repo_map.items():
                if p == path:
                    self.recent_menu.set(name)
                    break
            
            self.refresh_repo()
        else:
            # Revert to previous or default if cancelled? 
            # For now, just reset to what it was or current repo
            current = self.repo_path.get()
            # Try to find name for current path
            if current:
                 for name, p in self.recent_repo_map.items():
                    if p == current:
                        self.recent_menu.set(name)
                        break
            else:
                self.recent_menu.set("Select Repo...")

    def toggle_all_files(self, select=True):
        # This function is no longer directly called by UI buttons in the new layout
        # but might be useful internally or if buttons are re-added.
        if not self.file_vars: return
        for var in self.file_vars.values():
            var.set(select)
        self.update_diff_preview_wrapper()

    def refresh_repo(self):
        path = self.repo_path.get()
        if not path: return
        
        if not self.git_service.is_valid_repo(path):
            self.status_message.set("Invalid Repository")
            self.branch_lbl.configure(text="Invalid")
            self._clear_file_list()
            return
            
        branch = self.git_service.get_current_branch()
        self.current_branch.set(branch)
        self.branch_lbl.configure(text=f"Branch: {branch}")
        self.commit_btn.configure(text=f"Commit to {branch}")
        self.status_message.set(f"Repository loaded: {path}")
        
        self._refresh_file_list()

    def _clear_file_list(self):
        for w in self.file_list_frame.winfo_children(): w.destroy()
        self.file_vars = {}
        self.update_diff_view("")

    def _refresh_file_list(self):
        self._clear_file_list()
        files = self.git_service.get_changed_files()
        
        if not files:
            ctk.CTkLabel(self.file_list_frame, text="No changes", text_color="gray").pack(pady=20)
            return

        for f in files:
            var = ctk.BooleanVar(value=True)
            self.file_vars[f] = var
            # command=self.on_file_select_change could filter diff
            chk = ctk.CTkCheckBox(
                self.file_list_frame, 
                text=f, 
                variable=var, 
                font=("Segoe UI", 12),
                command=self.update_diff_preview_wrapper # auto update diff on check?
            )
            chk.pack(anchor="w", pady=2, padx=5)
        
        # Auto load diff for all
        self.update_diff_preview_wrapper()

    def update_diff_preview_wrapper(self):
        # Debounce?
        selected = [f for f, v in self.file_vars.items() if v.get()]
        if not selected: 
            self.update_diff_view("")
            return
        
        # Running diff on main thread for responsiveness if small. 
        # If huge, thread it.
        try:
            diff = self.git_service.get_diff(files=selected)
            self.update_diff_view(diff)
        except Exception as e:
            self.status_message.set(f"Error getting diff: {e}")
            self.update_diff_view(f"Error loading diff: {e}")

    def update_diff_view(self, diff_text):
        self.diff_text.configure(state="normal")
        self.diff_text.delete("1.0", END)
        if not diff_text:
            self.diff_text.insert("0.0", "No files selected or no changes.")
        else:
            for line in diff_text.splitlines():
                if line.startswith("diff --git"):
                    self.diff_text.insert(END, line + "\n", "diff_header")
                elif line.startswith("+") and not line.startswith("+++"):
                    self.diff_text.insert(END, line + "\n", "diff_add")
                elif line.startswith("-") and not line.startswith("---"):
                    self.diff_text.insert(END, line + "\n", "diff_rem")
                else:
                    self.diff_text.insert(END, line + "\n")
        self.diff_text.configure(state="disabled")

    def pull_repo(self):
        self._run_async("Pulling...", self.git_service.pull_changes)

    def push_repo(self):
        self._run_async("Pushing...", self.git_service.push_changes)

    def _run_async(self, msg, func, *args):
        def _task():
            try:
                func(*args)
                self.after(0, lambda: self.status_message.set("Action complete."))
                self.after(0, self.refresh_repo)
            except Exception as e:
                self.after(0, lambda: self.show_error("Error", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready"))
        
        self.set_busy(True, msg)
        threading.Thread(target=_task, daemon=True).start()

    def generate_message_thread(self):
        files = [f for f,v in self.file_vars.items() if v.get()]
        if not files: 
            self.show_error("No selection", "Select files first.")
            return
            
        def _task():
            try:
                diff = self.git_service.get_diff(files=files)
                if not diff: 
                    self.after(0, lambda: self.status_message.set("No diff to generate message for."))
                    return
                msg = self.ai_service.generate_commit_message(diff)
                
                parts = msg.split('\n', 1)
                title = parts[0].strip()
                desc = parts[1].strip() if len(parts) > 1 else ""
                
                self.after(0, lambda: self._fill_form(title, desc))
                self.after(0, lambda: self.status_message.set("AI message generated."))
            except Exception as e:
                self.after(0, lambda: self.show_error("AI Error", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready"))

        self.set_busy(True, "Generating message...")
        threading.Thread(target=_task, daemon=True).start()

    def _fill_form(self, title, desc):
        # Ensure widgets are editable
        try:
            self.title_entry.configure(state="normal")
        except:
            pass
        
        self.title_entry.delete(0, END)
        self.title_entry.insert(0, title)
        
        # CTkTextbox needs to be in normal state before editing
        try:
            self.desc_text.configure(state="normal")
        except:
            pass
        
        self.desc_text.delete("0.0", END)
        self.desc_text.insert("0.0", desc)

    def commit_changes(self):
        files = [f for f,v in self.file_vars.items() if v.get()]
        title = self.title_entry.get().strip()
        desc = self.desc_text.get("0.0", END).strip()
        
        if not files or not title:
            self.show_error("Incomplete", "Select files and provide a title.")
            return
            
        full_msg = f"{title}\n\n{desc}" if desc else title
        
        def _task():
            try:
                self.git_service.stage_files(files)
                self.git_service.commit_changes(full_msg)
                self.after(0, lambda: self.status_message.set("Commit successful."))
                self.after(0, lambda: self._fill_form("", "")) # Clear form
                self.after(0, self.refresh_repo)
            except Exception as e:
                self.after(0, lambda: self.show_error("Commit Error", str(e)))
            finally:
                self.after(0, lambda: self.set_busy(False, "Ready"))
                
        self.set_busy(True, "Committing...")
        threading.Thread(target=_task, daemon=True).start()

    def open_settings(self):
        SettingsDialog(self, self.ai_service, on_save_callback=lambda: self.log("Configuration updated."))
        
    def check_api_key(self):
        v, _ = self.ai_service.config.validate()
        if not v: self.open_settings()
        
    def show_error(self, t, m):
        ErrorDialog(self, t, m)

    def on_closing(self):
        # Use geometry string to get actual logical size, avoiding DPI scaling issues
        try:
            geo = self.geometry()
            # Format is typically 'WxH+X+Y'
            size = geo.split('+')[0]
            w, h = map(int, size.split('x'))
            self.ai_service.config.set_window_geometry(w, h)
        except:
             # Fallback if parsing fails (unlikely)
            pass
        self.destroy()

if __name__ == "__main__":
    app = AutoCommitterApp()
    app.mainloop()

