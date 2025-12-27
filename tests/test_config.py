import os
import pytest
from unittest.mock import patch, mock_open
from config import ConfigManager

# Mock load_dotenv to prevent reading real .env file
@pytest.fixture(autouse=True)
def mock_load_dotenv():
    with patch('config.load_dotenv'):
        yield

# Test 1: Load from .env
def test_load_config_from_env():
    with patch.dict(os.environ, {"API_KEY": "test_key", "MODEL_NAME": "test_model"}):
        config = ConfigManager()
        assert config.api_key == "test_key"
        assert config.model_name == "test_model"

# Test 2: Missing config file/env variables (default values or error)
def test_missing_api_key():
    with patch.dict(os.environ, {}, clear=True):
        config = ConfigManager()
        # Depending on implementation, might raise error or return None. 
        # Spec implies need for config, so let's expect None or validation failure.
        assert config.api_key is None 

# Test 3: Default values
def test_default_values():
    with patch.dict(os.environ, {"API_KEY": "key"}, clear=True):
        config = ConfigManager()
        assert config.model_name == "gpt-4o-mini" # Assuming default from spec example

