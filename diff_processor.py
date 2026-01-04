import re
from dataclasses import dataclass
from typing import List, Callable, Tuple
from token_management import TokenManager, FilePrioritizer, FileCategory

@dataclass
class DiffChunk:
    filename: str
    content: str
    token_count: int = 0
    category: FileCategory = FileCategory.UNKNOWN

class DiffProcessor:
    def __init__(self, token_manager: TokenManager, file_prioritizer: FilePrioritizer, summarizer: Callable[[str], str] = None):
        self.token_manager = token_manager
        self.file_prioritizer = file_prioritizer
        self.summarizer = summarizer

    def parse_diff(self, diff_text: str) -> List[DiffChunk]:
        chunks = []
        # Split by "diff --git "
        # Use a regex lookahead to keep the delimiter or just split and prepend.
        parts = diff_text.split("diff --git ")
        
        for part in parts:
            if not part.strip():
                continue
            
            content = "diff --git " + part
            
            # Extract filename
            # First line: a/path b/path
            first_line = part.splitlines()[0]
            # Heuristic: split by space, take last element, strip b/
            # This handles simple cases. Spaces in filenames might fail this simple check.
            # But git diff output usually quotes filenames with spaces?
            # Let's look for " b/" pattern.
            
            file_path = "unknown"
            # Try to find " b/"
            b_index = first_line.find(" b/")
            if b_index != -1:
                file_path = first_line[b_index+3:].strip()
            else:
                # Fallback
                tokens = first_line.split()
                if len(tokens) >= 2:
                    file_path = tokens[-1].lstrip("b/")
            
            # Count tokens
            count = self.token_manager.count_tokens(content)
            cat = self.file_prioritizer.categorize_file(file_path)
            
            chunks.append(DiffChunk(filename=file_path, content=content, token_count=count, category=cat))
            
        return chunks

    def process_diff(self, diff_text: str, token_limit: int = 4000) -> Tuple[str, bool]:
        chunks = self.parse_diff(diff_text)
        total_tokens = sum(c.token_count for c in chunks)
        
        if total_tokens <= token_limit:
            return diff_text, False

        # Order of categories to sacrifice: IGNORED -> LOCK -> UNKNOWN -> DOCS -> CONFIG -> LOGIC
        # We leave LOGIC out of this blind sacrifice loop so it can be handled by proportional budgeting
        # to ensure we don't just wipe out the first logic file we see.
        sacrifice_order = [
            FileCategory.IGNORED,
            FileCategory.LOCK,
            FileCategory.UNKNOWN,
            FileCategory.DOCS,
            FileCategory.CONFIG
        ]
        
        current_tokens = total_tokens
        
        for category in sacrifice_order:
            if current_tokens <= token_limit:
                break
                
            target_chunks = [c for c in chunks if c.category == category]
            # Sort by size (largest first) to make biggest impact
            target_chunks.sort(key=lambda c: c.token_count, reverse=True)
            
            for chunk in target_chunks:
                if current_tokens <= token_limit:
                    break
                
                # Summarize
                if self.summarizer:
                    try:
                        summary = self.summarizer(chunk.content)
                        new_content = f"diff --git {chunk.filename} [SUMMARIZED]\n{summary}\n"
                    except Exception:
                        new_content = f"diff --git {chunk.filename} [TRUNCATED]\n...Diff too large and summarization failed...\n"
                else:
                    new_content = f"diff --git {chunk.filename} [TRUNCATED]\n...Diff too large...\n"
                
                new_count = self.token_manager.count_tokens(new_content)
                
                # Only apply if it saves space
                if new_count < chunk.token_count:
                    diff = chunk.token_count - new_count
                    chunk.content = new_content
                    chunk.token_count = new_count
                    current_tokens -= diff

        # If still over limit, apply proportional budgeting
        if current_tokens > token_limit:
            # We need to reduce current_tokens to token_limit.
            # We should target ALL chunks to share the burden, or perhaps just the remaining "full" chunks.
            # But simpler to budget everyone proportional to their current size.
            
            # Calculate total size of all chunks currently
            total_current_size = sum(c.token_count for c in chunks)
            
            # This should equal current_tokens, but let's be safe
            if total_current_size == 0:
                 return "", True # Should not happen if over limit

            # Allocate budget
            for chunk in chunks:
                # ratio = chunk_size / total_current_size
                # budget = token_limit * ratio
                ratio = chunk.token_count / total_current_size
                budget = int(token_limit * ratio)
                
                # Ensure at least some budget (e.g. header) if possible, but strict limit applies.
                # If budget is smaller than current, truncate.
                if budget < chunk.token_count:
                    # Truncate content
                    # We need to be careful not to corrupt headers if possible, 
                    # but TokenManager.truncate_to_limit is raw text truncation.
                    chunk.content = self.token_manager.truncate_to_limit(chunk.content, budget)
                    chunk.content += "\n...[Truncated]..."
                    chunk.token_count = self.token_manager.count_tokens(chunk.content)

        # Reconstruct
        final_text = "\n".join([c.content for c in chunks])
        
        # Final safety check (hard truncate if somehow still over, e.g. due to "...[Truncated]..." additions)
        # But allow a small buffer if needed, or just hard cut.
        # The spec implies strict enforcement.
        final_count = self.token_manager.count_tokens(final_text)
        if final_count > token_limit:
             final_text = self.token_manager.truncate_to_limit(final_text, token_limit)
             final_text += "\n...[Remaining Diff Truncated]..."
            
        return final_text, True
