from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Base


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


class NotificationHistoryRecord(Base):
    __tablename__ = "notifications_history_records"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    trigger: Mapped[str] = mapped_column(String)
    user_id: Mapped[str] = mapped_column(String)
    status: Mapped[NotificationStatus] = mapped_column(String)
    retries: Mapped[int] = mapped_column(Integer)
    suppressed_because: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
