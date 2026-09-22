from datetime import datetime
from enum import IntEnum, StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class MisconceptionCategory(StrEnum):
    NONE_DETECTED = "none_detected"
    CONCEPTUAL_CONFUSION = "conceptual_confusion"
    OFF_BY_ONE_OR_BOUNDARY = "off_by_one_or_boundary"
    LOGICAL_INVERSION = "logical_inversion"
    INCOMPLETE_REASONING = "incomplete_reasoning"
    SYNTAX_OR_TYPE = "syntax_or_type"
    FRUSTRATION_OR_STUCK = "frustration_or_stuck"


class StudentCognitiveState(StrEnum):
    EXPLORING = "exploring"
    MAKING_PROGRESS = "making_progress"
    STRUGGLING = "struggling"
    STUCK = "stuck"
    MASTERED = "mastered"


class HintLevel(IntEnum):
    SOCRATIC_PROBE = 0
    CONCEPTUAL_POINTER = 1
    STRATEGIC_HINT = 2
    DECOMPOSITION_BREAKDOWN = 3
    WORKED_ANALOGY = 4
    BOTTOM_OUT_WALKTHROUGH = 5


class SessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"


class MessageRole(StrEnum):
    STUDENT = "student"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DiagnosticAssessment(BaseModel):
    cognitive_state: StudentCognitiveState = StudentCognitiveState.EXPLORING
    misconception: MisconceptionCategory = MisconceptionCategory.NONE_DETECTED
    struggle_score: float = Field(0.0, ge=0.0, le=1.0)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    key_signals: list[str] = Field(default_factory=list)
    suggested_hint_level: HintLevel = HintLevel.SOCRATIC_PROBE
    pedagogical_focus: str = Field("", description="Recommended focus for the tutor turn")


class CreateTutoringSessionRequest(BaseModel):
    classroom_id: UUID
    learning_objective: str = Field(min_length=1, max_length=500)


class TutoringSessionResponse(BaseModel):
    id: UUID
    classroom_id: UUID
    student_id: UUID
    learning_objective: str | None
    status: SessionStatus
    hints_used: int
    attempts: int
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SessionMessage(BaseModel):
    id: UUID
    session_id: UUID
    author_user_id: UUID | None
    role: MessageRole
    content: str
    sequence_number: int
    hint_level: HintLevel | None
    created_at: datetime


class TutoringTurnRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class TutoringTurnResponse(BaseModel):
    session_id: UUID
    student_message: SessionMessage
    assistant_message: SessionMessage
    diagnostic: DiagnosticAssessment
    current_hint_level: HintLevel
    attempts: int
    hints_used: int
    status: SessionStatus


class RequestHintResponse(BaseModel):
    session_id: UUID
    assistant_message: SessionMessage
    hint_level: HintLevel
    hints_used: int
    status: SessionStatus


class EndSessionRequest(BaseModel):
    status: SessionStatus = SessionStatus.COMPLETED


class SessionSummaryResponse(BaseModel):
    session_id: UUID
    classroom_id: UUID
    learning_objective: str | None
    status: SessionStatus
    total_turns: int
    attempts: int
    hints_used: int
    max_hint_level_reached: HintLevel
    identified_misconceptions: list[MisconceptionCategory]
    started_at: datetime
    ended_at: datetime | None
