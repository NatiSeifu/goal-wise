"""Environment-driven backend settings."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "test", "staging", "production"]
SameSitePolicy = Literal["lax", "strict", "none"]
AiSummaryTrigger = Literal["request", "automatic"]

LOCAL_DEV_SESSION_SECRET = "local-dev-session-secret-change-me"


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: EnvironmentName = "local"
    database_url: str = "sqlite+pysqlite:///./goalwise.db"
    session_secret: SecretStr = SecretStr(LOCAL_DEV_SESSION_SECRET)
    secure_cookies: bool = False
    cookie_samesite: SameSitePolicy = "lax"
    allowed_frontend_origin: str = "http://localhost:5173"
    ai_summary_enabled: bool = False
    ai_summary_trigger: AiSummaryTrigger = "request"
    ai_summary_provider: str | None = None
    ai_summary_model: str | None = None
    ai_summary_prompt_version: str = "ai-explanation-prompt-v1"
    ai_summary_response_schema_version: str = "ai-explanation-v1"
    ai_summary_timeout_seconds: float = 4.0

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("ai_summary_timeout_seconds")
    @classmethod
    def require_ai_summary_timeout(cls, value: float) -> float:
        if value != 4.0:
            raise ValueError("AI_SUMMARY_TIMEOUT_SECONDS must be 4 seconds")
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def require_secure_production_settings(self) -> Self:
        if not self.is_production:
            return self

        if self.session_secret.get_secret_value() == LOCAL_DEV_SESSION_SECRET:
            raise ValueError("SESSION_SECRET must be configured in production")

        if not self.secure_cookies:
            raise ValueError("SECURE_COOKIES must be enabled in production")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
