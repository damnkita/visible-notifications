from datetime import timedelta
from typing import Protocol

from domain import NotificationHistoryRecord


class NotificationHistoryRecordRepository(Protocol):
    async def save(self, record: NotificationHistoryRecord) -> None: ...

    async def count_by_user_and_type_within_time(
        self,
        user_id: str,
        notification_type: str,
        timerange: timedelta,
    ) -> int: ...

