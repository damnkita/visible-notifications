from datetime import UTC, datetime
from unittest.mock import AsyncMock, call
from uuid import uuid4

import pytest

from app.notifications.trigger_notifications_use_case import TriggerNotificationsUseCase
from domain import Event
from domain.notification_history_record import NotificationStatus
from infrastructure.staticyaml import (
    StaticNotificationRepository,
    StaticNotificationRuleRepository,
)


@pytest.mark.anyio
async def test_handle__creates_history_record_for_sent_notification():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    use_case = TriggerNotificationsUseCase(
        event_repository=mock_event_repo,
        notification_history_record_repository=mock_notification_history_repo,
        notification_repository=notification_repo,
        notification_rule_repository=rule_repo,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "signup_completed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {"signup_method": "email"}
    event.user_traits = {"email": "maria@example.com", "marketing_opt_in": "true"}

    await use_case.handle(event)

    assert mock_notification_history_repo.save.call_count == 1

    saved_record = mock_notification_history_repo.save.call_args[0][0]
    assert saved_record.type == "WELCOME_EMAIL"
    assert saved_record.trigger == "signup_completed"
    assert saved_record.user_id == "u_12345"
    assert saved_record.status == NotificationStatus.SENT
    assert saved_record.retries == 0
    assert saved_record.suppressed_because is None
    assert saved_record.created_at is not None


@pytest.mark.anyio
async def test_handle__creates_history_record_for_debounced_notification():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    # Simulate that user already received 1 notification (matches debounce_limit: 1)
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 1

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    use_case = TriggerNotificationsUseCase(
        event_repository=mock_event_repo,
        notification_history_record_repository=mock_notification_history_repo,
        notification_repository=notification_repo,
        notification_rule_repository=rule_repo,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 1425.0,
        "attempt_number": 1,
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "maria@example.com"}

    await use_case.handle(event)

    assert mock_notification_history_repo.save.call_count == 1

    saved_record = mock_notification_history_repo.save.call_args[0][0]
    assert saved_record.type == "INSUFFICIENT_FUNDS_EMAIL"
    assert saved_record.trigger == "payment_failed"
    assert saved_record.user_id == "u_12345"
    assert saved_record.status == NotificationStatus.SUPPRESSED
    assert saved_record.retries == 0
    assert saved_record.suppressed_because is not None
    assert "1" in saved_record.suppressed_because


@pytest.mark.anyio
async def test_handle__creates_multiple_history_records_for_multiple_intents():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    use_case = TriggerNotificationsUseCase(
        event_repository=mock_event_repo,
        notification_history_record_repository=mock_notification_history_repo,
        notification_repository=notification_repo,
        notification_rule_repository=rule_repo,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 1425.0,
        "attempt_number": 3,  # Triggers both INSUFFICIENT_FUNDS_EMAIL and HIGH_RISK_ALERT
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "maria@example.com"}

    await use_case.handle(event)

    assert mock_notification_history_repo.save.call_count == 2

    saved_types = {
        mock_notification_history_repo.save.call_args_list[i][0][0].type
        for i in range(2)
    }
    assert "INSUFFICIENT_FUNDS_EMAIL" in saved_types
    assert "HIGH_RISK_ALERT" in saved_types

    for call_args in mock_notification_history_repo.save.call_args_list:
        record = call_args[0][0]
        assert record.trigger == "payment_failed"
        assert record.user_id == "u_12345"
        assert record.status == NotificationStatus.SENT
