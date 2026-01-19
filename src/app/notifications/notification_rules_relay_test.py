from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.notifications.notification_rules_relay import NotificationRulesRelay
from domain import Event
from domain.notification_rule import NotificationRule
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


@pytest.mark.anyio
async def test_route__debounce_with_no_period__uses_eternity_fallback():
    """When debounce_limit is set but debounce_period is None (eternity),
    notification should be debounced if limit was ever reached."""
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    # User has received 1 notification at some point in the past
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 1

    notification_repo = StaticNotificationRepository()
    notifications = await notification_repo.get_all()

    # Create a custom rule with debounce_limit=1 but no debounce_period (eternity)
    rule_with_eternity_debounce = NotificationRule(
        notification_type="TEST_ONCE_EVER",
        event_type="test_event",
        event_conditions=[],
        delay=None,
        recheck=False,
        debounce_period=None,  # None means "ever" / eternity
        debounce_limit=1,
        debounce_calendar_day=False,
    )

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=[rule_with_eternity_debounce],
        notifications=notifications,
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "test_event"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {}
    event.user_traits = {}

    intents = await relay.route(event)

    # Verify the 100-year fallback was used
    mock_notification_history_repo.count_by_user_and_type_within_time.assert_called_once_with(
        user_id="u_12345",
        notification_type="TEST_ONCE_EVER",
        timerange=timedelta(weeks=52 * 100),  # 100 years hack
    )

    assert len(intents) == 1
    assert intents[0].notification_type == "TEST_ONCE_EVER"
    assert intents[0].debounced_because is not None


@pytest.mark.anyio
async def test_route__calendar_day_debounce__resets_at_midnight():
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    # No notifications sent since midnight today
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 0

    notification_repo = StaticNotificationRepository()
    notifications = await notification_repo.get_all()

    # Use the actual INSUFFICIENT_FUNDS_EMAIL rule which has calendar_day=True
    rule_repo = StaticNotificationRuleRepository()
    rules = await rule_repo.get_all()
    insufficient_funds_rule = next(
        r for r in rules if r.notification_type == "INSUFFICIENT_FUNDS_EMAIL"
    )

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=[insufficient_funds_rule],
        notifications=notifications,
    )

    # Current time: 00:00:01 on Jan 2, 2025
    frozen_now = datetime(2025, 1, 2, 0, 0, 1, tzinfo=UTC)

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = frozen_now
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 100.0,
        "attempt_number": 1,
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "test@example.com"}

    with patch(
        "app.notifications.notification_rules_relay.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        intents = await relay.route(event)

    # Verify the timerange is ~1 second (time since midnight)
    call_args = (
        mock_notification_history_repo.count_by_user_and_type_within_time.call_args
    )
    timerange = call_args.kwargs["timerange"]
    assert timerange == timedelta(seconds=1)

    # Notification should NOT be debounced since it's a new calendar day
    assert len(intents) == 1
    assert intents[0].notification_type == "INSUFFICIENT_FUNDS_EMAIL"
    assert intents[0].debounced_because is None


@pytest.mark.anyio
async def test_route__calendar_day_debounce__blocks_same_day():
    """When debounce_calendar_day=True and notification was already sent today,
    subsequent notifications should be debounced."""
    mock_event_repo = AsyncMock()
    mock_notification_history_repo = AsyncMock()
    # One notification already sent today
    mock_notification_history_repo.count_by_user_and_type_within_time.return_value = 1

    notification_repo = StaticNotificationRepository()
    notifications = await notification_repo.get_all()

    rule_repo = StaticNotificationRuleRepository()
    rules = await rule_repo.get_all()
    insufficient_funds_rule = next(
        r for r in rules if r.notification_type == "INSUFFICIENT_FUNDS_EMAIL"
    )

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_history_repo=mock_notification_history_repo,
        notification_rules=[insufficient_funds_rule],
        notifications=notifications,
    )

    # Current time: 23:59:59 on Jan 1, 2025 (same day as previous notification)
    frozen_now = datetime(2025, 1, 1, 23, 59, 59, tzinfo=UTC)

    event = Event()
    event.id = uuid4()
    event.user_id = "u_12345"
    event.type = "payment_failed"
    event.event_timestamp = frozen_now
    event.event_date = event.event_timestamp.date()
    event.properties = {
        "amount": 100.0,
        "attempt_number": 1,
        "failure_reason": "INSUFFICIENT_FUNDS",
    }
    event.user_traits = {"email": "test@example.com"}

    with patch(
        "app.notifications.notification_rules_relay.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = frozen_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        intents = await relay.route(event)

    # Verify the timerange covers the whole day until now
    call_args = (
        mock_notification_history_repo.count_by_user_and_type_within_time.call_args
    )
    timerange = call_args.kwargs["timerange"]
    expected_timerange = timedelta(hours=23, minutes=59, seconds=59)
    assert timerange == expected_timerange

    # Notification SHOULD be debounced since limit reached today
    assert len(intents) == 1
    assert intents[0].notification_type == "INSUFFICIENT_FUNDS_EMAIL"
    assert intents[0].debounced_because is not None
