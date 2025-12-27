import pytest
from unittest.mock import MagicMock, patch
from git_service import GitService

@pytest.fixture
def mock_git_repo():
    with patch('git_service.Repo') as MockRepo:
        yield MockRepo

def test_stage_files(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    service = GitService()
    service.repo = mock_repo_instance
    
    files_to_stage = ["file1.txt", "file2.py"]
    service.stage_files(files_to_stage)
    
    # repo.git.add should be called with the list of files
    mock_repo_instance.git.add.assert_called_with(files_to_stage)

def test_get_current_branch(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    mock_repo_instance.active_branch.name = "feature-branch"
    
    service = GitService()
    service.repo = mock_repo_instance
    
    branch = service.get_current_branch()
    assert branch == "feature-branch"

def test_push_changes(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    mock_remote = MagicMock()
    # Mock remotes to behave like a dict or have __contains__
    mock_repo_instance.remotes = {'origin': mock_remote}
    
    service = GitService()
    service.repo = mock_repo_instance
    
    service.push_changes()
    mock_remote.push.assert_called_once()

def test_pull_changes(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    mock_remote = MagicMock()
    mock_repo_instance.remotes = {'origin': mock_remote}
    
    service = GitService()
    service.repo = mock_repo_instance
    
    service.pull_changes()
    mock_remote.pull.assert_called_once()

def test_get_staged_files(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    # Mock index.diff("HEAD")
    mock_diff_item = MagicMock()
    mock_diff_item.a_path = "staged_file.py"
    mock_repo_instance.index.diff.return_value = [mock_diff_item]
    
    service = GitService()
    service.repo = mock_repo_instance
    
    staged = service.get_staged_files()
    assert "staged_file.py" in staged
    mock_repo_instance.index.diff.assert_called_with("HEAD")

def test_get_unstaged_files(mock_git_repo):
    mock_repo_instance = mock_git_repo.return_value
    # Mock index.diff(None) for unstaged
    mock_diff_item = MagicMock()
    mock_diff_item.a_path = "unstaged_file.py"
    mock_repo_instance.index.diff.return_value = [mock_diff_item]
    # Mock untracked files
    mock_repo_instance.untracked_files = ["untracked.txt"]
    
    service = GitService()
    service.repo = mock_repo_instance
    
    unstaged = service.get_unstaged_files()
    assert "unstaged_file.py" in unstaged
    assert "untracked.txt" in unstaged
