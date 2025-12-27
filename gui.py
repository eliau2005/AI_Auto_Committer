import customtkinter as ctk
from tkinter import filedialog, END
import threading
from git_service import GitService
from ai_service import AIService
from exceptions import APIKeyError, AIServiceError, NetworkError

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title("Error")
        self.geometry("400x200")
        # Center the window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set() # Make modal
        
        lbl_title = ctk.CTkLabel(self, text=title, font=("Helvetica", 16, "bold"), text_color="#ff5555")
        lbl_title.pack(pady=(20, 10), padx=20)
        
        lbl_msg = ctk.CTkLabel(self, text=message, wraplength=350)
        lbl_msg.pack(pady=10, padx=20)
        
        btn = ctk.CTkButton(self, text="Dismiss", command=self.destroy, fg_color="#ff5555", hover_color="#cc0000")
        btn.pack(pady=(10, 20))

class AutoCommitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Auto-Committer")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")
        
        self.git_service = GitService()
        self.ai_service = AIService()
        
        self.repo_path = ctk.StringVar()
        
        self._setup_ui()
        
    def _setup_ui(self):
        # 1. Path Selection
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=10, pady=10)
        
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.repo_path, placeholder_text="Select Repository Path...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", width=100, command=self.select_directory)
        browse_btn.pack(side="right")
        
        # 2. Terminal / Status Output
        self.terminal_text = ctk.CTkTextbox(self, height=100, fg_color="black", text_color="green", font=("Consolas", 12))
        self.terminal_text.pack(fill="x", padx=10, pady=(0, 10))
        self.terminal_text.insert("0.0", "Ready.\n")
        self.terminal_text.configure(state="disabled")
        
        # 3. Message Preview
        # Title
        title_label = ctk.CTkLabel(self, text="Commit Title:", anchor="w")
        title_label.pack(fill="x", padx=10, pady=(5, 0))
        
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Commit Summary")
        self.title_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Description
        desc_label = ctk.CTkLabel(self, text="Commit Description:", anchor="w")
        desc_label.pack(fill="x", padx=10)
        
        self.desc_text = ctk.CTkTextbox(self, height=150, font=("Consolas", 12))
        self.desc_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 4. Action Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.gen_btn = ctk.CTkButton(btn_frame, text="Generate Message", command=self.generate_message_thread)
        self.gen_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.commit_btn = ctk.CTkButton(btn_frame, text="Commit Changes", command=self.commit_changes, fg_color="green", hover_color="darkgreen")
        self.commit_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def log(self, message):
        self.terminal_text.configure(state="normal")
        self.terminal_text.insert(END, f"> {message}\n")
        self.terminal_text.see(END)
        self.terminal_text.configure(state="disabled")

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

    def generate_message_thread(self):
        threading.Thread(target=self.generate_message, daemon=True).start()

    def generate_message(self):
        path = self.repo_path.get()
        if not path:
            self.log("Error: No repository path selected.")
            return

        self.log("Analyzing changes and generating message...")
        try:
            # Re-init git service with correct path just in case
            if not self.git_service.is_valid_repo(path):
                 self.log("Error: Repo invalid.")
                 return

            diff = self.git_service.get_diff()
            if not diff:
                self.log("No changes detected.")
                return

            full_message = self.ai_service.generate_commit_message(diff)
            
            # Split into Title and Description
            parts = full_message.split('\n', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            
            # Update UI in main thread (using after to be thread-safe)
            self.after(0, lambda: self._update_ui_with_message(title, description))
            self.after(0, lambda: self.log("Message generated."))

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
             self.log("Error: No path.")
             return
             
        title = self.title_entry.get().strip()
        description = self.desc_text.get("0.0", END).strip()
        
        if not title:
            self.log("Error: Commit title is empty.")
            return

        full_message = f"{title}\n\n{description}" if description else title

        try:
             self.log("Staging files...")
             self.git_service.stage_all()
             self.log("Committing...")
             self.git_service.commit_changes(full_message)
             self.log("Success! Changes committed.")
             
             # Clear fields after successful commit
             self.title_entry.delete(0, END)
             self.desc_text.delete("0.0", END)
        except Exception as e:
             self.log(f"Commit Error: {e}")
             self.show_error("Commit Failed", str(e))

if __name__ == "__main__":
    app = AutoCommitterApp()
    app.mainloop()
