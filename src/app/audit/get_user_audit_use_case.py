from dataclasses import dataclass
from datetime import datetime

from app.persistence.event_repository import EventRepository
from app.persistence.notification_history_record_repository import (
    NotificationHistoryRecordRepository,
)
from app.usecase import UseCase
from domain.notification_history_record import NotificationStatus


@dataclass
class EventAuditItem:
    event_id: str
    event_type: str
    event_timestamp: datetime
    properties: dict


@dataclass
class NotificationAuditItem:
    notification_type: str
    trigger_event: str
    status: str
    created_at: datetime
    suppression_reason: str | None


@dataclass
class GetUserAuditRequest:
    user_id: str
    limit: int = 50


@dataclass
class GetUserAuditResponse:
    user_id: str
    recent_events: list[EventAuditItem]
    notification_history: list[NotificationAuditItem]


class GetUserAuditUseCase(UseCase[GetUserAuditRequest, GetUserAuditResponse]):
    def __init__(
        self,
        event_repository: EventRepository,
        notification_history_record_repository: NotificationHistoryRecordRepository,
    ) -> None:
        super().__init__()
        self.event_repository = event_repository
        self.notification_history_record_repository = notification_history_record_repository

    async def handle(self, request: GetUserAuditRequest) -> GetUserAuditResponse:
        events = await self.event_repository.find_recent_by_user(
            user_id=request.user_id,
            limit=request.limit,
        )

        notifications = await self.notification_history_record_repository.find_recent_by_user(
            user_id=request.user_id,
            limit=request.limit,
        )

        event_items = [
            EventAuditItem(
                event_id=str(event.id),
                event_type=event.type,
                event_timestamp=event.event_timestamp,
                properties=event.properties,
            )
            for event in events
        ]

        notification_items = [
            NotificationAuditItem(
                notification_type=record.type,
                trigger_event=record.trigger,
                status=record.status.value if isinstance(record.status, NotificationStatus) else record.status,
                created_at=record.created_at,
                suppression_reason=self._format_suppression_reason(record),
            )
            for record in notifications
        ]

        return GetUserAuditResponse(
            user_id=request.user_id,
            recent_events=event_items,
            notification_history=notification_items,
        )

    def _format_suppression_reason(self, record) -> str | None:
        if record.status == NotificationStatus.SUPPRESSED and record.suppressed_because:
            return f"skipped {record.type}: {record.suppressed_because}"
        return None
