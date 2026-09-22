from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.schemas.remediation import (
    CreateTutoringSessionRequest,
    EndSessionRequest,
    RequestHintResponse,
    SessionMessage,
    SessionSummaryResponse,
    TutoringSessionResponse,
    TutoringTurnRequest,
    TutoringTurnResponse,
)

router = APIRouter(prefix="/tutoring-sessions", tags=["tutoring"])


@router.post("", response_model=TutoringSessionResponse)
async def create_tutoring_session(
    body: CreateTutoringSessionRequest,
    request: Request,
    user=Depends(get_current_user),
):
    student_id = user.internal_user_id
    service = request.app.state.remediation_service
    return await service.create_session(
        classroom_id=body.classroom_id,
        student_id=student_id,
        learning_objective=body.learning_objective,
    )


@router.get("/{session_id}", response_model=TutoringSessionResponse)
async def get_tutoring_session(
    session_id: UUID,
    request: Request,
    user=Depends(get_current_user),
):
    service = request.app.state.remediation_service
    return await service.get_session(session_id)


@router.get("/{session_id}/messages", response_model=list[SessionMessage])
async def get_tutoring_messages(
    session_id: UUID,
    request: Request,
    user=Depends(get_current_user),
):
    service = request.app.state.remediation_service
    return await service.get_messages(session_id)


@router.post("/{session_id}/messages", response_model=TutoringTurnResponse)
async def send_tutoring_message(
    session_id: UUID,
    body: TutoringTurnRequest,
    request: Request,
    user=Depends(get_current_user),
):
    student_id = user.internal_user_id
    request_id = request.headers.get("x-request-id")
    service = request.app.state.remediation_service
    return await service.process_turn(
        session_id=session_id,
        student_id=student_id,
        student_content=body.content,
        request_id=request_id,
    )


@router.post("/{session_id}/hint", response_model=RequestHintResponse)
async def request_hint(
    session_id: UUID,
    request: Request,
    user=Depends(get_current_user),
):
    student_id = user.internal_user_id
    request_id = request.headers.get("x-request-id")
    service = request.app.state.remediation_service
    return await service.request_hint(
        session_id=session_id,
        student_id=student_id,
        request_id=request_id,
    )



@router.post("/{session_id}/end", response_model=TutoringSessionResponse)
async def end_tutoring_session(
    session_id: UUID,
    body: EndSessionRequest,
    request: Request,
    user=Depends(get_current_user),
):
    service = request.app.state.remediation_service
    return await service.end_session(session_id=session_id, body=body)


@router.get("/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(
    session_id: UUID,
    request: Request,
    user=Depends(get_current_user),
):
    service = request.app.state.remediation_service
    return await service.get_session_summary(session_id)
