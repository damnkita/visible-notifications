from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.health.readiness_check_usecase import ReadinessCheckUseCase

router = APIRouter()


@router.get("/healthz")
async def healthy() -> JSONResponse:
    return JSONResponse(content={"healthy": True})


@router.get("/readyz")
@inject
async def ready(use_case: FromDishka[ReadinessCheckUseCase]) -> JSONResponse:
    await use_case.handle(None)
    return JSONResponse(content={"ready": True})
