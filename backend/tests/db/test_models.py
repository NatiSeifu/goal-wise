from datetime import UTC, timedelta
from uuid import UUID

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.types import utc_now
from app.models import LoginAttempt, User, UserSession
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as db_session:
        yield db_session


def test_metadata_registers_auth_tables() -> None:
    assert "users" in Base.metadata.tables
    assert "sessions" in Base.metadata.tables
    assert "login_attempts" in Base.metadata.tables


def test_user_and_session_round_trip(session: Session) -> None:
    user = User(
        email_normalized="nati@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    user_session = UserSession(
        user_id=user.id,
        session_token_hash="session-token-hash",
        csrf_token_hash="csrf-token-hash",
        expires_at=utc_now() + timedelta(days=7),
    )
    session.add(user_session)
    session.commit()

    session.refresh(user)
    session.refresh(user_session)

    assert UUID(user.id).version == 4
    assert UUID(user_session.id).version == 4
    assert user_session.user_id == user.id
    assert user_session.user == user
    assert user.created_at.tzinfo is UTC
    assert user_session.expires_at.tzinfo is UTC


def test_user_email_is_unique(session: Session) -> None:
    session.add(
        User(
            email_normalized="same@example.com",
            password_hash="first",
            time_zone="America/Los_Angeles",
        )
    )
    session.commit()

    session.add(
        User(
            email_normalized="same@example.com",
            password_hash="second",
            time_zone="America/Los_Angeles",
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_token_hash_is_unique(session: Session) -> None:
    user = User(
        email_normalized="session-owner@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    expires_at = utc_now() + timedelta(days=7)
    session.add_all(
        [
            UserSession(
                user_id=user.id,
                session_token_hash="same-token-hash",
                csrf_token_hash="csrf-token-hash-1",
                expires_at=expires_at,
            ),
            UserSession(
                user_id=user.id,
                session_token_hash="same-token-hash",
                csrf_token_hash="csrf-token-hash-2",
                expires_at=expires_at,
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_model_does_not_store_raw_tokens() -> None:
    column_names = set(UserSession.__table__.columns.keys())

    assert "session_token" not in column_names
    assert "csrf_token" not in column_names
    assert "session_token_hash" in column_names
    assert "csrf_token_hash" in column_names


def test_login_attempt_round_trip(session: Session) -> None:
    login_attempt = LoginAttempt(
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=utc_now(),
    )
    session.add(login_attempt)
    session.commit()
    session.refresh(login_attempt)

    assert login_attempt.id
    assert login_attempt.source_hash == "source-hash"
