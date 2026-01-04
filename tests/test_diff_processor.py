import pytest
from unittest.mock import MagicMock, patch
from diff_processor import DiffProcessor
from token_management import TokenManager, FilePrioritizer, FileCategory

@pytest.fixture
def diff_processor():
    tm = TokenManager()
    fp = FilePrioritizer()
    # Mock summarizer
    summarizer = MagicMock()
    processor = DiffProcessor(tm, fp, summarizer)
    return processor

def test_parse_diff(diff_processor):
    diff_text = """diff --git a/main.py b/main.py
index 123..456 100644
--- a/main.py
+++ b/main.py
@@ -1,1 +1,2 @@
-print("Hello")
+print("Hello World")
diff --git a/config.json b/config.json
index abc..def 100644
--- a/config.json
+++ b/config.json
@@ -1,1 +1,1 @@
-{"debug": false}
+{"debug": true}
"""
    chunks = diff_processor.parse_diff(diff_text)
    assert len(chunks) == 2
    assert chunks[0].filename == "main.py"
    assert chunks[1].filename == "config.json"

def test_process_diff_truncation(diff_processor):
    # Create a scenario where total tokens > limit
    # main.py (Logic) - 100 tokens
    # huge.lock (Lock) - 5000 tokens
    # Limit - 1000 tokens
    
    chunk1 = MagicMock()
    chunk1.filename = "main.py"
    chunk1.content = "logic code"
    chunk1.token_count = 100
    chunk1.category = FileCategory.LOGIC
    
    chunk2 = MagicMock()
    chunk2.filename = "huge.lock"
    chunk2.content = "lock content"
    chunk2.token_count = 5000
    chunk2.category = FileCategory.LOCK
    
    diff_processor.parse_diff = MagicMock(return_value=[chunk1, chunk2])
    diff_processor.token_manager.count_tokens = MagicMock(side_effect=[100, 5000])
    
    # Action
    processed_text, was_truncated = diff_processor.process_diff("dummy", token_limit=1000)
    
    # Assert
    assert was_truncated is True
    assert "logic code" in processed_text
    assert "lock content" not in processed_text # Should be summarized or truncated
    assert "TRUNCATED" in processed_text or "SUMMARIZED" in processed_text

def test_summarization_trigger(diff_processor):
    # Test that AI service is called for summarization
    chunk1 = MagicMock()
    chunk1.filename = "large_config.json"
    chunk1.content = "large config"
    chunk1.token_count = 2000
    chunk1.category = FileCategory.CONFIG
    
    diff_processor.parse_diff = MagicMock(return_value=[chunk1])
    diff_processor.token_manager.count_tokens = MagicMock(return_value=100) # Reduced count after summary
    diff_processor.summarizer.return_value = "Summary of config"
    
    # Limit 1000. Config > Limit. Logic -> Summarize.
    processed_text, _ = diff_processor.process_diff("dummy", token_limit=1000)
    
    assert "Summary of config" in processed_text
    diff_processor.summarizer.assert_called_once()