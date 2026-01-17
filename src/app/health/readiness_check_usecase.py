from dataclasses import dataclass
from typing import Protocol

from app.usecase import UseCase


class DatabaseChecker(Protocol):
    async def check(self): ...


class ReadyChecker:
    def __init__(self, db_checker: DatabaseChecker) -> None:
        self.db_checker = db_checker

    async def check(self):
        await self.db_checker.check()


@dataclass
class ReadinessResponse:
    reason: str | None


class ReadinessCheckUseCase(UseCase[None, ReadinessResponse]):
    def __init__(self, ready_checker: ReadyChecker) -> None:
        super().__init__()
        self.ready_checker = ready_checker

    async def handle(self, request: None) -> ReadinessResponse:
        await self.ready_checker.check()

        return ReadinessResponse(reason=None)
