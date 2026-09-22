from uuid import UUID

from app.core.errors import APIError
from app.repositories.tutoring_session_repository import TutoringSessionRepository
from app.schemas.model import ChatMessage, ModelGenerationRequest
from app.schemas.remediation import (
    DiagnosticAssessment,
    EndSessionRequest,
    HintLevel,
    MessageRole,
    MisconceptionCategory,
    RequestHintResponse,
    SessionMessage,
    SessionStatus,
    SessionSummaryResponse,
    StudentCognitiveState,
    TutoringSessionResponse,
    TutoringTurnResponse,
)
from app.services.diagnostic_engine import DiagnosticEngine
from app.services.model_gateway import ModelGateway
from app.services.remediation_engine import RemediationEngine
from app.services.remediation_prompts import RemediationPromptBuilder


class RemediationService:
    """Orchestrator for Socratic tutoring turns, diagnostic assessment, and adaptive scaffolding."""

    def __init__(
        self,
        repository: TutoringSessionRepository,
        gateway: ModelGateway,
        diagnostic_engine: DiagnosticEngine | None = None,
        remediation_engine: RemediationEngine | None = None,
        prompt_builder: RemediationPromptBuilder | None = None,
    ):
        self.repo = repository
        self.gateway = gateway
        self.diagnostic_engine = diagnostic_engine or DiagnosticEngine()
        self.remediation_engine = remediation_engine or RemediationEngine()
        self.prompt_builder = prompt_builder or RemediationPromptBuilder()

    async def create_session(
        self,
        classroom_id: UUID,
        student_id: UUID,
        learning_objective: str,
    ) -> TutoringSessionResponse:
        session = await self.repo.create_session(classroom_id, student_id, learning_objective)
        # Seed the conversation with an initial welcome/opening question
        initial_prompt = (
            f"Hello! Today we are focusing on: {learning_objective}. "
            "To get started, what is your initial intuition or the first step you would take?"
        )
        await self.repo.add_message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=initial_prompt,
            sequence_number=0,
            hint_level=HintLevel.SOCRATIC_PROBE,
        )
        return session

    async def get_session(self, session_id: UUID) -> TutoringSessionResponse:
        session = await self.repo.get_session(session_id)
        if not session:
            raise APIError(404, "NOT_FOUND", f"Tutoring session {session_id} was not found.")
        return session

    async def get_messages(self, session_id: UUID) -> list[SessionMessage]:
        await self.get_session(session_id)
        return await self.repo.get_messages(session_id)

    async def process_turn(
        self,
        session_id: UUID,
        student_id: UUID,
        student_content: str,
        request_id: str | None = None,
    ) -> TutoringTurnResponse:
        session = await self.get_session(session_id)
        if session.status != SessionStatus.ACTIVE:
            raise APIError(400, "SESSION_CLOSED", "Cannot send messages to an inactive tutoring session.")

        messages = await self.repo.get_messages(session_id)
        next_seq = len(messages)

        # Count consecutive errors or past hint levels
        consecutive_errors = 0
        current_hint_level = HintLevel.SOCRATIC_PROBE
        for m in reversed(messages):
            if m.role == MessageRole.ASSISTANT and m.hint_level is not None:
                current_hint_level = m.hint_level
                break

        # 1. Run diagnostic assessment
        diagnostic = self.diagnostic_engine.diagnose(
            student_text=student_content,
            learning_objective=session.learning_objective,
            attempts=session.attempts + 1,
            current_hint_level=current_hint_level,
            consecutive_errors=consecutive_errors,
        )

        # 2. Determine scaffolding level
        target_hint_level = self.remediation_engine.determine_next_hint_level(
            current_hint_level=current_hint_level,
            diagnostic=diagnostic,
            explicit_hint_requested=False,
        )

        # 3. Build instructions & prompt
        scaffolding_instructions = self.remediation_engine.get_scaffolding_instructions(
            target_hint_level=target_hint_level,
            misconception=diagnostic.misconception,
            pedagogical_focus=diagnostic.pedagogical_focus,
        )

        history_chat_messages = [
            ChatMessage(role=m.role.value, content=m.content) for m in messages
        ]
        history_chat_messages.append(ChatMessage(role="user", content=student_content))

        model_messages = self.prompt_builder.build_messages(
            learning_objective=session.learning_objective,
            target_hint_level=target_hint_level,
            diagnostic=diagnostic,
            scaffolding_instructions=scaffolding_instructions,
            dialogue_history=history_chat_messages,
        )

        # 4. Generate response via Model Gateway
        gen_request = ModelGenerationRequest(
            session_id=str(session_id),
            messages=model_messages,
            max_output_tokens=300,
            temperature=0.7,
        )

        try:
            gen_result = await self.gateway.generate(gen_request, request_id=request_id)
            assistant_content = gen_result.content
        except Exception:
            # Pedagogical fallback if model service is unreachable
            assistant_content = self._generate_fallback_response(target_hint_level, diagnostic)

        # 5. Persist student and assistant messages
        student_msg = await self.repo.add_message(
            session_id=session_id,
            role=MessageRole.STUDENT,
            content=student_content,
            sequence_number=next_seq,
            author_user_id=student_id,
        )

        assistant_msg = await self.repo.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content,
            sequence_number=next_seq + 1,
            hint_level=target_hint_level,
        )

        # 6. Update session stats
        new_attempts = session.attempts + 1
        is_mastered = diagnostic.cognitive_state == StudentCognitiveState.MASTERED
        new_status = SessionStatus.COMPLETED if is_mastered else session.status
        await self.repo.update_session_stats(
            session_id=session_id,
            hints_used=session.hints_used,
            attempts=new_attempts,
            status=new_status,
        )


        return TutoringTurnResponse(
            session_id=session_id,
            student_message=student_msg,
            assistant_message=assistant_msg,
            diagnostic=diagnostic,
            current_hint_level=target_hint_level,
            attempts=new_attempts,
            hints_used=session.hints_used,
            status=new_status,
        )

    async def request_hint(
        self,
        session_id: UUID,
        student_id: UUID,
        request_id: str | None = None,
    ) -> RequestHintResponse:
        session = await self.get_session(session_id)
        if session.status != SessionStatus.ACTIVE:
            raise APIError(400, "SESSION_CLOSED", "Cannot request a hint for an inactive tutoring session.")

        messages = await self.repo.get_messages(session_id)
        next_seq = len(messages)

        current_hint_level = HintLevel.SOCRATIC_PROBE
        for m in reversed(messages):
            if m.role == MessageRole.ASSISTANT and m.hint_level is not None:
                current_hint_level = m.hint_level
                break

        # Escalate hint level
        target_hint_level = self.remediation_engine.determine_next_hint_level(
            current_hint_level=current_hint_level,
            diagnostic=DiagnosticAssessment(
                cognitive_state=StudentCognitiveState.STRUGGLING,
                misconception=MisconceptionCategory.NONE_DETECTED,
            ),
            explicit_hint_requested=True,
        )

        diagnostic = DiagnosticAssessment(
            cognitive_state=StudentCognitiveState.STRUGGLING,
            misconception=MisconceptionCategory.NONE_DETECTED,
            struggle_score=0.5,
            suggested_hint_level=target_hint_level,
            pedagogical_focus=f"The student requested a hint. Provide a Level {target_hint_level} scaffolded hint.",
        )

        scaffolding_instructions = self.remediation_engine.get_scaffolding_instructions(
            target_hint_level=target_hint_level,
            misconception=diagnostic.misconception,
            pedagogical_focus=diagnostic.pedagogical_focus,
        )

        history_chat_messages = [
            ChatMessage(role=m.role.value, content=m.content) for m in messages
        ]
        history_chat_messages.append(ChatMessage(role="user", content="Can you please give me a hint?"))

        model_messages = self.prompt_builder.build_messages(
            learning_objective=session.learning_objective,
            target_hint_level=target_hint_level,
            diagnostic=diagnostic,
            scaffolding_instructions=scaffolding_instructions,
            dialogue_history=history_chat_messages,
        )

        gen_request = ModelGenerationRequest(
            session_id=str(session_id),
            messages=model_messages,
            max_output_tokens=300,
            temperature=0.7,
        )

        try:
            gen_result = await self.gateway.generate(gen_request, request_id=request_id)
            hint_content = gen_result.content
        except Exception:
            hint_content = self._generate_fallback_response(target_hint_level, diagnostic)

        assistant_msg = await self.repo.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=hint_content,
            sequence_number=next_seq,
            hint_level=target_hint_level,
        )

        new_hints_used = session.hints_used + 1
        await self.repo.update_session_stats(
            session_id=session_id,
            hints_used=new_hints_used,
            attempts=session.attempts,
            status=session.status,
        )

        return RequestHintResponse(
            session_id=session_id,
            assistant_message=assistant_msg,
            hint_level=target_hint_level,
            hints_used=new_hints_used,
            status=session.status,
        )

    async def end_session(
        self,
        session_id: UUID,
        body: EndSessionRequest,
    ) -> TutoringSessionResponse:
        session = await self.get_session(session_id)
        updated = await self.repo.end_session(session_id, body.status)
        return updated or session

    async def get_session_summary(self, session_id: UUID) -> SessionSummaryResponse:
        session = await self.get_session(session_id)
        messages = await self.repo.get_messages(session_id)

        max_hint = HintLevel.SOCRATIC_PROBE
        misconceptions: set[MisconceptionCategory] = set()

        for m in messages:
            if m.hint_level is not None and int(m.hint_level) > int(max_hint):
                max_hint = m.hint_level
            if m.role == MessageRole.STUDENT:
                diag = self.diagnostic_engine.diagnose(m.content)
                if diag.misconception != MisconceptionCategory.NONE_DETECTED:
                    misconceptions.add(diag.misconception)

        return SessionSummaryResponse(
            session_id=session.id,
            classroom_id=session.classroom_id,
            learning_objective=session.learning_objective,
            status=session.status,
            total_turns=len(messages),
            attempts=session.attempts,
            hints_used=session.hints_used,
            max_hint_level_reached=max_hint,
            identified_misconceptions=list(misconceptions),
            started_at=session.started_at,
            ended_at=session.ended_at,
        )

    def _generate_fallback_response(self, hint_level: HintLevel, diagnostic: DiagnosticAssessment) -> str:
        """Deterministic pedagogical fallback if model inference endpoint is unavailable."""
        if hint_level == HintLevel.SOCRATIC_PROBE:
            return "Let's think carefully: what is the fundamental goal we want to achieve at this step?"
        if hint_level == HintLevel.CONCEPTUAL_POINTER:
            return (
                "Consider the base definition or invariant of the data structure. "
                "What condition must always hold true?"
            )
        if hint_level == HintLevel.STRATEGIC_HINT:
            return "Try dry-running your logic with a minimal example (such as an empty case or n=1). What happens?"
        if hint_level == HintLevel.DECOMPOSITION_BREAKDOWN:
            return "Let's break this down into smaller pieces: First, what should happen for the simplest base case?"
        if hint_level == HintLevel.WORKED_ANALOGY:
            return (
                "Think of it like looking up words in a dictionary: "
                "you wouldn't scan every page from the start, you would jump to the middle."
            )
        return (
            "Here is the key breakdown: identify the boundary condition, check if the input is valid, "
            "and recurse on the smaller sub-problem."
        )

