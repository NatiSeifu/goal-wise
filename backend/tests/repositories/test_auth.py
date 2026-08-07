from datetime import timedelta

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.types import utc_now
from app.repositories.auth import (
    clear_failed_login_attempts,
    count_recent_failed_login_attempts,
    create_session,
    create_user,
    get_active_session_by_token_hash,
    get_session_by_token_hash,
    get_user_by_normalized_email,
    record_failed_login_attempt,
    revoke_session,
)
from sqlalchemy import Engine
from sqlalchemy.orm import Session


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def db_session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        yield session


def test_create_and_get_user_by_normalized_email(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    db_session.commit()

    found_user = get_user_by_normalized_email(
        db_session,
        email_normalized="nati@example.com",
    )

    assert found_user == user
    assert found_user is not None
    assert found_user.password_hash == "argon2-hash"


def test_get_user_by_normalized_email_returns_none_for_missing_user(
    db_session: Session,
) -> None:
    assert get_user_by_normalized_email(db_session, email_normalized="missing@example.com") is None


def test_create_session_stores_hash_fields_only(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="session-owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    now = utc_now()

    user_session = create_session(
        db_session,
        user_id=user.id,
        session_token_hash="session-token-hash",
        csrf_token_hash="csrf-token-hash",
        issued_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(hours=1),
    )
    db_session.commit()

    found_session = get_session_by_token_hash(
        db_session,
        session_token_hash="session-token-hash",
    )

    assert found_session == user_session
    assert found_session is not None
    assert found_session.user_id == user.id
    assert found_session.csrf_token_hash == "csrf-token-hash"
    assert "session_token" not in found_session.__table__.columns
    assert "csrf_token" not in found_session.__table__.columns


def test_get_active_session_rejects_expired_sessions(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="expired@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    now = utc_now()
    create_session(
        db_session,
        user_id=user.id,
        session_token_hash="expired-token-hash",
        csrf_token_hash="csrf-token-hash",
        issued_at=now - timedelta(hours=2),
        last_seen_at=now - timedelta(hours=2),
        expires_at=now - timedelta(minutes=1),
    )
    db_session.commit()

    assert (
        get_active_session_by_token_hash(
            db_session,
            session_token_hash="expired-token-hash",
            now=now,
        )
        is None
    )


def test_get_active_session_rejects_revoked_sessions(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="revoked@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    now = utc_now()
    user_session = create_session(
        db_session,
        user_id=user.id,
        session_token_hash="revoked-token-hash",
        csrf_token_hash="csrf-token-hash",
        issued_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(hours=1),
    )
    revoke_session(db_session, user_session=user_session, revoked_at=now)
    db_session.commit()

    assert (
        get_active_session_by_token_hash(
            db_session,
            session_token_hash="revoked-token-hash",
            now=now,
        )
        is None
    )


def test_get_active_session_returns_unexpired_unrevoked_session(
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        email_normalized="active@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    now = utc_now()
    user_session = create_session(
        db_session,
        user_id=user.id,
        session_token_hash="active-token-hash",
        csrf_token_hash="csrf-token-hash",
        issued_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(hours=1),
    )
    db_session.commit()

    assert (
        get_active_session_by_token_hash(
            db_session,
            session_token_hash="active-token-hash",
            now=now,
        )
        == user_session
    )


def test_count_recent_failed_login_attempts_filters_by_email_source_and_window(
    db_session: Session,
) -> None:
    now = utc_now()
    record_failed_login_attempt(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=now - timedelta(minutes=1),
    )
    record_failed_login_attempt(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=now - timedelta(minutes=9),
    )
    record_failed_login_attempt(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=now - timedelta(minutes=11),
    )
    record_failed_login_attempt(
        db_session,
        email_normalized="other@example.com",
        source_hash="source-hash",
        failed_at=now - timedelta(minutes=1),
    )
    record_failed_login_attempt(
        db_session,
        email_normalized="nati@example.com",
        source_hash="other-source-hash",
        failed_at=now - timedelta(minutes=1),
    )
    db_session.commit()

    count = count_recent_failed_login_attempts(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
        since=now - timedelta(minutes=10),
    )

    assert count == 2


def test_clear_failed_login_attempts_removes_email_and_source_pair_only(
    db_session: Session,
) -> None:
    now = utc_now()
    record_failed_login_attempt(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=now,
    )
    record_failed_login_attempt(
        db_session,
        email_normalized="other@example.com",
        source_hash="source-hash",
        failed_at=now,
    )
    db_session.commit()

    removed_count = clear_failed_login_attempts(
        db_session,
        email_normalized="nati@example.com",
        source_hash="source-hash",
    )
    db_session.commit()

    assert removed_count == 1
    assert (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized="nati@example.com",
            source_hash="source-hash",
            since=now - timedelta(minutes=10),
        )
        == 0
    )
    assert (
        count_recent_failed_login_attempts(
            db_session,
            email_normalized="other@example.com",
            source_hash="source-hash",
            since=now - timedelta(minutes=10),
        )
        == 1
    )
