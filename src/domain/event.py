from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from domain.base import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (Index("ix__user_id__event_date", "user_id", "event_date"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_date: Mapped[date] = mapped_column(Date, primary_key=True)
    properties: Mapped[dict] = mapped_column(JSON)
    user_traits: Mapped[dict] = mapped_column(JSON)
