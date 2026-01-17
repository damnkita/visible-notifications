from contextlib import asynccontextmanager
from enum import Enum
from http import HTTPStatus

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.app_provider import AppProvider
from app.exceptions import (
    ApplicationException,
    InternalApplicationException,
    WebApplicationException,
)
from infrastructure.infrastructure_provider import InfrastructureProvider
from presentation.api.health.health_handlers import router as health_router


class Env(str, Enum):
    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    TEST = "test"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("I start")
    yield
    await app.state.dishka_container.close()
    print("I die")


def create_api(env: Env = Env.PROD) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)

    container = make_async_container(AppProvider(), InfrastructureProvider())
    setup_dishka(container, app)

    @app.exception_handler(ApplicationException)
    async def exception_handler(request: Request, e: InternalApplicationException):
        if env is Env.PROD and isinstance(e, InternalApplicationException):
            return JSONResponse(
                content={"code": "E_ERR_INTERNAL", "reason": "Internal error"},
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        if isinstance(e, WebApplicationException):
            return JSONResponse(
                content={"code": e.code, "reason": e.reason},
                status_code=e.status,
            )

        return JSONResponse(
            content={"code": e.code, "reason": e.reason},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(Exception)
    async def uncaught_exception_handler(request: Request, e: Exception):
        print("UNHANDLED EXCEPTION!")
        return JSONResponse(
            content={"code": "E_ERR_INTERNAL", "reason": "Internal error"},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    return app
