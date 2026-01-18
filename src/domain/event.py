from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    id: UUID = Field(default=None, primary_key=True)
    user_id: str
    type: str
    event_timestamp: datetime
    event_date: date
    properties: dict = Field(sa_type=JSON)
    user_traits: dict = Field(sa_type=JSON)
