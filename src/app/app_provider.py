from dishka import Provider, Scope, provide

from app.events import SaveEventsUseCase
from app.health import ReadinessCheckUseCase, ReadyChecker
from app.notifications.trigger_notifications_use_case import (
    TriggerNotificationsUseCase,
)


class AppProvider(Provider):
    scope = Scope.REQUEST
    services = (
        provide(ReadinessCheckUseCase)
        + provide(ReadyChecker)
        + provide(SaveEventsUseCase)
        + provide(TriggerNotificationsUseCase)
    )
