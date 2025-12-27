from openai import OpenAI
from config import ConfigManager

class AIService:
    def __init__(self):
        self.config = ConfigManager()
        self.client = None
        if self.config.api_key:
            self.client = OpenAI(
                base_url=self.config.api_base_url,
                api_key=self.config.api_key,
            )

    def generate_commit_message(self, diff_text):
        if not self.client:
            return "Error: API Key not configured."

        if not diff_text or not diff_text.strip():
             return "Error: No changes detected to generate a message."

        # Truncation logic
        if len(diff_text) > 4000:
            diff_text = diff_text[:4000] + "\n...[Diff truncated]..."

        system_prompt = (
            "You are a helpful assistant that generates professional git commit messages based on diffs. "
            "Rule 1: Use the conventional commits format if applicable. "
            "Rule 2: Keep the summary line under 50 characters. "
            "Rule 3: One empty line after summary. "
            "Rule 4: Use a concise bulleted list for details in present tense."
        )

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
            return f"Error generating commit message: {str(e)}"
