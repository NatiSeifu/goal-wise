import pytest
from app.core.config import LOCAL_DEV_SESSION_SECRET, Settings, get_settings
from pydantic import ValidationError


def test_settings_load_local_defaults() -> None:
    settings = Settings(
        environment="local",
        database_url="sqlite+pysqlite:///./goalwise.db",
        session_secret=LOCAL_DEV_SESSION_SECRET,
        secure_cookies=False,
        cookie_samesite="lax",
        allowed_frontend_origin="http://localhost:5173",
        _env_file=None,
    )

    assert settings.environment == "local"
    assert settings.database_url == "sqlite+pysqlite:///./goalwise.db"
    assert settings.session_secret.get_secret_value() == LOCAL_DEV_SESSION_SECRET
    assert settings.secure_cookies is False
    assert settings.cookie_samesite == "lax"
    assert settings.allowed_frontend_origin == "http://localhost:5173"


def test_ai_summary_defaults_to_disabled_and_explicit_request() -> None:
    settings = Settings(_env_file=None)

    assert settings.ai_summary_enabled is False
    assert settings.ai_summary_trigger == "request"
    assert settings.ai_summary_provider == "groq"
    assert settings.ai_summary_model == "openai/gpt-oss-120b"
    assert settings.groq_api_key is None
    assert settings.ai_summary_prompt_version == "ai-explanation-prompt-v3"
    assert settings.ai_summary_response_schema_version == "ai-explanation-v1"
    assert settings.ai_summary_timeout_seconds == 4.0


def test_ai_summary_settings_can_be_enabled_by_server_configuration() -> None:
    settings = Settings(
        ai_summary_enabled=True,
        ai_summary_trigger="automatic",
        ai_summary_provider="groq",
        ai_summary_model="test-model",
        groq_api_key="test-key",
        _env_file=None,
    )

    assert settings.ai_summary_enabled is True
    assert settings.ai_summary_trigger == "automatic"
    assert settings.ai_summary_provider == "groq"
    assert settings.ai_summary_model == "test-model"
    assert settings.groq_api_key is not None
    assert settings.groq_api_key.get_secret_value() == "test-key"


def test_ai_summary_timeout_cannot_exceed_four_seconds() -> None:
    with pytest.raises(ValidationError, match="AI_SUMMARY_TIMEOUT_SECONDS"):
        Settings(ai_summary_timeout_seconds=5.0, _env_file=None)


def test_pytest_runtime_settings_ignore_local_env_file() -> None:
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.environment == "test"
    assert settings.database_url == "sqlite+pysqlite:///:memory:"


def test_settings_accept_explicit_hosted_database_url() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://example",
        session_secret="secret",
        _env_file=None,
    )

    assert settings.database_url == "postgresql+psycopg://example"


def test_settings_normalize_bare_postgres_database_url() -> None:
    settings = Settings(
        database_url="postgresql://example",
        session_secret="secret",
        _env_file=None,
    )

    assert settings.database_url == "postgresql+psycopg://example"


def test_production_rejects_default_session_secret() -> None:
    with pytest.raises(ValidationError, match="SESSION_SECRET"):
        Settings(
            environment="production",
            session_secret=LOCAL_DEV_SESSION_SECRET,
            secure_cookies=True,
            _env_file=None,
        )


def test_production_requires_secure_cookies() -> None:
    with pytest.raises(ValidationError, match="SECURE_COOKIES"):
        Settings(
            environment="production",
            session_secret="configured-secret",
            _env_file=None,
        )
