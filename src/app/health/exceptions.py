from app.exceptions import InternalApplicationException


class DependencyNotReadyException(InternalApplicationException):
    def __init__(self, dependency_name: str) -> None:
        super().__init__(
            "dependency_not_ready", f"Dependency not ready: {dependency_name}"
        )
        self.dependency_name = dependency_name
