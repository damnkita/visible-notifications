from contextlib import asynccontextmanager
from http import HTTPStatus

from dishka import Provider, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.exceptions import (
    ApplicationException,
    InternalApplicationException,
    WebApplicationException,
)
from infrastructure.database.migrations.apply_migrations import update_head
from infrastructure.env_config import Env, EnvConfig
from infrastructure.logging import configure_logging
from presentation.api.events import events_router
from presentation.api.health import health_router


def make_lifespan(envconfig: EnvConfig):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Migrations starting")
        update_head(envconfig)
        logger.info("Migrations completed")
        yield
        await app.state.dishka_container.close()

    return lifespan


def create_api(envconfig: EnvConfig, dependencies_providers: list[Provider]) -> FastAPI:
    configure_logging(envconfig.env, service_name="visible-notify-api")

    lifespan = make_lifespan(envconfig)

    app = FastAPI(lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(events_router)

    container = make_async_container(*dependencies_providers)
    setup_dishka(container, app)

    @app.exception_handler(ApplicationException)
    async def exception_handler(
        e: InternalApplicationException,
    ):
        if envconfig.env is Env.PROD and isinstance(e, InternalApplicationException):
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
        logger.exception(
            "Unhandled exception", path=request.url.path, method=request.method
        )
        if envconfig.env is Env.PROD:
            return JSONResponse(
                content={"code": "E_ERR_INTERNAL", "reason": "Internal error"},
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        return JSONResponse(
            content={"code": "E_ERR_UNKNOWN", "reason": str(e)},
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    return app
