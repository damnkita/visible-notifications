from enum import Enum

from dishka import Provider, Scope, provide
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Env(str, Enum):
    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    TEST = "test"


class EnvConfig(BaseSettings):
    env: Env = Field(default=Env.PROD)
    database_url_sync: PostgresDsn = PostgresDsn(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
    )
    database_url_async: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> EnvConfig:
        return EnvConfig()
