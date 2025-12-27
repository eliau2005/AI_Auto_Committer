import pytest
import os
import json
from unittest.mock import patch, mock_open
from config import ConfigManager

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key", "MODEL_NAME": "test-model"}):
        yield

def test_load_defaults(mock_env):
    # Mock os.path.exists to return False so it exercises the default path
    with patch("os.path.exists", return_value=False):
        # We don't need to patch open if exists returns False (unless load_dotenv calls it)
        # But load_dotenv is called in __init__. Let's mock load_dotenv to avoid it hitting filesystem/open
        with patch("config.load_dotenv"):
             config = ConfigManager()
             assert config.get_provider() == "gemini" # Default
             assert config.get_recent_repos() == []

def test_load_settings_json(mock_env):
    settings_data = {
        "recent_repos": ["/path/one"],
        "provider": "ollama",
        "system_prompt": "Custom Prompt"
    }
    # Mock open to return json data
    with patch("builtins.open", mock_open(read_data=json.dumps(settings_data))):
        # Mock exists to return True
        with patch("os.path.exists", return_value=True):
             with patch("config.load_dotenv"):
                 config = ConfigManager()
                 assert config.get_provider() == "ollama"
                 assert config.get_recent_repos() == ["/path/one"]
                 assert config.get_system_prompt() == "Custom Prompt"

def test_add_recent_repo(mock_env):
    with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
        with patch("os.path.exists", return_value=True):  
             with patch("json.dump") as mock_json_dump:
                with patch("config.load_dotenv"):
                    config = ConfigManager()
                    config.settings = {"recent_repos": []} # Force empty
                    
                    config.add_recent_repo("/new/repo")
                    
                    assert config.get_recent_repos() == ["/new/repo"]
                    mock_json_dump.assert_called()

def test_provider_url_logic(mock_env):
    # Test that provider returns correct base_url
    with patch("os.path.exists", return_value=False):
        with patch("config.load_dotenv"):
            config = ConfigManager()
            # Default Gemini
            assert "googleapis" in config.get_api_base_url()
            
            # Switch to Ollama
            config.set_provider("ollama")
            assert "localhost" in config.get_api_base_url()
