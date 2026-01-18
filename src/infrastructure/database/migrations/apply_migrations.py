from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.health.exceptions import DependencyNotReadyException
from infrastructure.env_config import EnvConfig


def update_head(settings: EnvConfig):
    sync_dsn = settings.database_url_sync
    if not sync_dsn:
        raise ValueError("Datbase DSN misconfigured at times of migrations")
    engine = create_engine(str(sync_dsn))
    connection = engine.connect()
    stmt = text("SELECT CURRENT_TIME")
    row = connection.execute(stmt).fetchone()
    if not row or len(str(row[0])) < 2:
        raise DependencyNotReadyException("database")

    config_path = Path(__file__).parent / "alembic.ini"
    alembic_cfg = Config(str(config_path))
    alembic_cfg.set_main_option("sqlalchemy.url", str(sync_dsn))
    command.upgrade(alembic_cfg, "head")
