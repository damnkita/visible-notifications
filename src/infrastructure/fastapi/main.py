from contextlib import asynccontextmanager

from fastapi import FastAPI

from presentation.api.health.controller import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("I start")
    yield
    print("I die")


def create_api() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    return app
