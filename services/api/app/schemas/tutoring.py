from uuid import UUID

from pydantic import BaseModel, Field


class SendTutoringMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
    client_request_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")


class SendTutoringMessageResponse(BaseModel):
    student_message_id: UUID
    assistant_message_id: UUID
    assistant_status: str
    assistant_content: str
    duplicate: bool
