from abc import ABC, abstractmethod


class UseCase[TRequest, TResponse](ABC):
    @abstractmethod
    async def handle(self, request: TRequest) -> TResponse:
        raise NotImplementedError
