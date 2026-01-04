import unittest
from unittest.mock import MagicMock
from ai_service import AIService
from config import ConfigManager

class TestAISeparation(unittest.TestCase):
    def setUp(self):
        self.ai = AIService()
        self.ai.client = MagicMock()
        self.ai.config = MagicMock(spec=ConfigManager)
        self.ai.config.model_name = "test-model"
        self.ai.config.get_system_prompt.return_value = None

    def test_generate_commit_message_with_separator(self):
        # Mock successful structured response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Feat: Add login|||SEP|||- Added auth middleware\n- Updated user schema"
        self.ai.client.chat.completions.create.return_value = mock_response

        title, desc, truncated = self.ai.generate_commit_message("diff data")
        
        self.assertEqual(title, "Feat: Add login")
        self.assertEqual(desc, "- Added auth middleware\n- Updated user schema")
        self.assertFalse(truncated)

    def test_generate_commit_message_fallback_no_separator(self):
        # Mock response without separator (old model behavior)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Feat: Add login\n\n- Added auth middleware"
        self.ai.client.chat.completions.create.return_value = mock_response

        title, desc, truncated = self.ai.generate_commit_message("diff data")
        
        self.assertEqual(title, "Feat: Add login")
        self.assertEqual(desc, "- Added auth middleware")

    def test_generate_commit_message_empty(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = ""
        self.ai.client.chat.completions.create.return_value = mock_response

        title, desc, truncated = self.ai.generate_commit_message("diff data")
        
        self.assertEqual(title, "")
        self.assertEqual(desc, "")

if __name__ == '__main__':
    unittest.main()
