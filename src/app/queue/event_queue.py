from typing import Protocol

from domain import Event


class EventQueue(Protocol):
    async def events_received(self, events: list[Event]) -> None: ...
