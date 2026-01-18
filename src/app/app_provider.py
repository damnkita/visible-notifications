from dishka import Provider, Scope, provide

from app.events import SaveEventsUseCase
from app.health import ReadinessCheckUseCase, ReadyChecker


class AppProvider(Provider):
    scope = Scope.REQUEST
    services = (
        provide(ReadinessCheckUseCase)
        + provide(ReadyChecker)
        + provide(SaveEventsUseCase)
    )
