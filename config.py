import os
import json
from dotenv import load_dotenv, set_key

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.env_file = ".env"
        self.settings_file = "settings.json"
        
        # Load Env Vars
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        
        # Load Settings JSON
        self.settings = self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.settings_file):
            return {
                "recent_repos": [], 
                "provider": "gemini", 
                "system_prompt": None,
                "window_geometry": {"width": 1000, "height": 700} 
            }
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                # Ensure keys exist
                if "recent_repos" not in data: data["recent_repos"] = []
                if "provider" not in data: data["provider"] = "gemini"
                if "system_prompt" not in data: data["system_prompt"] = None
                if "window_geometry" not in data: data["window_geometry"] = {"width": 1000, "height": 700}
                return data
        except:
             return {
                "recent_repos": [], 
                "provider": "gemini", 
                "system_prompt": None,
                "window_geometry": {"width": 1000, "height": 700}
            }

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def validate(self):
        if self.get_provider() == "gemini":
            if not self.api_key:
                return False, "GEMINI_API_KEY not found in environment variables."
        # Ollama might not need a key, or uses 'ollama' as key
        return True, "Configuration valid."

    def update_credentials(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        
        # Persist to .env
        if not os.path.exists(self.env_file):
            open(self.env_file, 'w').close()
            
        set_key(self.env_file, "GEMINI_API_KEY", api_key)
        set_key(self.env_file, "MODEL_NAME", model_name)
        
        load_dotenv(override=True)

    def get_provider(self):
        return self.settings.get("provider", "gemini")

    def set_provider(self, provider):
        self.settings["provider"] = provider
        self.save_settings()

    def get_api_base_url(self):
        provider = self.get_provider()
        if provider == "ollama":
            return "http://localhost:11434/v1"
        return "https://generativelanguage.googleapis.com/v1beta/openai/"

    def get_recent_repos(self):
        return self.settings.get("recent_repos", [])

    def add_recent_repo(self, path):
        repos = self.get_recent_repos()
        if path in repos:
            repos.remove(path)
        repos.insert(0, path)
        self.settings["recent_repos"] = repos[:10]
        self.save_settings()

    def get_system_prompt(self):
        return self.settings.get("system_prompt")
    
    def set_system_prompt(self, prompt):
        self.settings["system_prompt"] = prompt
        self.save_settings()

    def get_window_geometry(self):
        return self.settings.get("window_geometry", {"width": 1000, "height": 700})

    def set_window_geometry(self, width, height):
        self.settings["window_geometry"] = {"width": width, "height": height}
        self.save_settings()
