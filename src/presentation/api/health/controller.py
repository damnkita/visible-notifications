from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.health.readiness_check_usecase import ReadinessCheckUseCase

router = APIRouter()


@router.get("/healthz")
async def healthy() -> JSONResponse:
    return JSONResponse(content={"healthy": True})


@router.get("/readyz")
async def ready(use_case: ReadinessCheckUseCase) -> JSONResponse:
    return JSONResponse(content={"ready": True})
