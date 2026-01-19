from infrastructure import dependencies_providers
from infrastructure.env_config import EnvConfig
from infrastructure.fastapi.main import create_api

# meant to run with fastapi run etc
app = create_api(EnvConfig(), dependencies_providers)
