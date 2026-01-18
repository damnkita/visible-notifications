import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

from infrastructure.settings import settings


def update_head():
    config_path = Path(__file__).parent / "alembic.ini"
    alembic_cfg = Config(str(config_path))
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database_url_async))
    command.upgrade(alembic_cfg, "head")
