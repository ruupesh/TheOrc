from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "TheOrchestrator"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    AGENT_MODEL: str | None = None
    AGENT_REASONING_EFFORT: str = "low"
    AGENT_THINKING_LEVEL: str = "low"
    AGENT_INCLUDE_THOUGHTS: bool = False
    GOOGLE_API_KEY: str | None = None
    DDG_MCP_PATH: str | None = None

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
