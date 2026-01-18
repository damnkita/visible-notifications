from collections.abc import Generator

import pytest
from dishka import Provider, Scope, provide
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.postgres import PostgresContainer

from infrastructure.database.sqlalchemy.engine import create_async_engine
from infrastructure.env_config import EnvConfig
from infrastructure.fastapi.main import create_api, get_dependencies_providers


@pytest.fixture(scope="package")
def client(
    async_db_engine: AsyncEngine,
    test_db_container: PostgresContainer,
) -> Generator[TestClient]:
    dependencies_providers = get_dependencies_providers()

    class MockDBEngineProvider(Provider):
        @provide(scope=Scope.APP)
        def get_mock_db_engine(self) -> AsyncEngine:
            return async_db_engine

    envconfig = EnvConfig()
    envconfig.database_url_async = PostgresDsn(
        test_db_container.get_connection_url(driver="asyncpg")
    )
    envconfig.database_url_sync = PostgresDsn(
        test_db_container.get_connection_url(driver="psycopg2")
    )

    # migrations dsn hack
    import os

    os.environ["DATABASE_URL_SYNC"] = test_db_container.get_connection_url(
        driver="psycopg2"
    )
    os.environ["DATABASE_URL_ASYNC"] = test_db_container.get_connection_url(
        driver="asyncpg"
    )

    test_providers = dependencies_providers + [MockDBEngineProvider()]

    app = create_api(envconfig, test_providers)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="package")
def test_db_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:17-alpine") as pgcont:
        yield pgcont


@pytest.fixture(scope="package")
def async_db_engine(test_db_container: PostgresContainer) -> AsyncEngine:
    host = test_db_container.get_connection_url(driver="asyncpg")
    engine = create_async_engine(host)
    return engine
