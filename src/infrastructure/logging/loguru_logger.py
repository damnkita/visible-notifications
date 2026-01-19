import sys
from typing import Any

from loguru import logger

from infrastructure.env_config import Env


def configure_logging(env: Env, service_name: str = "visible-notify") -> None:
    logger.remove()

    is_local = env in (Env.LOCAL)

    if is_local:
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level> | "
                "{extra}"
            ),
            level="DEBUG",
            colorize=True,
        )
    else:
        logger.add(
            sys.stdout,
            format="{message}",
            level="DEBUG" if env == Env.TEST else "INFO",
            serialize=True,
        )

    logger.configure(
        extra={
            "env": env.value,
            "service": service_name,
        }
    )


class LoguruLogger:
    def debug(self, message: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).debug(message)

    def info(self, message: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).info(message)

    def warning(self, message: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).warning(message)

    def error(self, message: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).error(message)

    def exception(self, message: str, **kwargs: Any) -> None:
        logger.bind(**kwargs).exception(message)
