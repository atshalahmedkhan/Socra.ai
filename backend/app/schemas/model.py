from enum import StrEnum

from pydantic import BaseModel, Field


class ModelErrorCode(StrEnum):
    TIMEOUT = "MODEL_TIMEOUT"
    UNAVAILABLE = "MODEL_UNAVAILABLE"
    AUTHENTICATION_FAILED = "MODEL_AUTHENTICATION_FAILED"
    INVALID_RESPONSE = "MODEL_INVALID_RESPONSE"
    NOT_LOADED = "MODEL_NOT_LOADED"
    POLICY_REJECTED = "MODEL_POLICY_REJECTED"
    CIRCUIT_OPEN = "MODEL_CIRCUIT_OPEN"
    CONFIGURATION_ERROR = "MODEL_CONFIGURATION_ERROR"


class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=20000)


class ModelGenerationRequest(BaseModel):
    session_id: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)
    requested_model: str | None = None
    max_output_tokens: int | None = Field(None, ge=1, le=2048)
    temperature: float | None = Field(None, ge=0, le=2)
    top_p: float | None = Field(None, gt=0, le=1)


class ModelGenerationResult(BaseModel):
    content: str
    model_name: str
    model_version: str
    prompt_version: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    total_latency_ms: int
    time_to_first_token_ms: int | None = None
    generation_latency_ms: int | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    retry_count: int = 0
    provider_endpoint: str
    finish_reason: str | None = None
