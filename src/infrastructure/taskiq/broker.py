from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqEvents
from taskiq_redis import RedisStreamBroker

from infrastructure.env_config import EnvConfig
from infrastructure.logging import configure_logging

settings = EnvConfig()

broker = RedisStreamBroker(url=str(settings.redis_url))


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_container(_state) -> None:
    configure_logging(settings.env, service_name="visible-notify-worker")

    from infrastructure import dependencies_providers

    container = make_async_container(*dependencies_providers)
    setup_dishka(container, broker)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def close_container(_state) -> None:
    if broker.state.dishka_container:
        await broker.state.dishka_container.close()
