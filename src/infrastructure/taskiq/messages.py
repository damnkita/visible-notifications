from dishka import FromDishka
from dishka.integrations.taskiq import inject

from app.logging import Logger
from infrastructure.taskiq.broker import broker


@broker.task
@inject
async def events_received(
    events: list[dict],
    logger: FromDishka[Logger],
) -> None:
    logger.info("Events received for processing", count=len(events))
    for event in events:
        logger.debug(
            "Processing event",
            event_type=event.get("type"),
            user_id=event.get("user_id"),
        )
