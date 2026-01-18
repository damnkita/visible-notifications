from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.health.exceptions import DependencyNotReadyException


class PostgresDBChecker:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def check(self):
        try:
            await self.session.execute(text("SELECT CURRENT_TIME"))
        except Exception as e:
            raise DependencyNotReadyException("postgres+asyncpg") from e
