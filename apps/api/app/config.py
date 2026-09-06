"""Environment-driven application settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/is_it_local"
    llm_base_url: str = "http://localhost:8080/v1"
    llm_model: str = "local-model"
    searxng_base_url: str = "http://localhost:8888"
    provider_rate_limit_per_min: int = 60

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, value: str) -> str:
        # SQLAlchemy needs an explicit driver; map the plain scheme to psycopg v3.
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


settings = Settings()
