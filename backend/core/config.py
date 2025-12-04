from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic app configs
    APP_NAME: str = "TestHub"
    APP_VERSION: str = "0.1.0"

    # SQLite for now (file-based DB)
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./testhub.db"

    # JWT config (we'll use this soon)
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
