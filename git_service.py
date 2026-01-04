import git
from git import Repo
from git.exc import InvalidGitRepositoryError
import os

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
        
        diff_output = []
        
        # Split files into tracked and untracked
        tracked_files = []
        untracked_files = []
        
        all_untracked = set(self.repo.untracked_files)
        
        if files:
            for f in files:
                if f in all_untracked:
                    untracked_files.append(f)
                else:
                    tracked_files.append(f)
        else:
            # If no files specified, get everything? 
            # Usually get_diff is called with specific files in this app
            tracked_files = [] # standard diff will capture modified
            untracked_files = [] # we might miss untracked if not explicitly requested?
            # For now, rely on 'files' arg being populated by UI
            pass

        # 1. Get standard diff for tracked files
        if tracked_files or not files:
            try:
                args = ['HEAD']
                if tracked_files:
                    args.extend(['--', *tracked_files])
                
                # Check if this is an initial commit scenario (HEAD invalid)
                try:
                    std_diff = self.repo.git.diff(*args)
                    if std_diff: diff_output.append(std_diff)
                except git.exc.GitCommandError:
                     # Initial commit, try cached
                     args = []
                     if tracked_files:
                         args.extend(['--', *tracked_files])
                     std_diff = self.repo.git.diff(cached=True, *args)
                     if std_diff: diff_output.append(std_diff)
            except Exception as e:
                print(f"Error getting standard diff: {e}")

        # 2. Generate pseudo-diff for untracked files
        # os is imported at top level now
        for f_path in untracked_files:
            try:
                full_path = os.path.join(self.repo.working_dir, f_path)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.readlines()
                        
                    # Format as git diff
                    diff_output.append(f"diff --git a/{f_path} b/{f_path}")
                    diff_output.append(f"new file mode 100644")
                    diff_output.append(f"--- /dev/null")
                    diff_output.append(f"+++ b/{f_path}")
                    diff_output.append(f"@@ -0,0 +1,{len(content)} @@")
                    for line in content:
                        diff_output.append(f"+{line.rstrip()}")
            except Exception as e:
                print(f"Error reading untracked file {f_path}: {e}")

        return "\n".join(diff_output)

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


