import pytest
from unittest.mock import MagicMock, patch
from ai_service import AIService
from exceptions import APIKeyError

@pytest.fixture
def mock_openai_client():
    with patch('ai_service.OpenAI') as mock:
        yield mock

@pytest.fixture
def ai_service(mock_openai_client):
    # Mock ConfigManager to return a dummy API key so client inits
    with patch('ai_service.ConfigManager') as MockConfig:
        config_instance = MockConfig.return_value
        config_instance.api_key = "dummy_key"
        config_instance.get_api_base_url.return_value = "https://api.openai.com/v1"
        config_instance.get_provider.return_value = "openai"
        config_instance.model_name = "gpt-4"
        
        service = AIService()
        return service

def test_generate_commit_message_uses_diff_processor(ai_service):
    # We want to verify that DiffProcessor is used.
    # We can mock DiffProcessor class in ai_service module
    
    with patch('ai_service.DiffProcessor') as MockProcessor:
        mock_instance = MockProcessor.return_value
        mock_instance.process_diff.return_value = ("Processed Diff", True)
        
        # Mock client chat completion
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Commit Message"
        ai_service.client.chat.completions.create.return_value = mock_completion
        
        diff = "raw diff"
        msg, truncated = ai_service.generate_commit_message(diff)
        
        # Verify DiffProcessor was initialized
        MockProcessor.assert_called_once()
        
        # Verify process_diff was called with token_limit=4000
        mock_instance.process_diff.assert_called_once_with(diff, token_limit=4000)
        
        # Verify the result from process_diff was sent to AI
        call_args = ai_service.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_content = messages[1]['content']
        assert "Processed Diff" in user_content
        
        assert msg == "Commit Message"
        assert truncated is True

def test_summarize_file_diff_integration(ai_service):
    # Test that summarize_file_diff calls the AI client
    
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "Summary of file"
    ai_service.client.chat.completions.create.return_value = mock_completion
    
    summary = ai_service.summarize_file_diff("diff content")
    
    assert summary == "Summary of file"
    
    # Verify call arguments
    call_args = ai_service.client.chat.completions.create.call_args
    messages = call_args[1]['messages']
    system_prompt = messages[0]['content']
    
    assert "Summarize the following git diff" in system_prompt

def test_summarize_file_diff_fallback(ai_service):
    # Test error handling
    ai_service.client.chat.completions.create.side_effect = Exception("API Error")
    
    summary = ai_service.summarize_file_diff("diff content")
    
    assert summary == "Summary generation failed."
