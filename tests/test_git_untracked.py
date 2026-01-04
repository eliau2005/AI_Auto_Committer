import unittest
from unittest.mock import MagicMock, patch, mock_open
from git_service import GitService

class TestGitUntracked(unittest.TestCase):
    def setUp(self):
        self.service = GitService()
        self.service.repo = MagicMock()
        self.service.repo.untracked_files = ["new_file.txt"]
        self.service.repo.working_dir = "/repo"
        
        # Default git diff returns empty for tracked checks
        self.service.repo.git.diff.side_effect = lambda *args, **kwargs: ""

    @patch("git_service.os")
    def test_get_diff_untracked_only(self, mock_os):
        # Setup mocks
        mock_os.path.join.side_effect = lambda a, b: f"{a}/{b}"
        mock_os.path.exists.return_value = True
        mock_os.path.isfile.return_value = True
        
        # Mock open
        with patch("builtins.open", mock_open(read_data="line1\nline2")) as m:
            diff = self.service.get_diff(files=["new_file.txt"])
            
        print(f"DEBUG DIFF: {diff}")
        
        self.assertIn("diff --git a/new_file.txt b/new_file.txt", diff)
        self.assertIn("new file mode 100644", diff)
        self.assertIn("+line1", diff)
        self.assertIn("+line2", diff)

    @patch("git_service.os")
    def test_get_diff_mixed(self, mock_os):
        # Setup mocks
        mock_os.path.join.side_effect = lambda a, b: f"{a}/{b}"
        mock_os.path.exists.return_value = True
        mock_os.path.isfile.return_value = True
        
        # Tracked file diff
        self.service.repo.git.diff.side_effect = lambda *args, **kwargs: "diff --git a/tracked.txt..." if "tracked.txt" in args else ""
        
        with patch("builtins.open", mock_open(read_data="new content")):
            diff = self.service.get_diff(files=["tracked.txt", "new_file.txt"])
            
        self.assertIn("diff --git a/tracked.txt", diff)
        self.assertIn("diff --git a/new_file.txt", diff)

if __name__ == '__main__':
    unittest.main()
