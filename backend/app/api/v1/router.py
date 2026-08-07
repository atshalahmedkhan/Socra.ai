from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.contracts import router as contract_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(contract_router)


@router.get("/status")
async def status():
    from app.core.config import get_settings

    settings = get_settings()
    return {"model_version": settings.model_version, "env": settings.environment}
