import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

    def validate(self):
        if not self.api_key:
            return False, "API_KEY not found in environment variables."
        return True, "Configuration valid."
