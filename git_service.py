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

    def get_diff(self, files=None):
        if not self.repo:
            raise ValueError("Repository not initialized")
        # Get diff of staged and unstaged changes
        # HEAD vs current working directory
        try:
            args = ['HEAD']
            if files:
                args.extend(['--', *files])
            return self.repo.git.diff(*args)
        except git.exc.GitCommandError:
             # Case for empty repo with no commits
             args = []
             if files:
                 args.extend(['--', *files])
             return self.repo.git.diff(cached=True, *args)

    def stage_all(self):
        if not self.repo:
             raise ValueError("Repository not initialized")
        self.repo.git.add('.')

    def commit_changes(self, message):
        if not self.repo:
             raise ValueError("Repository not initialized")
        self.repo.index.commit(message)

    def stage_files(self, files):
        if not self.repo:
             raise ValueError("Repository not initialized")
        self.repo.git.add(files)

    def get_current_branch(self):
        if not self.repo:
             return "Unknown"
        try:
            return self.repo.active_branch.name
        except TypeError:
            return "Detached HEAD"

    def push_changes(self, remote_name="origin"):
        if not self.repo:
             raise ValueError("Repository not initialized")
        # Check if remote exists
        if remote_name in self.repo.remotes:
            self.repo.remotes[remote_name].push()
        else:
            raise ValueError(f"Remote '{remote_name}' not found")

    def pull_changes(self, remote_name="origin"):
        if not self.repo:
             raise ValueError("Repository not initialized")
        if remote_name in self.repo.remotes:
            self.repo.remotes[remote_name].pull()
        else:
             raise ValueError(f"Remote '{remote_name}' not found")

    def get_changed_files(self):
        """Returns a list of changed files (staged + unstaged/untracked)"""
        if not self.repo:
            return []
        
        changed_files = set()
        # Unstaged
        changed_files.update([item.a_path for item in self.repo.index.diff(None)])
        # Staged
        changed_files.update([item.a_path for item in self.repo.index.diff("HEAD")])
        # Untracked
        changed_files.update(self.repo.untracked_files)
        
        return list(changed_files)

    def get_staged_files(self):
        if not self.repo:
            return []
        return [item.a_path for item in self.repo.index.diff("HEAD")]

    def get_unstaged_files(self):
        if not self.repo:
            return []
        unstaged = [item.a_path for item in self.repo.index.diff(None)]
        unstaged.extend(self.repo.untracked_files)
        return unstaged


