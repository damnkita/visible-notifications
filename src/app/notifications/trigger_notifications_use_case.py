from app.usecase import UseCase
from domain import Event


class TriggerNotificationsUseCase(UseCase[Event, int]):
    def __init__(self) -> None:
        super().__init__()

    async def handle(self, request: Event) -> int:
        return 5
