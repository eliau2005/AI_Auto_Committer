from openai import OpenAI
from config import ConfigManager
from exceptions import APIKeyError, AIServiceError

class AIService:
    def __init__(self):
        self.config = ConfigManager()
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes the OpenAI client based on current config."""
        api_key = self.config.api_key
        base_url = self.config.get_api_base_url()
        
        # Ollama local usually doesn't need a key, but OpenAI client requires one.
        if self.config.get_provider() == "ollama" and not api_key:
            api_key = "ollama"
            
        if api_key:
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key,
            )
        else:
            self.client = None

    def reload_config(self):
        """Reloads configuration and re-initializes the client."""
        # Force a reload of the config manager's internal state
        self.config = ConfigManager()
        self._init_client()

    def generate_commit_message(self, diff_text):
        if not self.client:
            # If provider is ollama, client should have been init with "ollama" key
            raise APIKeyError("API Key not configured. Please check your settings.")

        if not diff_text or not diff_text.strip():
             return "Error: No changes detected to generate a message."

        # Truncation logic
        if len(diff_text) > 4000:
            diff_text = diff_text[:4000] + "\n...[Diff truncated]..."

        default_system_prompt = (
            "You are a helpful assistant that generates professional git commit messages based on diffs. "
            "Rule 1: Use the conventional commits format if applicable. "
            "Rule 2: Keep the summary line under 50 characters. "
            "Rule 3: One empty line after summary. "
            "Rule 4: Use a concise bulleted list for details in present tense."
        )
        
        system_prompt = self.config.get_system_prompt() or default_system_prompt

        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the git diff:\n\n{diff_text}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e).lower()
            if "bx" in error_str or "401" in error_str or "unauthorized" in error_str or "api key" in error_str:
                raise APIKeyError(f"Invalid or missing API Key. Server returned: {e}", original_error=e)
            raise AIServiceError(f"AI Service Error: {e}", original_error=e)
