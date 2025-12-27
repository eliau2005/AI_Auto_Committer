import os
from dotenv import load_dotenv, set_key

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")

    def validate(self):
        if not self.api_key:
            return False, "GEMINI_API_KEY not found in environment variables."
        return True, "Configuration valid."

    def update_credentials(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        
        # Persist to .env
        env_file = ".env"
        if not os.path.exists(env_file):
            open(env_file, 'w').close()
            
        set_key(env_file, "GEMINI_API_KEY", api_key)
        set_key(env_file, "MODEL_NAME", model_name)
        
        # Reload env vars to be safe
        load_dotenv(override=True)
