from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.notifications.notification_intent import NotificationIntent
from app.notifications.notification_rules_relay import NotificationRulesRelay
from app.persistence.event_repository import EventRepository
from app.persistence.notification_history_record_repository import (
    NotificationHistoryRecordRepository,
)
from app.persistence.notification_repository import NotificationRepository
from app.persistence.notification_rule_repository import NotificationRuleRepository
from app.usecase import UseCase
from domain import Event
from domain.notification_history_record import (
    NotificationHistoryRecord,
    NotificationStatus,
)


@dataclass
class TriggerNotificationsResponse:
    intents: list[NotificationIntent]


class TriggerNotificationsUseCase(UseCase[Event, TriggerNotificationsResponse]):
    def __init__(
        self,
        event_repository: EventRepository,
        notification_history_record_repository: NotificationHistoryRecordRepository,
        notification_repository: NotificationRepository,
        notification_rule_repository: NotificationRuleRepository,
    ) -> None:
        super().__init__()
        self.event_repository = event_repository
        self.notification_history_record_repository = (
            notification_history_record_repository
        )
        self.notification_repository = notification_repository
        self.notification_rule_repository = notification_rule_repository

    async def handle(self, request: Event) -> TriggerNotificationsResponse:
        notifications = await self.notification_repository.get_all()
        rules = await self.notification_rule_repository.get_all()

        relay = NotificationRulesRelay(
            event_repo=self.event_repository,
            notification_history_repo=self.notification_history_record_repository,
            notification_rules=rules,
            notifications=notifications,
        )

        intents = await relay.route(request)

        for intent in intents:
            record = NotificationHistoryRecord(
                id=uuid4(),
                type=intent.notification_type,
                trigger=request.type,
                user_id=request.user_id,
                status=NotificationStatus.SUPPRESSED
                if intent.debounced_because
                else NotificationStatus.SENT,
                retries=0,
                suppressed_because=intent.debounced_because,
                created_at=datetime.now(UTC),
            )
            await self.notification_history_record_repository.save(record)

        return TriggerNotificationsResponse(intents=intents)
