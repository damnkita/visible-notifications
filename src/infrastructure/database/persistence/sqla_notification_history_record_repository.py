from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain import NotificationHistoryRecord


class SQLANotificationHistoryRecordRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def save(self, record: NotificationHistoryRecord) -> None:
        self.async_session.add(record)
        await self.async_session.flush()

    async def count_by_user_and_type_within_time(
        self,
        user_id: str,
        notification_type: str,
        timerange: timedelta,
    ) -> int:
        threshold = datetime.now(UTC) - timerange

        stmt = select(func.count()).where(
            NotificationHistoryRecord.user_id == user_id,
            NotificationHistoryRecord.type == notification_type,
            NotificationHistoryRecord.created_at >= threshold,
        )

        result = await self.async_session.execute(stmt)
        return result.scalar() or 0

    async def find_recent_by_user(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[NotificationHistoryRecord]:
        stmt = (
            select(NotificationHistoryRecord)
            .where(NotificationHistoryRecord.user_id == user_id)
            .order_by(NotificationHistoryRecord.created_at.desc())
            .limit(limit)
        )

        result = await self.async_session.execute(stmt)
        return list(result.scalars().all())
