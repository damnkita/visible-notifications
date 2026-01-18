from typing import Protocol

from domain import Event


class EventRepository(Protocol):
    async def save_all(self, events: list[Event]) -> int: ...
