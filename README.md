# Event-Driven Notification System

A fintech notification platform that triggers smart notifications based on user events and conditions.

## Quick Start

### Send Events to the API

Use these curl examples to post events to the API:

```bash
# 1. User Signup - Triggers WELCOME_EMAIL if marketing_opt_in is true
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"u_12345","event_type":"signup_completed","event_timestamp":"2025-10-31T19:00:00Z","properties":{"signup_method":"email","referral_source":"google_ads","device_type":"mobile"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"NEW"}}]'

# 2. Bank Link Success - Triggers BANK_LINK_NUDGE_SMS if within 24h of signup
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"u_12345","event_type":"link_bank_success","event_timestamp":"2025-10-31T19:10:45Z","properties":{"bank_name":"Santander","verification_method":"open_banking","account_type":"checking"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"LOW"}}]'

# 3. Payment Initiated
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"u_12345","event_type":"payment_initiated","event_timestamp":"2025-10-31T19:20:00Z","properties":{"amount":1425.00,"currency":"EUR","payment_method":"bank_transfer","recipient_id":"merch_998"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"MEDIUM"}}]'

# 4. Payment Failed - Triggers INSUFFICIENT_FUNDS_EMAIL and HIGH_RISK_ALERT (if attempts >= 3)
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"u_12345","event_type":"payment_failed","event_timestamp":"2025-10-31T19:22:11Z","properties":{"amount":1425.00,"attempt_number":2,"failure_reason":"INSUFFICIENT_FUNDS"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"MEDIUM"}}]'

# Send multiple events in one request
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '[{"user_id":"u_12345","event_type":"signup_completed","event_timestamp":"2025-10-31T19:00:00Z","properties":{"signup_method":"email","referral_source":"google_ads","device_type":"mobile"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"NEW"}},{"user_id":"u_12345","event_type":"link_bank_success","event_timestamp":"2025-10-31T19:10:45Z","properties":{"bank_name":"Santander","verification_method":"open_banking","account_type":"checking"},"user_traits":{"email":"maria@example.com","country":"PT","marketing_opt_in":true,"risk_segment":"LOW"}}]'
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
- **Event sourcing** pattern for all user actions
- **Rule-based notification engine** with debouncing and proximity conditions
- **Async processing** with Taskiq background workers
- **PostgreSQL** for event storage and notification history

## Development

```bash
# Run the API
make run-api

# Run background workers
make run-workers

# Run tests
pytest
```
