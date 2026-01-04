import customtkinter as ctk
from views import styles
from tkinter import END

class CommitView(ctk.CTkFrame):
    def __init__(self, parent, on_generate_callback, on_commit_callback, on_selection_change_callback=None):
        super().__init__(parent, corner_radius=0, fg_color=styles.COLOR_SIDEBAR)
        
        self.on_generate = on_generate_callback
        self.on_commit = on_commit_callback
        self.on_selection_change = on_selection_change_callback
        
        self.file_vars = {}
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        sidebar_header = ctk.CTkFrame(self, height=40, fg_color="transparent")
        sidebar_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(sidebar_header, text="Changes", font=styles.get_font_header(), text_color=styles.COLOR_LABEL_TEXT).pack(side="left")
        
        # File List
        self.file_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.file_list_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Form Area
        form_frame = ctk.CTkFrame(self, fg_color=styles.COLOR_SIDEBAR, corner_radius=0)
        form_frame.grid(row=2, column=0, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Summary (required)", 
            height=35, 
            font=styles.get_font_ui_bold()
        )
        self.title_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 5))

        self.desc_text = ctk.CTkTextbox(
            form_frame, 
            height=100, 
            font=styles.get_font_small_ui()
        )
        self.desc_text.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.gen_btn = ctk.CTkButton(
            form_frame, 
            text="✨ Generate AI Message", 
            command=self._on_generate_click, 
            fg_color=styles.COLOR_BTN_PRIMARY,
            hover_color=styles.COLOR_BTN_HOVER,
            height=30,
            font=styles.get_font_small_ui()
        )
        self.gen_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        self.commit_btn = ctk.CTkButton(
            form_frame, 
            text="Commit", 
            command=self._on_commit_click, 
            fg_color=styles.COLOR_SUCCESS, 
            height=40,
            font=styles.get_font_ui_bold()
        )
        self.commit_btn.grid(row=3, column=0, padx=10, pady=(0, 15), sticky="ew")

    def set_file_list(self, files, selected_files=None):
        # Clear existing
        for w in self.file_list_frame.winfo_children(): w.destroy()
        self.file_vars = {}
        
        if not files:
            ctk.CTkLabel(self.file_list_frame, text="No changes", text_color="gray").pack(pady=20)
            return

        for f in files:
            is_selected = True # Default to true
            if selected_files is not None:
                is_selected = f in selected_files
            
            var = ctk.BooleanVar(value=is_selected)
            self.file_vars[f] = var
            chk = ctk.CTkCheckBox(
                self.file_list_frame, 
                text=f, 
                variable=var, 
                font=styles.get_font_small_ui(),
                text_color=styles.COLOR_TEXT,
                command=self._on_check_change
            )
            chk.pack(anchor="w", pady=2, padx=5)

    def _on_check_change(self):
        if self.on_selection_change:
            selected = [f for f, v in self.file_vars.items() if v.get()]
            self.on_selection_change(selected)

    def _on_generate_click(self):
        if self.on_generate:
            self.on_generate()

    def _on_commit_click(self):
        if self.on_commit:
            self.on_commit()

    def get_commit_message(self):
        title = self.title_entry.get().strip()
        desc = self.desc_text.get("0.0", END).strip()
        return title, desc

    def set_commit_message(self, title, desc):
        try:
            self.title_entry.delete(0, END)
            self.title_entry.insert(0, title)
            self.desc_text.delete("0.0", END)
            self.desc_text.insert("0.0", desc)
        except:
            pass

    def set_loading(self, is_loading):
        state = "disabled" if is_loading else "normal"
        self.gen_btn.configure(state=state)
        self.commit_btn.configure(state=state)
        self.title_entry.configure(state=state)
        # Textbox enabling/disabling is a bit different but we can skip strict disabling for text for now
        # or use configure(state=...)
