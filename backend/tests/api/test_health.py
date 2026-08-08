from collections.abc import Generator

import pytest
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


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

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_is_public_and_does_not_require_database_override() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "goalwise-api",
        "status": "ok",
        "checks": {},
    }


def test_ready_checks_database(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "service": "goalwise-api",
        "status": "ready",
        "checks": {"database": "ok"},
    }


def test_ready_returns_unavailable_when_database_check_fails() -> None:
    class BrokenSession:
        def execute(self, _statement: object) -> None:
            raise SQLAlchemyError("database unavailable")

    def override_db_session() -> Generator[BrokenSession, None, None]:
        yield BrokenSession()

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as client:
        response = client.get("/ready")
    app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "service": "goalwise-api",
        "status": "unavailable",
        "checks": {"database": "unavailable"},
    }
