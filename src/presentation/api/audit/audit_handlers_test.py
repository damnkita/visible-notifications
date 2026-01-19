from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_audit__user_with_events_and_notifications__returns_audit_data(
    client: TestClient,
):
    # First, post some events to create data
    client.post(
        "/api/v1/events",
        json=[
            {
                "user_id": "u_audit_test",
                "event_type": "signup_completed",
                "event_timestamp": "2025-10-31T19:00:00Z",
                "properties": {"signup_method": "email"},
                "user_traits": {"email": "test@example.com", "marketing_opt_in": True},
            },
        ],
    )

    # Then, get the audit for the user
    response = client.get("/audit/u_audit_test")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["user_id"] == "u_audit_test"
    assert "recent_events" in data
    assert "notification_history" in data

    # Check that we have the event we posted
    assert len(data["recent_events"]) >= 1
    event_types = [e["event_type"] for e in data["recent_events"]]
    assert "signup_completed" in event_types


def test_get_audit__user_with_no_events__returns_empty_lists(client: TestClient):
    response = client.get("/audit/u_nonexistent_user_12345")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["user_id"] == "u_nonexistent_user_12345"
    assert data["recent_events"] == []
    assert data["notification_history"] == []


def test_get_audit__with_limit_parameter__respects_limit(client: TestClient):
    # Post multiple events
    client.post(
        "/api/v1/events",
        json=[
            {
                "user_id": "u_limit_test",
                "event_type": "signup_completed",
                "event_timestamp": "2025-10-31T19:00:00Z",
                "properties": {},
                "user_traits": {},
            },
            {
                "user_id": "u_limit_test",
                "event_type": "payment_initiated",
                "event_timestamp": "2025-10-31T19:01:00Z",
                "properties": {},
                "user_traits": {},
            },
            {
                "user_id": "u_limit_test",
                "event_type": "payment_failed",
                "event_timestamp": "2025-10-31T19:02:00Z",
                "properties": {"failure_reason": "OTHER", "attempt_number": 1},
                "user_traits": {},
            },
        ],
    )

    response = client.get("/audit/u_limit_test?limit=2")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert len(data["recent_events"]) <= 2


def test_get_audit__returns_events_in_correct_format(client: TestClient):
    # Post events with various properties
    client.post(
        "/api/v1/events",
        json=[
            {
                "user_id": "u_format_test",
                "event_type": "payment_failed",
                "event_timestamp": "2025-10-31T19:00:00Z",
                "properties": {
                    "failure_reason": "INSUFFICIENT_FUNDS",
                    "attempt_number": 1,
                    "amount": 100.0,
                },
                "user_traits": {"email": "test@example.com"},
            },
        ],
    )

    response = client.get("/audit/u_format_test")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["user_id"] == "u_format_test"
    assert len(data["recent_events"]) >= 1

    # Check event structure
    event = data["recent_events"][0]
    assert "event_id" in event
    assert "event_type" in event
    assert "event_timestamp" in event
    assert "properties" in event
    assert event["event_type"] == "payment_failed"
    assert event["properties"]["failure_reason"] == "INSUFFICIENT_FUNDS"

    # notification_history might be empty if worker isn't running
    # but the structure should still be correct
    assert isinstance(data["notification_history"], list)
