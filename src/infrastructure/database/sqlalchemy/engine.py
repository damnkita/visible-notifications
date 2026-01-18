from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine as sqla_create_async_engine,
)


def create_async_engine(database_url_async: str) -> AsyncEngine:
    return sqla_create_async_engine(database_url_async)
