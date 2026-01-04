import pytest
from diff_processor import DiffProcessor, DiffChunk
from token_management import TokenManager, FilePrioritizer, FileCategory
from unittest.mock import MagicMock

class MockTokenManager:
    def count_tokens(self, text: str) -> int:
        return len(text) # Simple 1 char = 1 token for easy math

    def truncate_to_limit(self, text: str, limit: int) -> str:
        return text[:limit]

@pytest.fixture
def diff_processor():
    token_manager = MockTokenManager()
    file_prioritizer = FilePrioritizer()
    return DiffProcessor(token_manager, file_prioritizer)

def test_sacrifice_order(diff_processor):
    # Setup chunks with different categories
    # Order should be: IGNORED -> LOCK -> UNKNOWN -> DOCS -> CONFIG -> LOGIC
    
    # We will simulate a situation where we need to sacrifice to meet the limit.
    # Total size = 600. Limit = 550. Need to save 50.
    
    chunks = [
        DiffChunk(filename="logic.py", content="L" * 100, token_count=100, category=FileCategory.LOGIC),
        DiffChunk(filename="config.yml", content="C" * 100, token_count=100, category=FileCategory.CONFIG),
        DiffChunk(filename="doc.md", content="D" * 100, token_count=100, category=FileCategory.DOCS),
        DiffChunk(filename="unknown.xyz", content="U" * 100, token_count=100, category=FileCategory.UNKNOWN),
        DiffChunk(filename="lock.lock", content="K" * 100, token_count=100, category=FileCategory.LOCK),
        DiffChunk(filename="ignore.tmp", content="I" * 100, token_count=100, category=FileCategory.IGNORED),
    ]
    
    # Mock parse_diff to return our chunks
    diff_processor.parse_diff = MagicMock(return_value=chunks)
    
    # We mock summarizer to reduce size to 10
    diff_processor.summarizer = MagicMock(return_value="SUMMARY") 
    
    # If we set limit to 550, we need to reduce 50 tokens.
    # The first victim should be IGNORED.
    # Reducing IGNORED from 100 to ~20-30 (header + summary) should start satisfying the limit.
    
    # Let's set the limit such that we need to sacrifice up to UNKNOWN.
    # Total = 600.
    # Sacrifice IGNORED -> saves ~70 (becomes ~30) -> Total ~530
    # Sacrifice LOCK -> saves ~70 (becomes ~30) -> Total ~460
    # Sacrifice UNKNOWN -> saves ~70 (becomes ~30) -> Total ~390
    
    # Set limit to 450.
    # This should trigger sacrifice of IGNORED, LOCK, and UNKNOWN.
    # DOCS, CONFIG, LOGIC should remain untouched (full content).
    
    final_text, truncated = diff_processor.process_diff("dummy", token_limit=450)
    
    assert truncated is True
    
    # Verify contents in final text
    # Untouched
    assert "L" * 100 in final_text
    assert "C" * 100 in final_text
    assert "D" * 100 in final_text
    
    # Sacrificed (Summarized or Truncated)
    # Since we have a summarizer, they should be summarized.
    # We expect the content to NOT contain the full text "I"*100
    assert "I" * 100 not in final_text
    assert "K" * 100 not in final_text
    assert "U" * 100 not in final_text
    
    assert "ignore.tmp [SUMMARIZED]" in final_text
    assert "lock.lock [SUMMARIZED]" in final_text
    assert "unknown.xyz [SUMMARIZED]" in final_text

def test_proportional_budgeting(diff_processor):
    # Test that when we still need to cut after sacrificing categories,
    # we cut proportionally from the remaining logic files instead of wiping one out.
    
    # Setup: 2 Logic files.
    # File A: 1000 tokens
    # File B: 1000 tokens
    # Limit: 1000 tokens total.
    
    chunks = [
        DiffChunk(filename="a.py", content="diff --git a.py\n" + "A" * 984, token_count=1000, category=FileCategory.LOGIC),
        DiffChunk(filename="b.py", content="diff --git b.py\n" + "B" * 984, token_count=1000, category=FileCategory.LOGIC),
    ]
    
    diff_processor.parse_diff = MagicMock(return_value=chunks)
    
    # Disable summarizer to force truncation/budgeting logic if implemented
    # Or keep it, but assume summarization is skipped for LOGIC if we want to test budgeting on raw text
    # The spec says "Cap each file's tokens proportionally".
    # If summarizer is None, it should fall back to truncation.
    diff_processor.summarizer = None
    
    final_text, truncated = diff_processor.process_diff("dummy", token_limit=1000)
    
    # Both should be present but truncated.
    # Ideally split 500/500 roughly.
    
    assert "diff --git a.py" in final_text
    assert "diff --git b.py" in final_text
    
    # Check that neither is completely empty (other than header) or completely full
    # A simple check is that we have roughly half of A and half of B
    
    count_a = final_text.count("A")
    count_b = final_text.count("B")
    
    assert count_a > 0
    assert count_b > 0
    assert count_a < 1000
    assert count_b < 1000
    
    # Allow some wiggle room for headers
    assert abs(count_a - count_b) < 200 
