from contextlib import asynccontextmanager
from enum import Enum
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    ApplicationException,
    InternalApplicationException,
    WebApplicationException,
)
from presentation.api.health.controller import router as health_router


class Mode(str, Enum):
    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    TEST = "test"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("I start")
    yield
    print("I die")


def create_api(mode: Mode = Mode.PROD) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)

    @app.exception_handler(ApplicationException)
    async def exception_handler(request: Request, e: InternalApplicationException):
        if mode is Mode.PROD and isinstance(e, InternalApplicationException):
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

    return app
