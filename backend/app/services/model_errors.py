from app.schemas.model import ModelErrorCode


class ModelError(Exception):
    def __init__(self, code: ModelErrorCode, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
