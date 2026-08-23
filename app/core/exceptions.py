class AppException(Exception):
    """Base exception for application domain errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class FileValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class TranscriptionError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=502)