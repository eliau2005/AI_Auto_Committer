class AutoCommitterError(Exception):
    """Base exception for the Auto Committer application."""
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class AIServiceError(AutoCommitterError):
    """Raised when the AI service fails to generate a response."""
    pass

class APIKeyError(AIServiceError):
    """Raised when there is an issue with the API key (missing or invalid)."""
    pass

class NetworkError(AutoCommitterError):
    """Raised when there are network connectivity issues."""
    pass
