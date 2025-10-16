class AppError(Exception):
    def __init__(self, message: str | None = None):
        super().__init__(message or self.__class__.__name__)


class StorageServiceError(AppError):
    """Error interacting with S3 or storage layer."""
    pass
