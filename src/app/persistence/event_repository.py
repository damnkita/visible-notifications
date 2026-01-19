from datetime import timedelta
from typing import Protocol

from domain import Event


class EventRepository(Protocol):
    async def save_all(self, events: list[Event]) -> int: ...

    async def find_for_user_within_time(
        self,
        event_type: str,
        user_id: str,
        timerange: timedelta,
    ) -> list[Event]: ...
