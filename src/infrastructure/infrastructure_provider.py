from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.health.readiness_check_usecase import DatabaseChecker
from app.persistence.event_repository import EventRepository
from infrastructure.database.persistence.sqla_event_repository import (
    SQLAEventRepository,
)
from infrastructure.database.postgres.postgres_db_checker import PostgresDBChecker
from infrastructure.database.sqlalchemy.engine import (
    create_async_engine,
)
from infrastructure.env_config import EnvConfig


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    def get_db_checker(self, async_session: AsyncSession) -> DatabaseChecker:
        return PostgresDBChecker(async_session)

    @provide(scope=Scope.APP)
    def get_async_engine(self, settings: EnvConfig) -> AsyncEngine:
        return create_async_engine(str(settings.database_url_async))

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self, engine: AsyncEngine
    ) -> AsyncIterable[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session

    repositories = provide(
        SQLAEventRepository, provides=EventRepository, scope=Scope.REQUEST
    )
