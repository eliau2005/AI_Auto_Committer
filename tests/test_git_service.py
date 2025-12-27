import pytest
from unittest.mock import MagicMock, patch
from git_service import GitService

@pytest.fixture
def mock_git_repo():
    with patch('git_service.Repo') as MockRepo:
        yield MockRepo

def test_is_valid_repo_valid(mock_git_repo):
    mock_git_repo.side_effect = None # Successful init
    service = GitService()
    assert service.is_valid_repo("/path/to/repo") is True

def test_is_valid_repo_invalid(mock_git_repo):
    from git.exc import InvalidGitRepositoryError
    mock_git_repo.side_effect = InvalidGitRepositoryError
    service = GitService()
    assert service.is_valid_repo("/path/to/repo") is False

def test_get_diff(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    mock_repo_instance.git.diff.return_value = "diff content"
    
    service = GitService()
    service.repo = mock_repo_instance # simulate initialized repo
    
    diff = service.get_diff()
    assert diff == "diff content"
    mock_repo_instance.git.diff.assert_called_with('HEAD') # or just diff depending on logic

def test_stage_all(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    service = GitService()
    service.repo = mock_repo_instance
    
    service.stage_all()
    mock_repo_instance.git.add.assert_called_with('.')

def test_commit_changes(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    service = GitService()
    service.repo = mock_repo_instance
    
    service.commit_changes("Initial commit")
    mock_repo_instance.index.commit.assert_called_with("Initial commit")

