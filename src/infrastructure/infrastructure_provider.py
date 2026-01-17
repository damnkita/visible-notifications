from dishka import Provider, Scope, provide

from app.health.readiness_check_usecase import DatabaseChecker
from infrastructure.database.dummy_db_checker import DummyDBChecker


class InfrastructureProvider(Provider):
    services = provide(DummyDBChecker, provides=DatabaseChecker, scope=Scope.REQUEST)
