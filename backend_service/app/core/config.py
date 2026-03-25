from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "TheOrchestrator"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    AGENT_MODEL: str | None = None
    AGENT_REASONING_EFFORT: str | None = None
    AGENT_THINKING_LEVEL: str | None = None
    AGENT_INCLUDE_THOUGHTS: bool = False
    GOOGLE_API_KEY: str | None = None
    DDG_MCP_PATH: str | None = None

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:admin@localhost:5432/my_db"
    SQL_ECHO: bool = False

    # JWT Auth
    SECRET_KEY: str = "CHANGE-ME-TO-A-REAL-SECRET-KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
