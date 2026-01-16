from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/healthz")
async def healthy() -> JSONResponse:
    return JSONResponse(content={"healthy": True})


@router.get("/readyz")
async def ready() -> JSONResponse:
    return JSONResponse(content={"ready": True})
