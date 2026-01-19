from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.notifications.notification_rules_relay import NotificationRulesRelay
from domain import Event
from infrastructure.staticyaml import (
    StaticNotificationRepository,
    StaticNotificationRuleRepository,
)


@pytest.mark.anyio
async def test_route__signup_with_marketing_consent__triggers_welcome_email():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    notifications = await notification_repo.get_all()
    rules = await rule_repo.get_all()

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=rules,
        notifications=notifications,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "signup_completed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {"signup_method": "email"}
    event.user_traits = {"email": "maria@example.com", "marketing_opt_in": "true"}

    intents = await relay.route(event)

    assert len(intents) == 1
    assert intents[0].notification_type == "WELCOME_EMAIL"
    assert intents[0].delay is None


@pytest.mark.anyio
async def test_route__payment_failed_insufficient_funds__triggers_email():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    notifications = await notification_repo.get_all()
    rules = await rule_repo.get_all()

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=rules,
        notifications=notifications,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 1425.0,
        "attempt_number": 2,
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "maria@example.com"}

    intents = await relay.route(event)

    assert len(intents) == 1
    assert intents[0].notification_type == "INSUFFICIENT_FUNDS_EMAIL"


@pytest.mark.anyio
async def test_route__payment_failed_third_attempt__triggers_high_risk_alert():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    notifications = await notification_repo.get_all()
    rules = await rule_repo.get_all()

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=rules,
        notifications=notifications,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 1425.0,
        "attempt_number": 3,
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "maria@example.com"}

    intents = await relay.route(event)

    assert len(intents) == 2
    notification_types = {intent.notification_type for intent in intents}
    assert "INSUFFICIENT_FUNDS_EMAIL" in notification_types
    assert "HIGH_RISK_ALERT" in notification_types


@pytest.mark.anyio
async def test_route__bank_linked_after_signup__triggers_nudge_sms():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    signup_event = Event()
    signup_event.id = uuid4()
    signup_event.user_id = "u_12345"
    signup_event.type = "signup_completed"
    signup_event.event_timestamp = datetime.now(UTC)
    signup_event.event_date = signup_event.event_timestamp.date()
    signup_event.properties = {}
    signup_event.user_traits = {}

    mock_event_repo.find_for_user_within_time.return_value = [signup_event]

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    notifications = await notification_repo.get_all()
    rules = await rule_repo.get_all()

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=rules,
        notifications=notifications,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "link_bank_success"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {"bank_name": "Santander"}
    event.user_traits = {"email": "maria@example.com"}

    intents = await relay.route(event)

    assert len(intents) == 1
    assert intents[0].notification_type == "BANK_LINK_NUDGE_SMS"


@pytest.mark.anyio
async def test_route__payment_failed_insufficient_funds__debounced_when_limit_reached():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    # Simulate that user already received 1 notification (matches debounce_limit: 1)
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 1

    notification_repo = StaticNotificationRepository()
    rule_repo = StaticNotificationRuleRepository()

    notifications = await notification_repo.get_all()
    rules = await rule_repo.get_all()

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=rules,
        notifications=notifications,
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

    intents = await relay.route(event)

    assert len(intents) == 1
    assert intents[0].notification_type == "INSUFFICIENT_FUNDS_EMAIL"
    assert intents[0].debounced_because is not None
    assert "1" in intents[0].debounced_because  # References the count
