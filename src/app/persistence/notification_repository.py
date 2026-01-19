from typing import Protocol

from domain import Notification


class NotificationRepository(Protocol):
    async def get_all(self) -> list[Notification]: ...

    async def get_by_type(self, notification_type: str) -> Notification | None: ...
