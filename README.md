# Event-Driven Notification System

A fintech notification platform that triggers smart notifications based on user events and conditions.

## Quick Start

### 1. Start the Platform

```bash
docker compose build
docker compose up -d
```

This spins up:

| Service        | URL                                 | Description                              |
| -------------- | ----------------------------------- | ---------------------------------------- |
| **API**        | http://localhost:8000               | Receives events                          |
| **Liveness**   | http://localhost:8000/healthz/live  | Health check                             |
| **Readiness**  | http://localhost:8000/healthz/ready | Dependency check                         |
| **Worker**     | -                                   | Processes events, triggers notifications |
| **PostgreSQL** | localhost:5432                      | Stores events and notification history   |
| **Redis**      | localhost:6379                      | Message queue for async processing       |

### 2. Open Audit Endpoint

Open http://localhost:8000/audit/u_12345 in your browser to watch notifications in real-time.

### 3. Send Events, Observe Audit Updates

> **Hint:** Trigger each call several times to see debouncing (suppression) in action.

#### Single Events

```bash
# User Signup - Triggers WELCOME_EMAIL if marketing_opt_in is true
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{
    "user_id": "u_12345",
    "event_type": "signup_completed",
    "event_timestamp": "2025-10-31T19:00:00Z",
    "properties": {"signup_method": "email"},
    "user_traits": {"email": "maria@example.com", "marketing_opt_in": true}
  }]'

# Bank Link Success - Triggers BANK_LINK_NUDGE_SMS if within 24h of signup
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{
    "user_id": "u_12345",
    "event_type": "link_bank_success",
    "event_timestamp": "2025-10-31T19:10:45Z",
    "properties": {"bank_name": "Santander"},
    "user_traits": {"email": "maria@example.com"}
  }]'

# Payment Failed - Triggers INSUFFICIENT_FUNDS_EMAIL (max 1 per calendar day)
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{
    "user_id": "u_12345",
    "event_type": "payment_failed",
    "event_timestamp": "2025-10-31T19:30:00Z",
    "properties": {"amount": 1425.00, "attempt_number": 1, "failure_reason": "INSUFFICIENT_FUNDS"},
    "user_traits": {"email": "maria@example.com"}
  }]'

# Payment with 3+ attempts - Triggers HIGH_RISK_ALERT (internal)
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{
    "user_id": "u_12345",
    "event_type": "payment_failed",
    "event_timestamp": "2025-10-31T19:30:00Z",
    "properties": {"amount": 1425.00, "attempt_number": 3, "failure_reason": "INSUFFICIENT_FUNDS"},
    "user_traits": {"email": "maria@example.com"}
  }]'
```

#### Batch Events

```bash
# Send multiple events at once
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[
    {"user_id": "u_12345", "event_type": "signup_completed", "event_timestamp": "2025-10-31T19:00:00Z", "properties": {}, "user_traits": {"marketing_opt_in": true}},
    {"user_id": "u_12345", "event_type": "link_bank_success", "event_timestamp": "2025-10-31T19:10:45Z", "properties": {"bank_name": "Santander"}, "user_traits": {}}
  ]'
```

#### Mixed Valid/Invalid Events

Invalid events are silently skipped (logged server-side). Only valid events are processed:

```bash
# 2 valid events, 2 invalid (missing fields) - returns accepted: 2
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[
    {"user_id": "u_12345", "event_type": "signup_completed", "event_timestamp": "2025-10-31T19:00:00Z", "properties": {}, "user_traits": {}},
    {"user_id": "u_12345"},
    {"event_type": "orphan_event"},
    {"user_id": "u_12345", "event_type": "payment_failed", "event_timestamp": "2025-10-31T19:30:00Z", "properties": {"failure_reason": "INSUFFICIENT_FUNDS"}, "user_traits": {}}
  ]'
```

#### Empty Events

```bash
# Empty array - returns accepted: 0
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[]'
```

### 4. Check the Final Audit Trail

See what happened for a user - events received and notifications sent/suppressed:

- http://localhost:8000/audit/u_12345

Example response:

```json
{
  "user_id": "u_12345",
  "recent_events": [
    {
      "event_id": "abc-123",
      "event_type": "payment_failed",
      "event_timestamp": "2025-10-31T19:22:11Z",
      "properties": {
        "failure_reason": "INSUFFICIENT_FUNDS",
        "attempt_number": 2
      }
    }
  ],
  "notification_history": [
    {
      "notification_type": "INSUFFICIENT_FUNDS_EMAIL",
      "trigger_event": "payment_failed",
      "status": "sent",
      "created_at": "2025-10-31T19:22:12Z",
      "suppression_reason": null
    },
    {
      "notification_type": "INSUFFICIENT_FUNDS_EMAIL",
      "trigger_event": "payment_failed",
      "status": "suppressed",
      "created_at": "2025-10-31T20:15:00Z",
      "suppression_reason": "skipped INSUFFICIENT_FUNDS_EMAIL: already sent today"
    }
  ]
}
```

## Configuration Files

The system uses YAML files in the `src/` directory for configuration:

- **`src/notifications.yaml`** - Defines notification templates (email/SMS content)
- **`src/notification_rules.yml`** - Defines rules that trigger notifications based on events

These files are loaded at startup. Any changes require a restart.

## Notification Rules

Current rules:

1. **WELCOME_EMAIL** - Sent when user signs up with marketing consent
2. **BANK_LINK_NUDGE_SMS** - Sent when bank account is linked within 24h of signup
3. **INSUFFICIENT_FUNDS_EMAIL** - Sent on payment failure (max once per day)
4. **HIGH_RISK_ALERT** - Internal alert when payment fails 3+ times

Please see notification_rules.yml file to understand the syntax (there's a hint).

## Architecture

- **Domain-Driven Design** with clean architecture layers
- **TDD**
- **SQLAlchemy DBAL**
- **Rule-based notification engine** with debouncing and proximity conditions
- **Async processing** with Taskiq background workers
- **PostgreSQL** for event storage and notification history

## Assumptions

- Moderately high load (~1k rps)
- Notification rules changed via code modification for now (admin UI could be added in future)
- The configuration must be easily modifiable
  - Also flexible! That's why there are additional rule properties, such as delay, recheck, event_logic or property operators for the xpath search (some.path could be EQ, NEQ, GTE, LTE (etc) than a property's value)
- When the event amout becomes really unimaginable, we can introduce partitioning or OLAP DB, but until then it's fine

## Trade Offs

- No event batching (could have helped resources at high RPS)
- No performance tests
- No observability, telemetry
- Redis as a queue backend (better to use a real queue with a persistent guaranteed "exactly once" delivery)
- No real message delivery, inherently no retries logic and "technical failure" status of a notification
- A few NotImplementedException, due to the lack of time
