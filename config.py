import os
from dotenv import load_dotenv

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
