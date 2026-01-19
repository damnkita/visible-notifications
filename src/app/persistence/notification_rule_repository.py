from typing import Protocol

from domain import NotificationRule


class NotificationRuleRepository(Protocol):
    async def get_all(self) -> list[NotificationRule]: ...

    async def get_by_event_type(self, event_type: str) -> list[NotificationRule]: ...
