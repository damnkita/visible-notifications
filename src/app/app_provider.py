from dishka import Provider, Scope, provide

from app.health import ReadinessCheckUseCase, ReadyChecker


class AppProvider(Provider):
    scope = Scope.REQUEST
    services = provide(ReadinessCheckUseCase) + provide(ReadyChecker)
