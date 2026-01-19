from domain import Event
from infrastructure.taskiq.messages import events_received


def _event_to_dict(event: Event) -> dict:
    return {
        "id": str(event.id),
        "user_id": event.user_id,
        "type": event.type,
        "event_timestamp": event.event_timestamp.isoformat(),
        "event_date": event.event_date.isoformat(),
        "properties": event.properties,
        "user_traits": event.user_traits,
    }


class TaskiqEventQueue:
    async def events_received(self, events: list[Event]) -> None:
        events_as_dicts = [_event_to_dict(event) for event in events]
        await events_received.kiq(events_as_dicts)  # type: ignore # kiq signature suddenly does not play well with dishka injections
