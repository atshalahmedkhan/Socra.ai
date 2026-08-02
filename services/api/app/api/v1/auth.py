from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.schemas.auth import MeResponse
from app.schemas.common import OperationSuccess

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MeResponse)
async def me(user=Depends(get_current_user)):
    return user


@router.post("/logout", response_model=OperationSuccess)
async def logout(user=Depends(get_current_user)):
    # Supabase browser sign-out owns token revocation for Phase 1.
    return OperationSuccess()
