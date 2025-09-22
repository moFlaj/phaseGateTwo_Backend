class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ResourceExistsException(Exception):
    def __init__(self, message):
        super().__init__(message)
