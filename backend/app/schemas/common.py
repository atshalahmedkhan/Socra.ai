from pydantic import BaseModel


class PageMetadata(BaseModel):
    limit: int = 20
    next_cursor: str | None = None


class OperationSuccess(BaseModel):
    success: bool = True
