from datetime import date, datetime
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from app.logging import Logger
from app.notifications.trigger_notifications_use_case import (
    TriggerNotificationsUseCase,
)
from domain import Event
from infrastructure.taskiq.broker import broker


def _dict_to_event(data: dict) -> Event:
    event = Event()
    event.id = UUID(data["id"])
    event.user_id = data["user_id"]
    event.type = data["type"]
    event.event_timestamp = datetime.fromisoformat(data["event_timestamp"])
    event.event_date = date.fromisoformat(data["event_date"])
    event.properties = data["properties"]
    event.user_traits = data["user_traits"]
    return event


@broker.task
@inject
async def events_received(
    events: list[dict],
    logger: FromDishka[Logger],
    trigger_notifications_usecase: FromDishka[TriggerNotificationsUseCase],
) -> None:
    logger.info("Events received for processing", count=len(events))

    for idx, event_dict in enumerate(events):
        logger.debug(
            "Converting event from dict",
            event_index=idx,
            event_id=event_dict.get("id"),
        )

        event = _dict_to_event(event_dict)

        logger.debug(
            "Processing event",
            event_id=str(event.id),
            event_type=event.type,
            user_id=event.user_id,
            properties_count=len(event.properties),
        )

        try:
            response = await trigger_notifications_usecase.handle(event)

            if response.intents:
                logger.info(
                    "Notification intents triggered",
                    event_id=str(event.id),
                    event_type=event.type,
                    user_id=event.user_id,
                    intents=[intent.notification_type for intent in response.intents],
                    intent_count=len(response.intents),
                )
            else:
                logger.debug(
                    "No notification intents triggered",
                    event_id=str(event.id),
                    event_type=event.type,
                    user_id=event.user_id,
                )
        except Exception as e:
            logger.error(
                "Failed to process event for notifications",
                event_id=str(event.id),
                event_type=event.type,
                user_id=event.user_id,
                error=str(e),
            )
            raise

    logger.info("Events processing completed", processed_count=len(events))
