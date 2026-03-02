from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # App metadata:
    APP_NAME: str = "AeroOps"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    ENV: str = "dev"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # security - JWT:
    JWT_SECRET_KEY: SecretStr  #! required
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: int = 30
    REFRESH_TOKEN_EXPIRE: int = 7

    # security - ARGON2:
    ARGON2__TYPE: str = "ID"
    ARGON2__TIME_COST: int = 3
    ARGON2__MEMORY_COST: int = 65536
    ARGON2__PARALLELISM: int = 4
    ARGON2__HASH_LEN: int = 32
    ARGON2__SALT_LEN: int = 16

    # infrastructure:
    DATABASE_URL: SecretStr  #! required
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6302
    REDIS_DB: int = 0

    # rate limiting
    BURST_WINDOW: int = 600
    BURST_LIMIT: int = 100
    SUSTAINED_WINDOW: int = 3600
    SUSTAINED_LIMIT: int = 300

    # Comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:5173"

    @computed_field @ property  # type: ignore[misc]
    def allowed_origins(self) -> list[str]:
        """Parses the CORS_ORIGINS string into a list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Used only on first startup to seed the initial admin
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: SecretStr  #! required

    model_config = SettingsConfigDict(
        env_file=str(env_path), env_file_encoding="utf-8", extra="ignore"
    )


# Instantiation
@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# Global settings instance
settings = get_settings()
