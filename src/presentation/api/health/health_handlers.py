from dataclasses import dataclass

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter

from app.health.readiness_check_usecase import ReadinessCheckUseCase

router = APIRouter()


@dataclass
class HealthcheckResponse:
    status: str = "ok"


@router.get("/healthz/live")
async def healthy() -> HealthcheckResponse:
    return HealthcheckResponse()


@router.get("/healthz/ready")
@inject
async def ready(use_case: FromDishka[ReadinessCheckUseCase]) -> HealthcheckResponse:
    await use_case.handle(None)
    return HealthcheckResponse()
