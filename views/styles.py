import customtkinter as ctk

# --- Fonts ---
def get_font_main(): return ctk.CTkFont(family="Segoe UI", size=14)
def get_font_header(): return ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
def get_font_mono(): return ctk.CTkFont(family="Consolas", size=13)
def get_font_branch(): return ctk.CTkFont(family="Consolas", size=13, weight="bold")
def get_font_small_ui(): return ctk.CTkFont(family="Segoe UI", size=12)
def get_font_ui_bold(): return ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
def get_font_small(): return ctk.CTkFont(family="Segoe UI", size=11)


# --- Colors ---
COLOR_SUCCESS = "#4caf50"
COLOR_ERROR = "#f44336"

# Theme Colors (Light, Dark)
COLOR_BG_MAIN = ("#fcfbf4", "#2b2b2b") # Cream White / Dark Gray
COLOR_SIDEBAR = ("#e8e6f0", "#2b2b2b") # Light Purple-Gray / Dark Gray
COLOR_TEXT = ("#2d2d2d", "#DCE4EE") # Very Dark Gray / Light
COLOR_BTN_PRIMARY = ("#7e57c2", "#5c6bc0") # Purple / Indigo
COLOR_BTN_HOVER = ("#673ab7", "#3949ab")
COLOR_DIFF_BG = ("#ffffff", "#1e1e1e")
COLOR_DIFF_TEXT = ("#1a1a1a", "#d4d4d4")
COLOR_HEADER_BTN_TEXT = ("#2d2d2d", "#DCE4EE") # Very Dark Gray / Light
COLOR_LABEL_TEXT = ("#1a1a1a", "#DCE4EE") # Almost Black / Light
COLOR_STATUS_BAR = ("gray80", "#252526")

# --- Diff Tags ---
DIFF_TAGS = {
    "diff_add": {"foreground": "#4cd964", "background": "#1a2e1e"},
    "diff_rem": {"foreground": "#ff5252", "background": "#2e1a1a"},
    "diff_header": {"foreground": "#6f42c1"}
}

# --- Padding ---
PADDING_STD = 20
PADDING_INNER = 10
