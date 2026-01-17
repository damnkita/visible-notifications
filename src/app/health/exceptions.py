from http import HTTPStatus

from app.exceptions import WebApplicationException


class DependencyNotReadyException(WebApplicationException):
    def __init__(self, dependency_name: str) -> None:
        super().__init__(
            "E_DEPENDENCY_NOT_READY",
            f"Dependency not ready: {dependency_name}",
            HTTPStatus.SERVICE_UNAVAILABLE,
        )
        self.dependency_name = dependency_name
