from infrastructure.taskiq.broker import broker


@broker.task
async def events_received(events: list[dict]) -> None:
    # TODO: Implement actual event processing logic
    print(f"Received {len(events)} events for processing")
    for event in events:
        print(f"  - {event.get('event_type')} for user {event.get('user_id')}")
