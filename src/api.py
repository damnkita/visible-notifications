from pydantic import Field
from pydantic_settings import BaseSettings

from infrastructure.fastapi.main import Env, create_api


class APISettings(BaseSettings):
    env: Env = Field(default=Env.PROD)


settings = APISettings()
print(settings.model_dump_json())

app = create_api(settings.env)
