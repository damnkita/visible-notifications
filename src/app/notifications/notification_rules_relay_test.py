from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.notifications.notification_rules_relay import NotificationRulesRelay
from domain import Event, Notification, NotificationRule
from domain.notification import NotificationChannel
from domain.notification_rule import EventCondition, PropertyMatch, PropertyOperator


@pytest.mark.anyio
async def test_route__event_matches_simple_rule__returns_intent():
    """Test that an event matching a simple property condition returns the correct intent."""
    # Arrange
    mock_event_repo = AsyncMock()

    notification = Notification()
    notification.type = "payment_failed"
    notification.channel = NotificationChannel.EMAIL
    notification.private = False

    rule = NotificationRule(
        notification_type="payment_failed",
        event_type="payment_processing",
        event_conditions=[
            EventCondition(
                property_match=PropertyMatch(
                    property_xpath="properties.status",
                    value="failed",
                    operator=PropertyOperator.EQ,
                ),
                event_proximity=None,
                event_logic=None,
            )
        ],
        delay=None,
        recheck=False,
    )

    relay = NotificationRulesRelay(
        event_repo=mock_event_repo,
        notification_rules=[rule],
        notifications=[notification],
    )

    event = Event()
    event.id = uuid4()
    event.user_id = "user_123"
    event.type = "payment_processing"
    event.event_timestamp = datetime.now(UTC)
    event.event_date = event.event_timestamp.date()
    event.properties = {"status": "failed", "amount": 100}
    event.user_traits = {"email": "test@example.com"}

    # Act
    intents = await relay.route(event)

    # Assert
    assert len(intents) == 1
    assert intents[0].notification_type == "payment_failed"
    assert intents[0].delay is None
