import pytest
from unittest.mock import patch, MagicMock
from ai_service import AIService

@pytest.fixture
def mock_config():
    with patch('ai_service.ConfigManager') as MockConfig:
        config_instance = MockConfig.return_value
        config_instance.api_key = "fake_key"
        config_instance.model_name = "gpt-4o-mini"
        yield config_instance

def test_generate_commit_message_success(mock_config):
    with patch('ai_service.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "feat: added new feature"
        mock_client.chat.completions.create.return_value = mock_response

        service = AIService()
        message = service.generate_commit_message("diff content")
        
        assert "feat: added new feature" in message
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify prompt construction (partial check)
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == "gpt-4o-mini"
        assert "diff content" in call_args.kwargs['messages'][1]['content']

def test_generate_commit_message_api_error(mock_config):
    with patch('ai_service.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        service = AIService()
        message = service.generate_commit_message("diff content")
        
        assert "Error generating commit message" in message

def test_truncation_logic(mock_config):
    with patch('ai_service.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "msg"
        mock_client.chat.completions.create.return_value = mock_response

        service = AIService()
        long_diff = "a" * 5000
        service.generate_commit_message(long_diff)
        
        call_args = mock_client.chat.completions.create.call_args
        sent_content = call_args.kwargs['messages'][1]['content']
        assert len(sent_content) < 5000
        assert "truncated" in sent_content or len(sent_content) <= 4000 + 100 # buffer
