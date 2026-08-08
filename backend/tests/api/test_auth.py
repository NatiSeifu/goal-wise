from collections.abc import Generator

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from app.models import UserSession
from app.services.tokens import hash_session_token
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

TEST_SESSION_SECRET = "test-session-secret"


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    session_factory = make_session_factory(engine)

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as db_session:
            yield db_session

    def override_settings() -> Settings:
        return Settings(environment="test", session_secret=TEST_SESSION_SECRET)

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_openapi_loads(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200


def test_register_creates_user_sets_cookie_and_returns_csrf(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "  Nati@Example.COM ",
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["item"]["user"]["email"] == "nati@example.com"
    assert body["item"]["user"]["time_zone"] == "America/Los_Angeles"
    assert body["item"]["csrf_token"]
    assert "goalwise_session=" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


def test_register_session_cookie_uses_expected_local_flags(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nati@example.com",
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )

    cookie = response.headers["set-cookie"]

    assert response.status_code == 201
    assert "goalwise_session=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert "Secure" not in cookie


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "nati@example.com",
        "password": "correct horse battery staple",
        "time_zone": "America/Los_Angeles",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post("/api/v1/auth/register", json={**payload, "email": "NATI@example.com"})

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "email_conflict",
            "message": "Email is already registered.",
        },
    }


def test_register_validation_errors_use_error_envelope(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "short",
            "time_zone": "America/Los_Angeles",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "email" in response.json()["error"]["fields"]
    assert "password" in response.json()["error"]["fields"]


def test_login_succeeds_and_invalid_credentials_are_generic(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nati@example.com",
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )
    assert register_response.status_code == 201

    invalid_response = client.post(
        "/api/v1/auth/login",
        json={"email": "nati@example.com", "password": "wrong password"},
    )
    assert invalid_response.status_code == 401
    assert invalid_response.json() == {
        "error": {
            "code": "invalid_credentials",
            "message": "Invalid email or password.",
        },
    }

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "NATI@example.com", "password": "correct horse battery staple"},
    )

    assert response.status_code == 200
    assert response.json()["item"]["user"]["email"] == "nati@example.com"
    assert response.json()["item"]["csrf_token"]
    assert "HttpOnly" in response.headers["set-cookie"]


def test_login_rate_limiting_returns_generic_429_for_missing_user(client: TestClient) -> None:
    payload = {"email": "missing@example.com", "password": "wrong password"}
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 429
    assert response.json() == {
        "error": {
            "code": "rate_limited",
            "message": "Too many login attempts. Try again later.",
        },
    }


def test_login_rate_limiting_returns_same_429_for_existing_user(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nati@example.com",
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )
    assert register_response.status_code == 201

    payload = {"email": "nati@example.com", "password": "wrong password"}
    for _ in range(5):
        response = client.post("/api/v1/auth/login", json=payload)
        assert response.status_code == 401

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 429
    assert response.json() == {
        "error": {
            "code": "rate_limited",
            "message": "Too many login attempts. Try again later.",
        },
    }


def test_api_login_stores_only_session_and_csrf_hashes(
    client: TestClient,
    engine: Engine,
) -> None:
    response = _register_and_login(client)
    session_token = client.cookies.get(SESSION_COOKIE_NAME)
    csrf_token = response.json()["item"]["csrf_token"]

    assert session_token is not None
    with Session(engine) as db_session:
        user_sessions = list(db_session.scalars(select(UserSession)))

    assert user_sessions
    assert all(
        session_token not in user_session.session_token_hash for user_session in user_sessions
    )
    assert all(csrf_token not in user_session.csrf_token_hash for user_session in user_sessions)
    assert hash_session_token(session_token, TEST_SESSION_SECRET) in {
        user_session.session_token_hash for user_session in user_sessions
    }


def test_me_returns_user_and_fresh_csrf_token(client: TestClient) -> None:
    login_response = _register_and_login(client)
    login_csrf = login_response.json()["item"]["csrf_token"]

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["item"]["user"]["email"] == "nati@example.com"
    assert response.json()["item"]["csrf_token"]
    assert response.json()["item"]["csrf_token"] != login_csrf


def test_me_rejects_missing_session(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Authentication required.",
        },
    }


def test_me_rejects_invalid_session_cookie(client: TestClient) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, "not-a-valid-session-token")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Authentication required.",
        },
    }


def test_logout_requires_csrf_and_clears_session_cookie(client: TestClient) -> None:
    login_response = _register_and_login(client)
    csrf_token = login_response.json()["item"]["csrf_token"]

    missing_csrf_response = client.post("/api/v1/auth/logout")
    assert missing_csrf_response.status_code == 403
    assert missing_csrf_response.json() == {
        "error": {
            "code": "csrf_failed",
            "message": "Invalid request token.",
        },
    }

    logout_response = client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token})

    assert logout_response.status_code == 204
    assert "goalwise_session=" in logout_response.headers["set-cookie"]

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 401


def test_logout_rejects_invalid_csrf(client: TestClient) -> None:
    _register_and_login(client)

    response = client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": "invalid-csrf"})

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "csrf_failed",
            "message": "Invalid request token.",
        },
    }


def _register_and_login(client: TestClient) -> object:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nati@example.com",
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )
    assert register_response.status_code == 201
    return client.post(
        "/api/v1/auth/login",
        json={"email": "nati@example.com", "password": "correct horse battery staple"},
    )
