from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


async def create_async_session(engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
