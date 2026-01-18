from enum import Enum
from uuid import UUID

from sqlmodel import AutoString, Field, SQLModel


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


class Notification(SQLModel, table=True):
    id: UUID = Field(default=None, primary_key=True)
    type: str
    trigger: str
    user_id: str
    status: NotificationStatus = Field(sa_type=AutoString)
    retries: int
    suppressed_because: str | None
