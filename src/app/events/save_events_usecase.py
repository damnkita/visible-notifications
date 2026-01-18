import asyncio
from dataclasses import dataclass

from app.persistence.event_repository import EventRepository
from app.queue import EventQueue
from app.usecase import UseCase
from domain import Event


@dataclass
class SaveEventsRequest:
    events: list[Event]


@dataclass
class SaveEventsResponse:
    saved_count: int


class SaveEventsUseCase(UseCase[SaveEventsRequest, SaveEventsResponse]):
    def __init__(
        self,
        event_repository: EventRepository,
        event_queue: EventQueue,
    ) -> None:
        super().__init__()
        self.event_repository = event_repository
        self.event_queue = event_queue

    async def handle(self, request: SaveEventsRequest) -> SaveEventsResponse:
        save_all_task = self.event_repository.save_all(request.events)
        events_received_task = self.event_queue.events_received(request.events)
        (saved_count, queue_ex) = await asyncio.gather(
            save_all_task, events_received_task, return_exceptions=True
        )
        if isinstance(saved_count, Exception):
            raise saved_count

        if isinstance(queue_ex, Exception):
            raise (queue_ex)

        assert isinstance(saved_count, int)
        return SaveEventsResponse(saved_count=saved_count)
