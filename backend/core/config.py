from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2-style config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # ignore any other env vars we don't explicitly define
    )

    # Basic app configs
    APP_NAME: str = "TestHub"
    APP_VERSION: str = "0.1.0"

    # SQLite for now
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./testhub.db"

    # JWT config
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # IMPORTANT: this must exist
    GEMINI_API_KEY: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
