import tiktoken
from enum import Enum, auto
import os

class FileCategory(Enum):
    LOGIC = auto()
    CONFIG = auto()
    DOCS = auto()
    LOCK = auto()
    IGNORED = auto()
    UNKNOWN = auto()

class TokenManager:
    def __init__(self, model="cl100k_base"):
        self.encoding = tiktoken.get_encoding(model)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def truncate_to_limit(self, text: str, limit: int) -> str:
        tokens = self.encoding.encode(text)
        if len(tokens) <= limit:
            return text
        
        truncated_tokens = tokens[:limit]
        return self.encoding.decode(truncated_tokens)

class FilePrioritizer:
    def __init__(self):
        self.category_priority = {
            FileCategory.LOGIC: 1,
            FileCategory.CONFIG: 2,
            FileCategory.DOCS: 3,
            FileCategory.UNKNOWN: 4,
            FileCategory.LOCK: 5,
            FileCategory.IGNORED: 6
        }

    def categorize_file(self, file_path: str) -> FileCategory:
        # Check for ignored directories first
        path_parts = file_path.split('/')
        if any(p in ['dist', 'tests', 'vendor', 'node_modules', '__pycache__', '.git'] for p in path_parts):
            # Special case: if tests are the only thing, we might want to include them, 
            # but for categorization they are "IGNORED" priority (lowest) or separate.
            # The spec says "Automatically deprioritize or exclude tests/".
            # Let's map them to IGNORED for now, which implies lowest priority or exclusion.
            return FileCategory.IGNORED
        
        # Check extensions
        _, ext = os.path.splitext(file_path)
        filename = os.path.basename(file_path)
        
        if filename in ['package-lock.json', 'poetry.lock', 'yarn.lock', 'Gemfile.lock', 'composer.lock']:
            return FileCategory.LOCK
            
        if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.c', '.cpp', '.java', '.rb', '.php', '.swift', '.kt']:
            return FileCategory.LOGIC
            
        if ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.xml', '.env', '.conf']:
            return FileCategory.CONFIG
            
        if ext in ['.md', '.txt', '.rst']:
            return FileCategory.DOCS
            
        if ext in ['.lock']:
             return FileCategory.LOCK

        return FileCategory.UNKNOWN

    def sort_files(self, file_paths: list[str]) -> list[str]:
        """
        Sorts file paths based on their priority category.
        """
        return sorted(file_paths, key=lambda f: self.category_priority[self.categorize_file(f)])
