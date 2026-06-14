from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str


@lru_cache
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()  # pyright: ignore[reportCallIssue]


db_settings = get_db_settings()
