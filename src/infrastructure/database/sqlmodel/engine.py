from sqlalchemy import Engine, create_engine as sqla_create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine as sqla_create_async_engine,
)

from infrastructure.settings import APISettings


def create_sync_engine(settings: APISettings) -> Engine:
    return sqla_create_engine(str(settings.database_url_sync))


def create_async_engine(settings: APISettings) -> AsyncEngine:
    return sqla_create_async_engine(str(settings.database_url_async))
