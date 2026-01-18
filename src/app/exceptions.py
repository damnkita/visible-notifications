from http import HTTPStatus


class ApplicationException(Exception):
    """
    Any exception produced by the application
    """

    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__()


class InternalApplicationException(ApplicationException):
    """
    Application exceptions that are not meant to be public
    """

    pass


class WebApplicationException(ApplicationException):
    """
    Application exceptions that could have a web representation
    """

    def __init__(self, code: str, reason: str, status: HTTPStatus) -> None:
        self.status = status
        super().__init__(code, reason)
