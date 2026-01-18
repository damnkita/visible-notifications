from sqlalchemy.ext.asyncio import AsyncSession

from domain import Event


class SQLAEventRepository:
    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    async def save_all(self, events: list[Event]) -> int:
        self.async_session.add_all(events)
        await self.async_session.flush()
        return len(events)
