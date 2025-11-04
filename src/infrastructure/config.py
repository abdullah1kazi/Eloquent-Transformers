"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Application
    app_name: str = "Eloquent Transformers"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: list[str] = Field(default=["http://localhost:3000"])

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/eloquent_transformers",
        validation_alias="DATABASE_URL",
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    redis_ttl: int = 3600  # 1 hour

    # Storage
    storage_path: str = Field(default="./storage/audio", validation_alias="STORAGE_PATH")
    max_upload_size: int = 100 * 1024 * 1024  # 100MB

    # ML Models
    whisper_model: str = Field(default="base", validation_alias="WHISPER_MODEL")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL"
    )
    device: str = "cpu"  # or "cuda"

    # Vector Database
    chroma_persist_dir: str = Field(
        default="./storage/chroma", validation_alias="CHROMA_PERSIST_DIR"
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", validation_alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", validation_alias="CELERY_RESULT_BACKEND"
    )

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production", validation_alias="SECRET_KEY"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100

    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"

    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
