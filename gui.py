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
        self.geometry("550x350")
        self.grid_columnconfigure(0, weight=1)
        
        self.ai_service = ai_service
        self.on_save_callback = on_save_callback
        
        # Center the window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
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

        # API Key
        key_label = ctk.CTkLabel(main_frame, text="Gemini API Key", font=FONT_MAIN, anchor="w")
        key_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.key_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter your Gemini API Key", height=40, font=FONT_MAIN)
        self.key_entry.grid(row=2, column=0, sticky="ew", pady=(0, PADDING_STD))
        if self.ai_service.config.api_key:
            self.key_entry.insert(0, self.ai_service.config.api_key)

        # Model Name
        model_label = ctk.CTkLabel(main_frame, text="Model Name", font=FONT_MAIN, anchor="w")
        model_label.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        self.model_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g. gemini-2.0-flash", height=40, font=FONT_MAIN)
        self.model_entry.grid(row=4, column=0, sticky="ew", pady=(0, PADDING_STD*2))
        if self.ai_service.config.model_name:
            self.model_entry.insert(0, self.ai_service.config.model_name)

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="ew")
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
        
        if not new_key:
            self.key_entry.configure(border_color=COLOR_ERROR)
            return
            
        self.ai_service.config.update_credentials(new_key, new_model)
        self.ai_service.reload_config()
        
        if self.on_save_callback:
            self.on_save_callback()
            
        self.destroy()

class AutoCommitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Auto-Committer")
        self.geometry("900x700")
        self.minsize(600, 500)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.git_service = GitService()
        self.ai_service = AIService()
        
        self.repo_path = ctk.StringVar()
        
        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Path
        self.grid_rowconfigure(1, weight=1) # Content Area
        
        self._setup_ui()
        
        # Check API Key on startup
        self.after(100, self.check_api_key)
        
    def _setup_ui(self):
        # --- 1. Top Bar (Path & Settings) ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_STD, pady=PADDING_STD)
        top_frame.grid_columnconfigure(1, weight=1)

        lbl_path = ctk.CTkLabel(top_frame, text="Repository:", font=FONT_MAIN)
        lbl_path.grid(row=0, column=0, padx=(0, 10))

        self.path_entry = ctk.CTkEntry(
            top_frame, 
            textvariable=self.repo_path, 
            placeholder_text="Select Repository Path...",
            font=FONT_MAIN,
            height=35
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            top_frame, 
            text="Browse", 
            width=100, 
            height=35,
            command=self.select_directory,
            font=FONT_MAIN
        )
        browse_btn.grid(row=0, column=2, padx=(0, 10))

        settings_btn = ctk.CTkButton(
            top_frame, 
            text="⚙", 
            width=40, 
            height=35,
            command=self.open_settings,
            font=FONT_MAIN
        )
        settings_btn.grid(row=0, column=3)
        
        # --- 2. Main Content Area ---
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING_STD, pady=(0, PADDING_STD))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(2, weight=1) # Description
        content_frame.grid_rowconfigure(4, weight=0) # Terminal
        
        # Commit Components
        lbl_title = ctk.CTkLabel(content_frame, text="Commit Title", font=FONT_HEADER, anchor="w")
        lbl_title.grid(row=0, column=0, sticky="ew", padx=PADDING_STD, pady=(PADDING_STD, 5))
        
        self.title_entry = ctk.CTkEntry(
            content_frame, 
            placeholder_text="Brief summary of changes",
            font=FONT_MAIN,
            height=40
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=PADDING_STD, pady=(0, PADDING_STD))
        
        lbl_desc = ctk.CTkLabel(content_frame, text="Description", font=FONT_HEADER, anchor="w")
        lbl_desc.grid(row=2, column=0, sticky="ew", padx=PADDING_STD, pady=(0, 5))
        
        self.desc_text = ctk.CTkTextbox(
            content_frame, 
            font=FONT_MONO,
            height=150
        )
        self.desc_text.grid(row=3, column=0, sticky="nsew", padx=PADDING_STD, pady=(0, PADDING_STD))
        
        # Terminal Output (Collapsible-ish feel, smaller)
        lbl_term = ctk.CTkLabel(content_frame, text="Activity Log", font=("Segoe UI", 12), text_color="gray", anchor="w")
        lbl_term.grid(row=4, column=0, sticky="ew", padx=PADDING_STD, pady=(0, 2))
        
        self.terminal_text = ctk.CTkTextbox(
            content_frame, 
            height=100, 
            fg_color="#1e1e1e", 
            text_color="#00e676", 
            font=("Consolas", 11)
        )
        self.terminal_text.grid(row=5, column=0, sticky="ew", padx=PADDING_STD, pady=(0, PADDING_STD))
        self.terminal_text.insert("0.0", "Ready.\n")
        self.terminal_text.configure(state="disabled")
        
        # --- 3. Action Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_STD, pady=(0, PADDING_STD))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.gen_btn = ctk.CTkButton(
            btn_frame, 
            text="✨ Generate Suggestion", 
            command=self.generate_message_thread,
            font=("Segoe UI", 15, "bold"),
            height=50,
            fg_color="#5c6bc0", 
            hover_color="#3949ab"
        )
        self.gen_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.commit_btn = ctk.CTkButton(
            btn_frame, 
            text="✓ Commit Changes", 
            command=self.commit_changes, 
            font=("Segoe UI", 15, "bold"),
            height=50,
            fg_color=COLOR_SUCCESS, 
            hover_color="#388e3c"
        )
        self.commit_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def log(self, message):
        self.terminal_text.configure(state="normal")
        self.terminal_text.insert(END, f"> {message}\n")
        self.terminal_text.see(END)
        self.terminal_text.configure(state="disabled")

    def open_settings(self):
        SettingsDialog(self, self.ai_service, on_save_callback=lambda: self.log("Configuration updated."))

    def check_api_key(self):
        valid, msg = self.ai_service.config.validate()
        if not valid:
             self.log("Configuration missing. Please set API Key.")
             self.open_settings()

    def show_error(self, title, message):
        ErrorDialog(self, title, message)

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            if self.git_service.is_valid_repo(path):
                self.repo_path.set(path)
                self.log(f"Repository selected: {path}")
            else:
                self.log(f"Error: Invalid Git Repository at {path}")
                self.repo_path.set("")
                self.show_error("Invalid Repo", f"The directory:\n{path}\nis not a valid Git repository.")

    def generate_message_thread(self):
        threading.Thread(target=self.generate_message, daemon=True).start()

    def generate_message(self):
        path = self.repo_path.get()
        if not path:
            self.show_error("Selection Required", "Please select a git repository first.")
            return

        self.log("Analyzing changes and generating message...")
        # Disable buttons? Maybe later.
        
        try:
            if not self.git_service.is_valid_repo(path):
                 self.log("Error: Repo invalid.")
                 return

            diff = self.git_service.get_diff()
            if not diff:
                self.log("No changes detected.")
                self.after(0, lambda: self.show_error("No Changes", "There are no staged or unstaged changes to commit."))
                return

            full_message = self.ai_service.generate_commit_message(diff)
            
            parts = full_message.split('\n', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            
            self.after(0, lambda: self._update_ui_with_message(title, description))
            self.after(0, lambda: self.log("Message generated successfully."))

        except APIKeyError as e:
            self.after(0, lambda: self.show_error("API Authentication Error", str(e)))
            self.after(0, lambda: self.log(f"API Error: {e}"))
        except AIServiceError as e:
            self.after(0, lambda: self.show_error("AI Service Error", str(e)))
            self.after(0, lambda: self.log(f"AI Error: {e}"))
        except Exception as e:
            self.after(0, lambda: self.show_error("Unexpected Error", str(e)))
            self.after(0, lambda: self.log(f"Error: {e}"))

    def _update_ui_with_message(self, title, description):
        self.title_entry.delete(0, END)
        self.title_entry.insert(0, title)
        self.desc_text.delete("0.0", END)
        self.desc_text.insert("0.0", description)

    def commit_changes(self):
        path = self.repo_path.get()
        if not path:
             self.show_error("Selection Required", "Please select a git repository first.")
             return
             
        title = self.title_entry.get().strip()
        description = self.desc_text.get("0.0", END).strip()
        
        if not title:
            self.show_error("Missing Info", "Commit title cannot be empty.")
            return

        full_message = f"{title}\n\n{description}" if description else title

        try:
             self.log("Staging files...")
             self.git_service.stage_all()
             self.log("Committing...")
             self.git_service.commit_changes(full_message)
             self.log("Success! Changes committed.")
             
             self.title_entry.delete(0, END)
             self.desc_text.delete("0.0", END)
             self.log("Ready for next task.")
        except Exception as e:
             self.log(f"Commit Error: {e}")
             self.show_error("Commit Failed", str(e))

if __name__ == "__main__":
    app = AutoCommitterApp()
    app.mainloop()
