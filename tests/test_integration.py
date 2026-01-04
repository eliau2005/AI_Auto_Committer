import pytest
import os
import shutil
import tempfile
from git import Repo
from unittest.mock import patch, MagicMock
from git_service import GitService
from ai_service import AIService

@pytest.fixture
def temp_git_repo():
    # Create temp dir
    temp_dir = tempfile.mkdtemp()
    
    # Init git repo
    repo = Repo.init(temp_dir)
    
    # Create a file
    file_path = os.path.join(temp_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("Initial content")
    
    # Commit initial
    repo.index.add([file_path])
    repo.index.commit("Initial commit")
    
    # Make a change
    with open(file_path, "w") as f:
        f.write("Modified content")
    
    # Close repo handle from init
    repo.close()

    yield temp_dir
    
    # Cleanup with retry/ignore errors for Windows
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_full_flow_integration(temp_git_repo):
    # Setup Services with Mocks
    git_service = GitService()
    
    # Mock Config to ensure API Key exists (so client is created)
    with patch('ai_service.ConfigManager') as MockConfig, \
         patch('ai_service.OpenAI') as MockOpenAI:
        
        # Configure Config Mock
        config_instance = MockConfig.return_value
        config_instance.api_key = "test_key"
        config_instance.model_name = "test_model"
        
        # Configure OpenAI Mock
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "feat: updated test file"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Init AI Service (using mocks)
        ai_service = AIService()
        
        # 1. Select Repo
        assert git_service.is_valid_repo(temp_git_repo) is True
        
        # 2. Get Diff
        diff = git_service.get_diff()
        assert "Modified content" in diff
        
        # 3. Generate Message
        message, truncated = ai_service.generate_commit_message(diff)
        assert message == "feat: updated test file"
        assert truncated is False
        
    # 4. Commit
    git_service.stage_all()
    git_service.commit_changes(message)
    
    # Verify commit
    repo = Repo(temp_git_repo)
    last_commit = repo.head.commit
    assert last_commit.message.strip() == "feat: updated test file"
    assert not repo.is_dirty() # Working tree clean
    
    # Close handles
    repo.close()
    if git_service.repo:
        git_service.repo.close()
