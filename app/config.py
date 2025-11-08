
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # LLM
    LLM_PROVIDER: str = "deepseek"
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    DEEPSEEK_API_KEY: str | None = None  # do not commit

    # Server
    CORS_ORIGINS: str = "http://localhost:3000"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Webhook security
    WEBHOOK_SHARED_SECRET: str | None = None

    # Observability
    LOG_JSON: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None

    # Adapters
    SLACK_BOT_TOKEN: str | None = None

    # Clockify
    CLOCKIFY_API_KEY: str | None = None
    CLOCKIFY_ADDON_TOKEN: str | None = None
    CLOCKIFY_BASE_URL: str = "https://api.clockify.me/api"

settings = Settings()
