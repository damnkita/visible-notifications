from datetime import datetime, timedelta
from typing import Protocol

from domain import Event


class EventRepository(Protocol):
    async def save_all(self, events: list[Event]) -> int: ...

    async def find_for_user_within_time(
        self,
        event_type: str,
        user_id: str,
        timerange: timedelta,
        event_timestamp: datetime,
    ) -> list[Event]: ...

    async def find_recent_by_user(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[Event]: ...
