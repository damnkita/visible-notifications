from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain import Event


class SQLAEventRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def save_all(self, events: list[Event]) -> int:
        self.async_session.add_all(events)
        await self.async_session.flush()
        return len(events)

    async def find_for_user_within_time(
        self,
        event_type: str,
        user_id: str,
        timerange: timedelta,
    ) -> list[Event]:
        threshold_datetime = datetime.now(UTC) - timerange
        threshold_date = threshold_datetime.date()

        stmt = (
            select(Event)
            .where(
                Event.event_date >= threshold_date,
                Event.type == event_type,
                Event.user_id == user_id,
                Event.event_timestamp >= threshold_datetime,
            )
            .order_by(Event.event_timestamp.desc())
        )

        result = await self.async_session.execute(stmt)
        return list(result.scalars().all())
