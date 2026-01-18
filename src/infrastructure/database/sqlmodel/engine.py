from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine as sqla_create_async_engine,
)

from infrastructure.settings import APISettings


def create_async_engine(settings: APISettings) -> AsyncEngine:
    return sqla_create_async_engine(str(settings.database_url_async))
