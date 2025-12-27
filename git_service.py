import git
from git import Repo
from git.exc import InvalidGitRepositoryError

class GitService:
    def __init__(self):
        self.repo = None
        self.path = None

    def is_valid_repo(self, path):
        try:
            self.repo = Repo(path)
            self.path = path
            return True
        except InvalidGitRepositoryError:
            self.repo = None
            return False
        except Exception:
             self.repo = None
             return False

    def get_status(self):
        if not self.repo:
            return "No repository selected."
        return self.repo.git.status()

    def get_diff(self):
        if not self.repo:
            raise ValueError("Repository not initialized")
        # Get diff of staged and unstaged changes
        # HEAD vs current working directory
        try:
            return self.repo.git.diff('HEAD')
        except git.exc.GitCommandError:
             # Case for empty repo with no commits
             return self.repo.git.diff(cached=True) 

    def stage_all(self):
        if not self.repo:
             raise ValueError("Repository not initialized")
        self.repo.git.add('.')

    def commit_changes(self, message):
        if not self.repo:
             raise ValueError("Repository not initialized")
        self.repo.index.commit(message)
