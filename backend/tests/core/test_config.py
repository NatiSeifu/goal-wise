import pytest
from app.core.config import LOCAL_DEV_SESSION_SECRET, Settings
from pydantic import ValidationError


def test_settings_load_local_defaults() -> None:
    settings = Settings()

    assert settings.environment == "local"
    assert settings.database_url == "sqlite+pysqlite:///./goalwise.db"
    assert settings.session_secret.get_secret_value() == LOCAL_DEV_SESSION_SECRET
    assert settings.secure_cookies is False
    assert settings.cookie_samesite == "lax"


def test_settings_accept_explicit_hosted_database_url() -> None:
    settings = Settings(database_url="postgresql+psycopg://example", session_secret="secret")

    assert settings.database_url == "postgresql+psycopg://example"


def test_settings_normalize_bare_postgres_database_url() -> None:
    settings = Settings(database_url="postgresql://example", session_secret="secret")

    assert settings.database_url == "postgresql+psycopg://example"


def test_production_rejects_default_session_secret() -> None:
    with pytest.raises(ValidationError, match="SESSION_SECRET"):
        Settings(environment="production", secure_cookies=True)


def test_production_requires_secure_cookies() -> None:
    with pytest.raises(ValidationError, match="SECURE_COOKIES"):
        Settings(environment="production", session_secret="configured-secret")
