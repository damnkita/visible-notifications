from taskiq_redis import ListQueueBroker

from infrastructure.env_config import EnvConfig

settings = EnvConfig()

broker = ListQueueBroker(url=str(settings.redis_url))
