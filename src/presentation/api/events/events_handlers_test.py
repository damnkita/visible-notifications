from http import HTTPStatus

from fastapi.testclient import TestClient


def test_post_events__normal_payload__accepted(client: TestClient):
    response = client.post(
        "/api/v1/events",
        json=[
            {
                "user_id": "u_12345",
                "event_type": "signup_completed",
                "event_timestamp": "2025-10-31T19:00:00Z",
                "properties": {
                    "signup_method": "email",
                    "referral_source": "google_ads",
                    "device_type": "mobile",
                },
                "user_traits": {
                    "email": "maria@example.com",
                    "country": "PT",
                    "marketing_opt_in": True,
                    "risk_segment": "NEW",
                },
            },
            {
                "user_id": "u_12345",
                "event_type": "link_bank_success",
                "event_timestamp": "2025-10-31T19:10:45Z",
                "properties": {
                    "bank_name": "Santander",
                    "verification_method": "open_banking",
                    "account_type": "checking",
                },
                "user_traits": {
                    "email": "maria@example.com",
                    "country": "PT",
                    "marketing_opt_in": True,
                    "risk_segment": "LOW",
                },
            },
            {
                "user_id": "u_12345",
                "event_type": "payment_initiated",
                "event_timestamp": "2025-10-31T19:20:00Z",
                "properties": {
                    "amount": 1425.00,
                    "currency": "EUR",
                    "payment_method": "bank_transfer",
                    "recipient_id": "merch_998",
                },
                "user_traits": {
                    "email": "maria@example.com",
                    "country": "PT",
                    "marketing_opt_in": True,
                    "risk_segment": "MEDIUM",
                },
            },
            {
                "user_id": "u_12345",
                "event_type": "payment_failed",
                "event_timestamp": "2025-10-31T19:22:11Z",
                "properties": {
                    "amount": 1425.00,
                    "attempt_number": 2,
                    "failure_reason": "INSUFFICIENT_FUNDS",
                },
                "user_traits": {
                    "email": "maria@example.com",
                    "country": "PT",
                    "marketing_opt_in": True,
                    "risk_segment": "MEDIUM",
                },
            },
        ],
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()["accepted"] == 4


def test_post_events__empty_payload__accepted(client: TestClient):
    response = client.post("/api/v1/events", json=[])
    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()["accepted"] == 0


def test_post_events__partially_gibberish_payload__accepted_what_possible(
    client: TestClient,
):
    response = client.post(
        "/api/v1/events",
        json=[
            "asdfghjkl",
            {"foo": "bar", "baz": 12345},
            {
                "user_id": "u_12345",
                "event_type": "signup_completed",
                "event_timestamp": "2025-10-31T19:00:00Z",
                "properties": {
                    "signup_method": "email",
                    "referral_source": "google_ads",
                    "device_type": "mobile",
                },
                "user_traits": {
                    "email": "maria@example.com",
                    "country": "PT",
                    "marketing_opt_in": True,
                    "risk_segment": "NEW",
                },
            },
            {"xyzzy": [1, 2, 3], "plugh": None},
        ],
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()["accepted"] == 1


def test_post_events__totally_gibberish_payload__still_not_broken(client: TestClient):
    response = client.post(
        "/api/v1/events",
        json=[
            "asdfghjkl",
            {"foo": "bar", "baz": 12345},
            [1, 2, 3, "nonsense"],
            {"xyzzy": [1, 2, 3], "plugh": None},
            42,
            None,
        ],
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()["accepted"] == 0


def test_post_events__input_malformed__not_processed(client: TestClient):
    response = client.post(
        "/api/v1/events", json="hello I am completely, terribly malformed JSON, Sir"
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
