import customtkinter as ctk
from views import styles
from tkinter import END

class DiffView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color=styles.COLOR_DIFF_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.diff_tabs = ctk.CTkTabview(
            self, 
            corner_radius=0, 
            fg_color="transparent",
            segmented_button_fg_color=styles.COLOR_SIDEBAR,
            segmented_button_selected_color=styles.COLOR_BTN_PRIMARY,
            segmented_button_unselected_color=("#d0d0d0", "#404040"),
            segmented_button_selected_hover_color=styles.COLOR_BTN_HOVER,
            segmented_button_unselected_hover_color=("#e0e0e0", "#505050"),
            text_color=styles.COLOR_TEXT
        )
        self.diff_tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
    def update_diffs(self, diff_map: dict):
        """
        Updates the tabs with provided diffs.
        diff_map: dict where key is filename, value is diff text.
        """
        # Get current tabs
        try:
            current_tabs = set(self.diff_tabs._tab_dict.keys())
        except:
            current_tabs = set()
            
        new_files = set(diff_map.keys())
        
        # Remove tabs not in new_files
        for t in current_tabs:
            if t not in new_files:
                self.diff_tabs.delete(t)
                
        # Add or Update tabs
        for filename, diff_text in diff_map.items():
            if filename not in current_tabs:
                self._create_tab(filename, diff_text)
            else:
                # Optional: Update text if tab exists? 
                # For now assume we don't update existing tabs often unless refreshed
                # But let's support it if needed.
                # Since accessing the textbox inside isn't direct in CTkTabview public API,
                # we might just recreate or find it.
                # Simplified: only create if not exists.
                pass

    def _create_tab(self, filename, diff_text):
        self.diff_tabs.add(filename)
        tab = self.diff_tabs.tab(filename)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(
            tab, 
            font=styles.get_font_mono(), 
            wrap="none", 
            fg_color="transparent",
            text_color=styles.COLOR_DIFF_TEXT
        )
        textbox.grid(row=0, column=0, sticky="nsew")
        
        # Configure tags
        for tag, kargs in styles.DIFF_TAGS.items():
            textbox.tag_config(tag, **kargs)
            
        if not diff_text:
            textbox.insert("0.0", "No changes detected.")
        else:
             for line in diff_text.splitlines():
                if line.startswith("diff --git"):
                    textbox.insert(END, line + "\n", "diff_header")
                elif line.startswith("+") and not line.startswith("+++"):
                    textbox.insert(END, line + "\n", "diff_add")
                elif line.startswith("-") and not line.startswith("---"):
                    textbox.insert(END, line + "\n", "diff_rem")
                else:
                    textbox.insert(END, line + "\n")
        
        textbox.configure(state="disabled")
