from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.health.readiness_check_usecase import DatabaseChecker
from infrastructure.database.postgres.postgres_db_checker import PostgresDBChecker
from infrastructure.database.sqlmodel.engine import (
    create_async_engine,
)
from infrastructure.settings import APISettings


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    def get_db_checker(self, async_session: AsyncSession) -> DatabaseChecker:
        return PostgresDBChecker(async_session)

    @provide
    def get_async_engine(self, settings: APISettings) -> AsyncEngine:
        return create_async_engine(settings)

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self, engine: AsyncEngine
    ) -> AsyncIterable[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session
