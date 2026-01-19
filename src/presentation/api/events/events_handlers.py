import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any
from uuid import uuid4

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from pydantic import BaseModel

from app.events import SaveEventsRequest, SaveEventsUseCase
from domain import Event

logger = logging.getLogger(__name__)

router = APIRouter()


class EventDTO(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: datetime
    properties: dict[str, Any]
    user_traits: dict[str, Any]

    def to_domain(self) -> Event:
        return Event(
            id=uuid4(),
            user_id=self.user_id,
            type=self.event_type,
            event_timestamp=self.event_timestamp,
            event_date=self.event_timestamp.date(),
            properties=self.properties,
            user_traits=self.user_traits,
        )


class PostEventsResponse(BaseModel):
    accepted: int


@router.post("/api/v1/events", status_code=HTTPStatus.ACCEPTED)
@inject
async def post(
    events: list[EventDTO | Any],
    save_events: FromDishka[SaveEventsUseCase],
) -> PostEventsResponse:
    domain_events: list[Event] = []
    for event in events:
        try:
            dto = EventDTO.model_validate(event)
            domain_events.append(dto.to_domain())
        except ValueError as e:
            logger.warning("Event validation failed", extra={"event": event, "error": str(e)})
            continue

    result = await save_events.handle(SaveEventsRequest(events=domain_events))
    return PostEventsResponse(accepted=result.saved_count)
