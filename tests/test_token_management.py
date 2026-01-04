import pytest
from unittest.mock import MagicMock
from token_management import TokenManager, FilePrioritizer, FileCategory

class TestTokenManager:
    def test_count_tokens(self):
        # Setup
        tm = TokenManager(model="cl100k_base")
        text = "Hello world"
        
        # Action
        count = tm.count_tokens(text)
        
        # Assert
        # "Hello world" is typically 2 tokens in cl100k_base (Hello, space+world) or similar.
        # We verify it returns a positive integer close to expected.
        assert isinstance(count, int)
        assert count > 0

    def test_truncate_to_limit(self):
        # Setup
        tm = TokenManager()
        text = "word " * 100 # 100 words
        limit = 10
        
        # Action
        truncated = tm.truncate_to_limit(text, limit)
        
        # Assert
        assert tm.count_tokens(truncated) <= limit
        assert len(truncated) < len(text)

class TestFilePrioritizer:
    def test_categorize_logic_file(self):
        fp = FilePrioritizer()
        assert fp.categorize_file("main.py") == FileCategory.LOGIC
        assert fp.categorize_file("script.js") == FileCategory.LOGIC
        assert fp.categorize_file("src/utils.ts") == FileCategory.LOGIC

    def test_categorize_config_file(self):
        fp = FilePrioritizer()
        assert fp.categorize_file("config.json") == FileCategory.CONFIG
        assert fp.categorize_file("docker-compose.yml") == FileCategory.CONFIG

    def test_categorize_lock_file(self):
        fp = FilePrioritizer()
        assert fp.categorize_file("poetry.lock") == FileCategory.LOCK
        assert fp.categorize_file("package-lock.json") == FileCategory.LOCK

    def test_categorize_ignored_file(self):
        fp = FilePrioritizer()
        assert fp.categorize_file("dist/bundle.js") == FileCategory.IGNORED
        assert fp.categorize_file("tests/test_app.py") == FileCategory.IGNORED

    def test_sort_files(self):
        fp = FilePrioritizer()
        files = [
            "poetry.lock",
            "README.md",
            "main.py",
            "config.json"
        ]
        
        sorted_files = fp.sort_files(files)
        
        # Expected order: Logic (main.py) -> Config (config.json) -> Docs (README.md) -> Lock (poetry.lock)
        # Note: README.md might be DOCS.
        
        assert sorted_files[0] == "main.py"
        assert sorted_files[1] == "config.json"
        # The exact order of docs vs config depends on implementation, but Lock should be last.
        assert sorted_files[-1] == "poetry.lock"
