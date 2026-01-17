import decimal
import uuid
from uuid import UUID

from sqlmodel import Field, SQLModel


class Pipka(SQLModel):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    size: decimal.Decimal = decimal.Decimal(0)
