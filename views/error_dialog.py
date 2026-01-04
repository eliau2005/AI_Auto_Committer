import customtkinter as ctk
from views import styles

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x250")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
            self.geometry(f"+{x}+{y}")
        except:
             self.geometry("+100+100")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()
        
        lbl_title = ctk.CTkLabel(
            self, 
            text=title, 
            font=styles.get_font_header(), 
            text_color=styles.COLOR_ERROR
        )
        lbl_title.grid(row=0, column=0, padx=styles.PADDING_STD, pady=(styles.PADDING_STD, styles.PADDING_INNER), sticky="ew")
        
        msg_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        msg_frame.grid(row=1, column=0, padx=styles.PADDING_STD, pady=styles.PADDING_INNER, sticky="nsew")
        
        lbl_msg = ctk.CTkLabel(
            msg_frame, 
            text=message, 
            font=styles.get_font_main(),
            wraplength=380,
            justify="left"
        )
        lbl_msg.pack(fill="both", expand=True)
        
        btn = ctk.CTkButton(
            self, 
            text="Dismiss", 
            command=self.destroy, 
            font=styles.get_font_main(),
            fg_color=styles.COLOR_ERROR, 
            hover_color="#d32f2f",
            height=40
        )
        btn.grid(row=2, column=0, padx=styles.PADDING_STD, pady=styles.PADDING_STD, sticky="ew")
