from pydantic import Field
from pydantic_settings import BaseSettings

from infrastructure.fastapi.main import Mode, create_api

if __name__ == "__main__":
    import uvicorn

    class APISettings(BaseSettings):
        mode: Mode = Field(default=Mode.PROD)

    settings = APISettings()

    uvicorn.run(
        app=create_api(settings.mode),
        port=8000,
        reload=False,
        loop="uvloop",
    )
