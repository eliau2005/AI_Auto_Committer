import customtkinter as ctk
from views import styles

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, ai_service, on_save_callback=None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        
        self.ai_service = ai_service
        self.on_save_callback = on_save_callback
        
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 400
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
            self.geometry(f"+{x}+{y}")
        except:
            # Fallback if parent geometry isn't ready
            self.geometry("+100+100")
        
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=styles.PADDING_STD, pady=styles.PADDING_STD)
        main_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(main_frame, text="Configuration", font=styles.get_font_header(), anchor="w")
        header.grid(row=0, column=0, sticky="ew", pady=(0, styles.PADDING_STD))

        lbl_prov = ctk.CTkLabel(main_frame, text="AI Provider", font=styles.get_font_main(), anchor="w")
        lbl_prov.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.provider_var = ctk.StringVar(value=self.ai_service.config.get_provider())
        self.provider_menu = ctk.CTkOptionMenu(
            main_frame, 
            values=["gemini", "ollama", "openai"],
            variable=self.provider_var,
            font=styles.get_font_main(),
            height=40,
            command=self.update_model_list
        )
        self.provider_menu.grid(row=2, column=0, sticky="ew", pady=(0, styles.PADDING_STD))

        key_label = ctk.CTkLabel(main_frame, text="API Key (Optional for Ollama)", font=styles.get_font_main(), anchor="w")
        key_label.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        self.key_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter API Key", height=40, font=styles.get_font_main())
        self.key_entry.grid(row=4, column=0, sticky="ew", pady=(0, styles.PADDING_STD))
        if self.ai_service.config.api_key and self.ai_service.config.api_key != "ollama":
            self.key_entry.insert(0, self.ai_service.config.api_key)

        model_label = ctk.CTkLabel(main_frame, text="Model Name", font=styles.get_font_main(), anchor="w")
        model_label.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        
        self.model_menu = ctk.CTkComboBox(
            main_frame, 
            values=[],
            height=40, 
            font=styles.get_font_main()
        )
        self.model_menu.grid(row=6, column=0, sticky="ew", pady=(0, styles.PADDING_STD))
        
        # Initialize model list
        self.update_model_list(self.provider_var.get())
        
        # Set current model if available
        if self.ai_service.config.model_name:
             self.model_menu.set(self.ai_service.config.model_name)
            
        prompt_label = ctk.CTkLabel(main_frame, text="Custom System Prompt (Optional)", font=styles.get_font_main(), anchor="w")
        prompt_label.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        
        self.prompt_entry = ctk.CTkEntry(main_frame, placeholder_text="Override default prompt...", height=40, font=styles.get_font_main())
        self.prompt_entry.grid(row=8, column=0, sticky="ew", pady=(0, styles.PADDING_STD))
        current_prompt = self.ai_service.config.get_system_prompt()
        if current_prompt:
             self.prompt_entry.insert(0, current_prompt)

        theme_label = ctk.CTkLabel(main_frame, text="Theme", font=styles.get_font_main(), anchor="w")
        theme_label.grid(row=9, column=0, sticky="ew", pady=(0, 5))
        
        self.theme_var = ctk.StringVar(value=self.ai_service.config.get_theme())
        self.theme_menu = ctk.CTkOptionMenu(
            main_frame, 
            values=["Light", "Dark"],
            variable=self.theme_var,
            font=styles.get_font_main(),
            height=40
        )
        self.theme_menu.grid(row=10, column=0, sticky="ew", pady=(0, styles.PADDING_STD*2))

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=11, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(1, weight=1) 
        
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            command=self.destroy, 
            fg_color="transparent", 
            border_width=1, 
            font=styles.get_font_main(),
            text_color=styles.COLOR_TEXT,
            height=40,
            width=100
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save Configuration", 
            command=self.save_config, 
            fg_color=styles.COLOR_SUCCESS, 
            hover_color="#388e3c",
            font=styles.get_font_main(),
            height=40,
            width=150
        )
        save_btn.grid(row=0, column=2)

    def update_model_list(self, provider):
        models = self.ai_service.config.get_supported_models(provider)
        self.model_menu.configure(values=models)
        if models:
            self.model_menu.set(models[0])
        else:
            self.model_menu.set("")

    def save_config(self):
        new_key = self.key_entry.get().strip()
        new_model = self.model_menu.get().strip()
        provider = self.provider_var.get()
        prompt = self.prompt_entry.get().strip()
        theme = self.theme_var.get()
        
        if provider != "ollama" and not new_key:
            self.key_entry.configure(border_color=styles.COLOR_ERROR)
            return
            
        self.ai_service.config.update_credentials(new_key, new_model)
        self.ai_service.config.set_provider(provider)
        self.ai_service.config.set_system_prompt(prompt if prompt else None)
        self.ai_service.config.set_theme(theme)
        self.ai_service.reload_config()
        
        # Apply theme immediately
        ctk.set_appearance_mode(theme)
        
        if self.on_save_callback:
            self.on_save_callback()
            
        self.destroy()
