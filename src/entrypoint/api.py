from infrastructure.env_config import EnvConfig
from infrastructure.fastapi.main import create_api, get_dependencies_providers

dependences_providers = get_dependencies_providers()

# meant to run with fastapi run etc
app = create_api(EnvConfig(), dependences_providers)
