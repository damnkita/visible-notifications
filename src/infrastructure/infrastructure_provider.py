from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.health.readiness_check_usecase import DatabaseChecker
from app.logging import Logger
from app.persistence.event_repository import EventRepository
from app.persistence.notification_repository import NotificationRepository
from app.persistence.notification_rule_repository import NotificationRuleRepository
from app.queue import EventQueue
from infrastructure.database.persistence.sqla_event_repository import (
    SQLAEventRepository,
)
from infrastructure.database.postgres.postgres_db_checker import PostgresDBChecker
from infrastructure.env_config import EnvConfig
from infrastructure.logging import LoguruLogger
from infrastructure.staticyaml import (
    StaticNotificationRepository,
    StaticNotificationRuleRepository,
)
from infrastructure.taskiq import TaskiqEventQueue


class InfrastructureProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    def get_db_checker(self, async_session: AsyncSession) -> DatabaseChecker:
        return PostgresDBChecker(async_session)

    @provide(scope=Scope.APP)
    def get_async_engine(self, settings: EnvConfig) -> AsyncEngine:
        return create_async_engine(str(settings.database_url_async))

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_async_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session, session.begin():
            yield session

    repositories = (
        provide(SQLAEventRepository, provides=EventRepository, scope=Scope.REQUEST)
        + provide(
            StaticNotificationRepository,
            provides=NotificationRepository,
            scope=Scope.APP,
        )
        + provide(
            StaticNotificationRuleRepository,
            provides=NotificationRuleRepository,
            scope=Scope.APP,
        )
    )

    queues = provide(TaskiqEventQueue, provides=EventQueue, scope=Scope.REQUEST)

    loggers = provide(LoguruLogger, provides=Logger, scope=Scope.REQUEST)
