from dishka import Provider, Scope, provide

from app.health.readiness_check_usecase import ReadinessCheckUseCase, ReadyChecker


class AppProvider(Provider):
    scope = Scope.REQUEST
    services = provide(ReadinessCheckUseCase) + provide(ReadyChecker)
