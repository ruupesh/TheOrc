from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    APP_NAME: str = "TheOrchestrator"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    AGENT_MODEL: str | None = None
    GOOGLE_API_KEY: str | None = None
    DDG_MCP_PATH: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
