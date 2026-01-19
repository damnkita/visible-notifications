from datetime import datetime
from http import HTTPStatus

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from pydantic import BaseModel

from app.audit import GetUserAuditRequest, GetUserAuditUseCase

router = APIRouter()


class EventAuditDTO(BaseModel):
    event_id: str
    event_type: str
    event_timestamp: datetime
    properties: dict


class NotificationAuditDTO(BaseModel):
    notification_type: str
    trigger_event: str
    status: str
    created_at: datetime
    suppression_reason: str | None


class UserAuditResponse(BaseModel):
    user_id: str
    recent_events: list[EventAuditDTO]
    notification_history: list[NotificationAuditDTO]


@router.get("/audit/{user_id}", status_code=HTTPStatus.OK)
@inject
async def get_user_audit(
    user_id: str,
    get_user_audit_usecase: FromDishka[GetUserAuditUseCase],
    limit: int = 50,
) -> UserAuditResponse:
    result = await get_user_audit_usecase.handle(
        GetUserAuditRequest(user_id=user_id, limit=limit)
    )

    return UserAuditResponse(
        user_id=result.user_id,
        recent_events=[
            EventAuditDTO(
                event_id=event.event_id,
                event_type=event.event_type,
                event_timestamp=event.event_timestamp,
                properties=event.properties,
            )
            for event in result.recent_events
        ],
        notification_history=[
            NotificationAuditDTO(
                notification_type=notif.notification_type,
                trigger_event=notif.trigger_event,
                status=notif.status,
                created_at=notif.created_at,
                suppression_reason=notif.suppression_reason,
            )
            for notif in result.notification_history
        ],
    )
