import pytest
from unittest.mock import MagicMock, patch
from ai_service import AIService
from exceptions import APIKeyError

@pytest.fixture
def mock_config():
    with patch('ai_service.ConfigManager') as MockConfig:
        instance = MockConfig.return_value
        instance.api_key = "test_key"
        instance.get_provider.return_value = "gemini"
        instance.get_api_base_url.return_value = "https://mock.url"
        instance.model_name = "mock-model"
        instance.get_system_prompt.return_value = None
        yield instance

@pytest.fixture
def mock_openai():
    with patch('ai_service.OpenAI') as MockOpenAI:
        yield MockOpenAI

def test_ollama_init_no_key(mock_config, mock_openai):
    mock_config.api_key = None
    mock_config.get_provider.return_value = "ollama"
    mock_config.get_api_base_url.return_value = "http://localhost:11434"
    
    service = AIService()
    
    # Should init client with fake key "ollama"
    mock_openai.assert_called_with(base_url="http://localhost:11434", api_key="ollama")
    assert service.client is not None

def test_custom_system_prompt(mock_config, mock_openai):
    mock_config.get_system_prompt.return_value = "Custom System Prompt"
    service = AIService()
    
    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Commit message"
    service.client.chat.completions.create.return_value = mock_response
    
    service.generate_commit_message("diff")
    
    # Check if system prompt was used
    call_args = service.client.chat.completions.create.call_args
    assert call_args is not None
    messages = call_args[1]['messages']
    assert messages[0]['content'] == "Custom System Prompt"

def test_default_system_prompt(mock_config, mock_openai):
    mock_config.get_system_prompt.return_value = None
    service = AIService()
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Commit message"
    service.client.chat.completions.create.return_value = mock_response
    
    service.generate_commit_message("diff")
    
    call_args = service.client.chat.completions.create.call_args
    messages = call_args[1]['messages']
    assert "Rule 1" in messages[0]['content']
