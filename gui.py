import customtkinter as ctk
from tkinter import filedialog, END
import threading
from git_service import GitService
from ai_service import AIService

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
        preview_label = ctk.CTkLabel(self, text="Commit Message Preview:", anchor="w")
        preview_label.pack(fill="x", padx=10)
        
        self.preview_text = ctk.CTkTextbox(self, height=200, font=("Consolas", 12))
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=5)
        
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

            message = self.ai_service.generate_commit_message(diff)
            
            # Update UI in main thread (simple tkinter usually handles this ok, but safer to schedule)
            self.preview_text.delete("0.0", END)
            self.preview_text.insert("0.0", message)
            self.log("Message generated.")
        except Exception as e:
            self.log(f"Error: {e}")

    def commit_changes(self):
        path = self.repo_path.get()
        if not path:
             self.log("Error: No path.")
             return
             
        message = self.preview_text.get("0.0", END).strip()
        if not message:
            self.log("Error: Commit message is empty.")
            return

        try:
             self.log("Staging files...")
             self.git_service.stage_all()
             self.log("Committing...")
             self.git_service.commit_changes(message)
             self.log("Success! Changes committed.")
             self.preview_text.delete("0.0", END)
        except Exception as e:
             self.log(f"Commit Error: {e}")

if __name__ == "__main__":
    app = AutoCommitterApp()
    app.mainloop()
