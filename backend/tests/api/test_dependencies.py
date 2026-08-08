from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.api.dependencies import CsrfSessionDep, CurrentSessionDep
from app.api.errors import ApiError
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import api_error_handler
from app.models import UserSession
from app.services.auth import login_user, register_user
from app.services.tokens import hash_session_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

TEST_SESSION_SECRET = "test-session-secret"


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return make_session_factory(engine)


@pytest.fixture
def protected_client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    app = FastAPI()
    app.add_exception_handler(ApiError, api_error_handler)

    @app.get("/protected")
    def protected(current_session: CurrentSessionDep) -> dict[str, str]:
        return {"user_id": current_session.user.id}

    @app.post("/protected")
    def protected_unsafe(current_session: CsrfSessionDep) -> dict[str, str]:
        return {"user_id": current_session.user.id}

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as db_session:
            yield db_session

    def override_settings() -> Settings:
        return Settings(environment="test", session_secret=TEST_SESSION_SECRET)

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    with TestClient(app) as test_client:
        yield test_client


def test_current_session_dependency_rejects_missing_cookie(protected_client: TestClient) -> None:
    response = protected_client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Authentication required.",
        },
    }


def test_current_session_dependency_exposes_authenticated_user(
    protected_client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    session_token, _csrf_token = _create_login(session_factory)
    protected_client.cookies.set(SESSION_COOKIE_NAME, session_token)

    response = protected_client.get("/protected")

    assert response.status_code == 200
    assert response.json()["user_id"]


def test_current_session_dependency_persists_last_seen_for_authenticated_get(
    protected_client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    session_token, _csrf_token = _create_login(session_factory)
    last_seen_before = _last_seen_at(session_factory, session_token)
    protected_client.cookies.set(SESSION_COOKIE_NAME, session_token)

    response = protected_client.get("/protected")

    assert response.status_code == 200
    assert _last_seen_at(session_factory, session_token) > last_seen_before


def test_csrf_dependency_rejects_missing_header(
    protected_client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    session_token, _csrf_token = _create_login(session_factory)
    last_seen_before = _last_seen_at(session_factory, session_token)
    protected_client.cookies.set(SESSION_COOKIE_NAME, session_token)

    response = protected_client.post("/protected")

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "csrf_failed",
            "message": "Invalid request token.",
        },
    }
    assert _last_seen_at(session_factory, session_token) > last_seen_before


def test_csrf_dependency_accepts_matching_header(
    protected_client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    session_token, csrf_token = _create_login(session_factory)
    protected_client.cookies.set(SESSION_COOKIE_NAME, session_token)

    response = protected_client.post("/protected", headers={"X-CSRF-Token": csrf_token})

    assert response.status_code == 200
    assert response.json()["user_id"]


def _create_login(
    session_factory: sessionmaker[Session],
) -> tuple[str, str]:
    with session_factory() as db_session:
        now = datetime.now(UTC)
        register_user(
            db_session,
            email="nati@example.com",
            password="correct horse battery staple",
            time_zone="America/Los_Angeles",
        )
        login_result = login_user(
            db_session,
            email="nati@example.com",
            password="correct horse battery staple",
            source_identifier="203.0.113.10",
            session_secret=TEST_SESSION_SECRET,
            now=now,
        )
        db_session.commit()
        return login_result.session_token, login_result.csrf_token


def _last_seen_at(
    session_factory: sessionmaker[Session],
    session_token: str,
) -> datetime:
    with session_factory() as db_session:
        user_session = db_session.scalar(
            select(UserSession).where(
                UserSession.session_token_hash
                == hash_session_token(session_token, TEST_SESSION_SECRET),
            ),
        )
        assert user_session is not None
        return user_session.last_seen_at
